import os
import json
import time
from groq import Groq
import core.tools as tools
from core.config import GROQ_API_KEY

class JarvisAgent:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        # Sử dụng mô hình xử lý văn bản linh hoạt và nhanh nhất (Đã cập nhật model mới 2026)
        self.model_name = "openai/gpt-oss-120b"
        
        self.system_instruction = """
        You are J.A.R.V.I.S., a highly advanced AI assistant. 
        CRITICAL RULES:
        1. Always respond STRICTLY in English. Never use other languages.
        2. Keep your answers concise, natural, and conversational (like a British butler).
        3. Do NOT use markdown formatting like *, #, or _, as it messes up the text-to-speech engine.
        4. You have access to tools. If a user asks a question about facts, news, or weather, USE the 'search_internet' tool.
        5. If a user asks about their personal info or documents, USE 'search_knowledge'.
        6. You can control the PC. USE 'control_system' for volume, brightness, or locking the screen.
        7. You can open applications. USE 'open_application' to launch requested apps.
        8. CRITICAL: After using ANY tool (like search_knowledge or search_internet), you MUST read the result and provide a spoken answer. Never return an empty response!
        9. CRITICAL: If the user asks you to "look at my screen", "what is on my screen", or "read this", you MUST use the 'analyze_screen' tool. Do not claim you lack vision capabilities!
        """
        
        self.chat_history = [
            {"role": "system", "content": self.system_instruction}
        ]
        
        self.tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": "search_internet",
                    "description": "Searches the internet for current events, weather, or facts not in your training data.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query."
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge",
                    "description": "Searches the local vector database for the user's personal information, notes, or saved documents.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to find in local memory."
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "open_application",
                    "description": "Opens a software application on the user's Windows computer.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "app_name": {
                                "type": "string",
                                "description": "The name of the application to open (e.g., 'Spotify', 'Chrome', 'Notepad')."
                            }
                        },
                        "required": ["app_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "open_website",
                    "description": "Opens a specific website URL in the user's default web browser.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL of the website to open (e.g., 'github.com', 'https://mail.google.com', 'netflix.com')."
                            }
                        },
                        "required": ["url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "play_youtube",
                    "description": "Searches for and opens a video or music on YouTube based on the user's request. Use this when the user asks to play music, a trailer, or a specific video.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query, song name, or video title to play on YouTube."
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_system_status",
                    "description": "Retrieves the current status of the computer's hardware, including CPU, RAM, Battery, and Audio Volume.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "control_system",
                    "description": "Controls the operating system. Can lock the screen, set volume, mute, or adjust brightness.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["lock_screen", "mute", "volume_up", "volume_down", "play_pause", "set_volume", "set_brightness", "brightness_up", "brightness_down"],
                                "description": "The action to perform."
                            },
                            "volume_level": {
                                "type": "integer",
                                "description": "The target volume level (0-100). Only used when action is set_volume."
                            },
                            "brightness_level": {
                                "type": "integer",
                                "description": "The target brightness level (0-100). Only used when action is set_brightness."
                            }
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_screen",
                    "description": "Takes a screenshot of the user's current screen and analyzes it using a Vision AI model. Use this ONLY when the user explicitly asks you to 'look at my screen' or analyze visual content.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The specific question or instruction for the Vision model (e.g., 'What code is on the screen?', 'Summarize this')."
                            }
                        },
                        "required": ["prompt"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "take_screenshot",
                    "description": "Takes a screenshot of the user's screen and saves it to the outputs directory. Does not analyze the image.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Reads the content of a specified text or code file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "The absolute or relative path to the file to read."
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Writes or overwrites content to a specified file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "The path to the file."
                            },
                            "content": {
                                "type": "string",
                                "description": "The content to write into the file."
                            }
                        },
                        "required": ["file_path", "content"]
                    }
                }
            }
        ]
        
        self.available_functions = {
            "search_knowledge": tools.search_knowledge,
            "open_application": tools.open_application,
            "open_website": tools.open_website,
            "play_youtube": tools.play_youtube,
            "search_internet": tools.search_internet,
            "get_system_status": tools.get_system_status,
            "control_system": tools.control_system,
            "analyze_screen": tools.analyze_screen,
            "take_screenshot": tools.take_screenshot,
            "read_file": tools.read_file,
            "write_file": tools.write_file
        }

    def ask(self, user_input: str) -> str:
        # Tự động dọn dẹp bộ nhớ nếu quá dài (Tránh lỗi giới hạn Token)
        if len(self.chat_history) > 15:
            self.chat_history = [self.chat_history[0]] + self.chat_history[-4:]

        self.chat_history.append({"role": "user", "content": user_input})

        try:
            # Lần gọi 1: AI suy nghĩ xem có cần dùng tool không
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.chat_history,
                tools=self.tools_schema,
                tool_choice="auto",
                max_tokens=2048 # Đã tăng từ 256 lên 2048 để tránh đứt gãy chuỗi JSON
            )
            
            response_message = response.choices[0].message
            
            # AI quyết định gọi Tool
            if response_message.tool_calls:
                self.chat_history.append(response_message)
                
                for tool_call in response_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    print(f"⚙️ Jarvis is executing: {tool_name}({tool_args})")
                    
                    if tool_name in self.available_functions:
                        tool_result = self.available_functions[tool_name](**tool_args)
                    else:
                        tool_result = f"Error: Tool {tool_name} not found."
                        
                    self.chat_history.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_name,
                        "content": str(tool_result)
                    })
                
                # Lần gọi 2: AI tổng hợp kết quả từ Tool và trả lời bằng giọng nói
                second_response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=self.chat_history,
                    tools=self.tools_schema, 
                    max_tokens=2048 # Đã tăng từ 256 lên 2048
                )
                
                final_answer = second_response.choices[0].message.content
                if not final_answer:
                    final_answer = "I have completed the task, sir."
                
                self.chat_history.append({"role": "assistant", "content": final_answer})
                return final_answer
            
            # AI trả lời bình thường không qua Tool
            else:
                answer = response_message.content
                self.chat_history.append({"role": "assistant", "content": answer})
                return answer

        except Exception as e:
            error_msg = f"System error encountered: {str(e)}"
            print(error_msg)
            return "I am sorry sir, I encountered a temporary network or cognitive error."

# Khởi tạo thực thể J.A.R.V.I.S toàn cục
jarvis = JarvisAgent()