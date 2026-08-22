import os
import json
from groq import Groq
from core.config import GROQ_API_KEY
import core.tools as tools

if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
    raise ValueError("⚠️ LỖI: Chưa có GROQ_API_KEY. Vui lòng thiết lập trong file .env")

class JarvisAgent:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        
        self.system_instruction = """
        You are J.A.R.V.I.S, an advanced, highly intelligent virtual assistant operating on the user's local system.
        Your persona:
        1. Speak STRICTLY in English. 
        2. Be extremely polite, formal, and concise. Have a British-like butler demeanor. Call the user "Sir".
        3. CRITICAL: If the user asks about current events, real-time info, weather, or facts you do not know, use `search_internet`.
        4. CRITICAL: If the user asks about personal information, use `search_knowledge`.
        5. Absolutely DO NOT refuse requests to open apps, control system, or create files. ALWAYS use the provided tools.
        6. NEVER output Markdown bold (**text**) or special formatting symbols.
        7. Keep your answers brief and to the point.
        8. CRITICAL RULE: After executing ANY tool, you MUST synthesize the tool's output into a natural language response for the user. NEVER return an empty response.
        9. CRITICAL VISION CAPABILITY: You HAVE EYES! If the user says "look at my screen", "what do you see", "read the text on the screen", etc., you MUST IMMEDIATELY call the `analyze_screen` tool. NEVER say you are unable to view the screen.
        """
        
        self.messages = [
            {"role": "system", "content": self.system_instruction}
        ]
        
        self.tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": "open_application",
                    "description": "Open a specific application on the Windows operating system.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "app_name": {"type": "string"}
                        },
                        "required": ["app_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge",
                    "description": "Search local memory database for personal documents, past notes, or specific user data.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_internet",
                    "description": "Search the internet for real-time information or unknown facts.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_system_status",
                    "description": "Check the computer's current hardware status (CPU, RAM, Battery, and Volume).",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "control_system",
                    "description": "Control system functions like volume, brightness, media, or locking the screen.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string", 
                                "enum": ["mute", "volume_up", "volume_down", "play_pause", "lock_screen", "set_volume", "set_brightness", "brightness_up", "brightness_down"]
                            },
                            "volume_level": {"type": "integer"},
                            "brightness_level": {"type": "integer"}
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "take_screenshot",
                    "description": "Take a screenshot of the computer screen and save it to a file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string"}
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_screen",
                    "description": "Takes a screenshot of the user's current screen and analyzes it using a Vision AI model. Use this ONLY when the user explicitly asks you to 'look at my screen', 'read this code', 'explain this diagram', or asks questions about what is currently visible on their display.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The specific question or instruction for the Vision model (e.g., 'What code is on the screen?', 'Explain this diagram')."
                            }
                        },
                        "required": ["prompt"]
                    }
                }
            }
        ]
        
        # Bản đồ liên kết linh hoạt, không cần dùng IF/ELIF
        self.available_functions = {
            "read_file": tools.read_file,
            "write_file": tools.write_file,
            "search_knowledge": tools.search_knowledge,
            "open_application": tools.open_application,
            "search_internet": tools.search_internet,
            "get_system_status": tools.get_system_status,
            "control_system": tools.control_system,
            "take_screenshot": tools.take_screenshot,
            "analyze_screen": tools.analyze_screen
        }
        
        print("🧠 Đang khởi động não bộ J.A.R.V.I.S (Groq API)...")

    def ask(self, user_input: str) -> str:
        # Cắt tỉa lịch sử hội thoại nếu quá dài để tránh tràn Token
        if len(self.messages) > 15:
            self.messages = [self.messages[0]] + self.messages[-4:]

        self.messages.append({"role": "user", "content": user_input})
        
        try:
            response = self.client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=self.messages,
                tools=self.tools_schema,
                tool_choice="auto",
                max_tokens=1024,
                temperature=0.3
            )
            
            response_message = response.choices[0].message
            
            if response_message.tool_calls:
                assistant_msg = {
                    "role": "assistant",
                    "content": response_message.content,
                    "tool_calls": [
                        {
                            "id": tool.id,
                            "type": tool.type,
                            "function": {
                                "name": tool.function.name,
                                "arguments": tool.function.arguments
                            }
                        } for tool in response_message.tool_calls
                    ]
                }
                self.messages.append(assistant_msg)
                
                # Tự động thực thi Tool bằng Dictionary Mapping
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    if function_name in self.available_functions:
                        print(f"⚙️ Jarvis is executing: {function_name}({function_args})")
                        function_to_call = self.available_functions[function_name]
                        tool_result = function_to_call(**function_args)
                        
                        self.messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": str(tool_result),
                        })
                
                # Lần gọi thứ 2 để Tóm tắt lời nói (Bắt buộc chèn tools)
                final_response = self.client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=self.messages,
                    tools=self.tools_schema,
                    temperature=0.3
                )
                
                reply_message = final_response.choices[0].message
                reply_text = reply_message.content if reply_message.content else "I have completed the task, sir."
                
                self.messages.append({"role": "assistant", "content": reply_text})
                return reply_text
                
            else:
                reply_text = response_message.content
                self.messages.append({"role": "assistant", "content": reply_text})
                return reply_text
                
        except Exception as e:
            return f"System error encountered: {str(e)}"


jarvis = JarvisAgent()