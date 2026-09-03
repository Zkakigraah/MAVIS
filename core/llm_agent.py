import os
import json
from groq import Groq
from dotenv import load_dotenv
import core.tools as tools

load_dotenv()

class LLMAgent:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = "openai/gpt-oss-120b"
        self.system_prompt = """You are M.A.V.I.S. (Multi-purpose Automated Virtual Information System), a precision AI desktop assistant.

CORE DIRECTIVES:
1. Always respond in English.
2. Maintain a neutral, precise, and concise demeanor.
3. Keep spoken replies strictly under 2 sentences unless the user explicitly requests an extended explanation.
4. Execute tools immediately when a user request maps to an available function.

CRITICAL SYSTEM DISTINCTIONS:
- "Shut down system", "exit", "close yourself", "quit", "terminate MAVIS" refers to EXITING THE MAVIS APPLICATION. Use `control_system` with action `exit_mavis`.
- Only use `shutdown_pc` or `restart_pc` if the user explicitly mentions "computer", "PC", "machine", or "Windows" (e.g., "shut down my PC", "turn off the computer")."""

        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        self.should_exit = False
        
        self.available_functions = {
            "search_knowledge": tools.search_knowledge,
            "open_application": tools.open_application,
            "open_website": tools.open_website,
            "play_youtube": tools.play_youtube,
            "search_internet": tools.search_internet,
            "get_system_status": tools.get_system_status,
            "control_system": tools.control_system,
            "analyze_screen": tools.analyze_screen,
            "write_file": tools.write_file,
            "read_file": tools.read_file,
            "take_screenshot": tools.take_screenshot,
            "remember_information": tools.remember_information
        }

        self.tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge",
                    "description": "Query long-term semantic memory for personal user context, project specs, or previous facts.",
                    "parameters": {
                        "type": "object",
                        "properties": {"query": {"type": "string", "description": "The search query."}},
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "open_application",
                    "description": "Launch an application installed on the Windows system using the start menu search indexer.",
                    "parameters": {
                        "type": "object",
                        "properties": {"app_name": {"type": "string", "description": "Executable or application display name."}},
                        "required": ["app_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "open_website",
                    "description": "Open an arbitrary URL in the system default web browser.",
                    "parameters": {
                        "type": "object",
                        "properties": {"url": {"type": "string", "description": "Fully qualified target URL or domain."}},
                        "required": ["url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "play_youtube",
                    "description": "Search and launch video query results directly on YouTube.",
                    "parameters": {
                        "type": "object",
                        "properties": {"search_query": {"type": "string", "description": "The video search term."}},
                        "required": ["search_query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_internet",
                    "description": "Query DuckDuckGo for live web data, current news, weather, or real-time information.",
                    "parameters": {
                        "type": "object",
                        "properties": {"query": {"type": "string", "description": "Search engine query string."}},
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_system_status",
                    "description": "Read instantaneous hardware telemetry: CPU load, RAM usage, Battery level, Master Volume, and Brightness.",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "control_system",
                    "description": "Control system states, audio, display, or application lifecycle.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": [
                                    "exit_mavis",
                                    "lock_workstation",
                                    "shutdown_pc",
                                    "restart_pc",
                                    "volume_up",
                                    "volume_down",
                                    "set_volume",
                                    "mute",
                                    "unmute",
                                    "brightness_up",
                                    "brightness_down",
                                    "set_brightness"
                                ],
                                "description": "Action selector. Use 'exit_mavis' for closing MAVIS or shutting down system assistant. Use 'shutdown_pc' ONLY when the user explicitly requests shutting down the computer/PC."
                            },
                            "value": {
                                "type": "integer",
                                "description": "Integer target value (0-100) for set_volume or set_brightness actions."
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
                    "description": "Capture the active primary screen display and submit it to a multimodal vision model for real-time analysis.",
                    "parameters": {
                        "type": "object",
                        "properties": {"prompt": {"type": "string", "description": "Analytical question or prompt regarding screen contents."}},
                        "required": ["prompt"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Create and write plain-text content into an isolated sandboxed file in workspace/outputs.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string", "description": "Target file name (e.g. data.txt)."},
                            "content": {"type": "string", "description": "Complete text content to write."}
                        },
                        "required": ["filename", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read content from a file located in workspace/outputs.",
                    "parameters": {
                        "type": "object",
                        "properties": {"filename": {"type": "string", "description": "Name of the target file to read."}},
                        "required": ["filename"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "take_screenshot",
                    "description": "Capture the current desktop screen and store it directly in workspace/outputs.",
                    "parameters": {
                        "type": "object",
                        "properties": {"filename": {"type": "string", "description": "Optional destination file name."}}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "remember_information",
                    "description": "Commit user statements, preferences, credentials, or custom facts permanently to vector memory.",
                    "parameters": {
                        "type": "object",
                        "properties": {"fact": {"type": "string", "description": "The exact fact or preference to record."}},
                        "required": ["fact"]
                    }
                }
            }
        ]

    def chat(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        
        while True:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools_schema,
                tool_choice="auto",
                max_tokens=2048
            )
            
            response_message = response.choices[0].message
            
            if response_message.tool_calls:
                self.messages.append(response_message)
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_to_call = self.available_functions.get(function_name)
                    
                    if not function_to_call:
                        function_response = f"Execution rejected: Unknown tool '{function_name}'."
                    else:
                        try:
                            function_args = json.loads(tool_call.function.arguments)
                            if function_name == "control_system" and function_args.get("action") == "exit_mavis":
                                self.should_exit = True
                            function_response = function_to_call(**function_args)
                        except Exception as err:
                            function_response = f"Tool execution failed with error: {err}"
                            
                    self.messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response),
                    })
                
                # Constrain follow-up response to eliminate verbal delay
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    max_tokens=128
                )
                reply = final_response.choices[0].message.content
                self.messages.append({"role": "assistant", "content": reply})
                return reply
            else:
                reply = response_message.content
                self.messages.append({"role": "assistant", "content": reply})
                return reply