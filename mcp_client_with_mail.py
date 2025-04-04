import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
import google.generativeai as genai
from concurrent.futures import TimeoutError

# Load environment variables from .env file
load_dotenv()

# Use colors to make the logs more readable
COLORS = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "reset": "\033[0m",
    "bold": "\033[1m",
    "underline": "\033[4m",
    "italic": "\033[3m",
}

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_API_KEY")
model = genai.configure(api_key=api_key)
model = genai.GenerativeModel(os.getenv("MODEL_NAME"))


max_iterations = 10
last_response = None
iteration = 0
iteration_response = []


async def generate_with_timeout(prompt, timeout=10):
    """Generate content with a timeout"""
    print("Starting LLM generation...")
    try:
        # Pause for 3 seconds to avoid being rate limited by gemini-2.0-flash API
        await asyncio.sleep(3)
        # Convert the synchronous generate_content call to run in a thread
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda: model.generate_content(prompt),
            ),
            timeout=timeout,
        )
        print("LLM generation completed")
        return response
    except TimeoutError:
        print("LLM generation timed out!")
        raise
    except Exception as e:
        print(f"Error in LLM generation: {e}")
        raise


def reset_state():
    """Reset all global variables to their initial state"""
    global last_response, iteration, iteration_response
    last_response = None
    iteration = 0
    iteration_response = []


async def main():
    reset_state()  # Reset at the start of main
    print("Starting main execution...")
    try:
        # Create a single MCP server connection
        print("Establishing connection to MCP server...")
        server_params = StdioServerParameters(
            command="python", args=["mcp_server_with_mail.py"]
        )

        async with stdio_client(server_params) as (read, write):
            print("Connection established, creating session...")
            async with ClientSession(read, write) as session:
                print("Session created, initializing...")
                await session.initialize()

                # Get available tools
                print("Requesting tool list...")
                tools_result = await session.list_tools()
                tools = tools_result.tools
                print(f"Successfully retrieved {len(tools)} tools")

                # Create system prompt with available tools
                print("Creating system prompt...")
                print(f"Number of tools: {len(tools)}")

                try:
                    # First, let's inspect what a tool object looks like
                    # if tools:
                    #     print(f"First tool properties: {dir(tools[0])}")
                    #     print(f"First tool example: {tools[0]}")

                    tools_description = []
                    for i, tool in enumerate(tools):
                        try:
                            # Get tool properties
                            params = tool.inputSchema
                            desc = getattr(
                                tool, "description", "No description available"
                            )
                            name = getattr(tool, "name", f"tool_{i}")

                            # Format the input schema in a more readable way
                            if "properties" in params:
                                param_details = []
                                for param_name, param_info in params[
                                    "properties"
                                ].items():
                                    param_type = param_info.get("type", "unknown")
                                    param_details.append(f"{param_name}: {param_type}")
                                params_str = ", ".join(param_details)
                            else:
                                params_str = "no parameters"

                            tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                            tools_description.append(tool_desc)
                            print(f"Added description for tool: {tool_desc}")
                        except Exception as e:
                            print(f"Error processing tool {i}: {e}")
                            tools_description.append(f"{i+1}. Error processing tool")

                    tools_description = "\n".join(tools_description)
                    print("Successfully created tools description")
                except Exception as e:
                    print(f"Error creating tools description: {e}")
                    tools_description = "Error loading tools"

                print("Created system prompt...")

                system_prompt = f"""You are a math agent solving problems in iterations. You have access to various mathematical tools. Additionally, you also have access to a paint tool.

Available tools:
{tools_description}

You must respond with EXACTLY ONE line in one of these formats (no additional text):
1. For function calls:
   FUNCTION_CALL: function_name|param1|param2|...
   
2. For final answers:
   FINAL_ANSWER: [number]

Important:
- When a function returns multiple values, you need to process all of them
- Only give FINAL_ANSWER when you have completed all necessary calculations
- If you are asked to display the answer in a paint tool, you must first use the paint tool and do that before giving out the final answer.
- Do not repeat function calls with the same parameters
- Remember that when you are providing a list as an argument for a function call, you need to provide it in the format [1, 2, 3]. DO NOT FORGET to add the square brackets.

Examples:
- FUNCTION_CALL: add|5|3
- FUNCTION_CALL: strings_to_chars_to_int|INDIA
- FUNCTION_CALL: summify_list|[1, 2, 3]
- FINAL_ANSWER: [42]

DO NOT include any explanations or additional text. Be very careful with selection of function calls and repeat the calls only when necessary.
Your entire response should be a single line starting with either FUNCTION_CALL: or FINAL_ANSWER:"""

                query = """TASK:
                Given two positive integers A and B, you can only perform the following operation:
                Replace A with the sum of its digits
                i.e. if A = 123, then you can perform the operation 1 + 2 + 3 = 6
                Check if you can make A equal to B by performing the above operation any number of times. 
                
                If yes, then say "YES, A can be made equal to B by summing it's digits recursively" and if not then say "NO, A can never be made equal to B by summing it's digits recursively". Where A and B are to placeholders that you need to fill appropriately.

                Finally send the result (i.e. either of the above statements, whichever is applicable) in an email to the recipient nayakvinayak2408@gmail.com with the subject "Answer to your query"
                A is 132 and B is 6
                ---
                Meta-instructions:
                Make sure that you do not call the FINAL_ANSWER: statement before you have called the function to send the email. Once you have done that then you can say FINAL_ANSWER: statement where statement is the result of the email that you have sent.
                """
                print("Starting iteration loop...")

                # Use global iteration variables
                global iteration, last_response

                while iteration < max_iterations:
                    # Introduce a sleep to avoid being rate limited by gemini-2.0-flash API
                    # For free tier, we have a max of 15 requests per minute
                    await asyncio.sleep(3)
                    print(f"\n--- Iteration {iteration + 1} ---")
                    if last_response is None:
                        current_query = query
                    else:
                        current_query = (
                            current_query + "\n\n" + " ".join(iteration_response)
                        )
                        current_query = current_query + "  What should I do next?"

                    # Get model's response with timeout
                    print("Preparing to generate LLM response...")
                    prompt = f"{system_prompt}\n\nQuery: {current_query}"
                    try:
                        response = await generate_with_timeout(prompt)
                        response_text = response.text.strip()
                        print(
                            f"{COLORS['green']}{COLORS['bold']}LLM Response: {response_text}{COLORS['reset']}"
                        )

                        # Find the FUNCTION_CALL line in the response
                        for line in response_text.split("\n"):
                            line = line.strip()
                            if line.startswith("FUNCTION_CALL:"):
                                response_text = line
                                break

                    except Exception as e:
                        print(f"Failed to get LLM response: {e}")
                        break

                    if response_text.startswith("FUNCTION_CALL:"):
                        _, function_info = response_text.split(":", 1)
                        parts = [p.strip() for p in function_info.split("|")]
                        func_name, params = parts[0], parts[1:]

                        print(
                            f"\n{COLORS['yellow']}DEBUG: Raw function info: {function_info}{COLORS['reset']}"
                        )
                        print(
                            f"{COLORS['yellow']}DEBUG: Split parts: {parts}{COLORS['reset']}"
                        )
                        print(
                            f"{COLORS['yellow']}DEBUG: Function name: {func_name}{COLORS['reset']}"
                        )
                        print(
                            f"{COLORS['yellow']}{COLORS['bold']}DEBUG: Raw parameters: {params}{COLORS['reset']}"
                        )

                        try:
                            # Find the matching tool to get its input schema
                            tool = next((t for t in tools if t.name == func_name), None)
                            if not tool:
                                print(
                                    f"DEBUG: Available tools: {[t.name for t in tools]}"
                                )
                                raise ValueError(f"Unknown tool: {func_name}")

                            print(f"DEBUG: Found tool: {tool.name}")
                            print(f"DEBUG: Tool schema: {tool.inputSchema}")

                            # Prepare arguments according to the tool's input schema
                            arguments = {}
                            schema_properties = tool.inputSchema.get("properties", {})
                            print(f"DEBUG: Schema properties: {schema_properties}")

                            for param_name, param_info in schema_properties.items():
                                if not params:  # Check if we have enough parameters
                                    raise ValueError(
                                        f"Not enough parameters provided for {func_name}"
                                    )

                                value = params.pop(
                                    0
                                )  # Get and remove the first parameter
                                param_type = param_info.get("type", "string")

                                print(
                                    f"DEBUG: Converting parameter {param_name} with value {value} to type {param_type}"
                                )

                                # Convert the value to the correct type based on the schema
                                if param_type == "integer":
                                    arguments[param_name] = int(value)
                                elif param_type == "number":
                                    arguments[param_name] = float(value)
                                elif param_type == "array":
                                    # Handle array input
                                    if isinstance(value, str):
                                        value = value.strip("[]").split(",")
                                    arguments[param_name] = [
                                        int(x.strip()) for x in value
                                    ]
                                else:
                                    arguments[param_name] = str(value)

                            import code

                            code.interact(local=dict(globals(), **locals()))

                            print(
                                f"{COLORS['yellow']}DEBUG: Final arguments: {arguments}{COLORS['reset']}"
                            )
                            print(
                                f"{COLORS['yellow']}DEBUG: Calling tool {func_name}{COLORS['reset']}"
                            )

                            result = await session.call_tool(
                                func_name, arguments=arguments
                            )
                            print(f"DEBUG: Raw result: {result}")

                            # Get the full result content
                            if hasattr(result, "content"):
                                print(f"DEBUG: Result has content attribute")
                                # Handle multiple content items
                                if isinstance(result.content, list):
                                    iteration_result = [
                                        (
                                            item.text
                                            if hasattr(item, "text")
                                            else str(item)
                                        )
                                        for item in result.content
                                    ]
                                else:
                                    iteration_result = str(result.content)
                            else:
                                print(f"DEBUG: Result has no content attribute")
                                iteration_result = str(result)

                            print(
                                f"{COLORS['blue']}{COLORS['bold']}{COLORS['underline']}DEBUG: Final iteration result: {iteration_result}{COLORS['reset']}"
                            )

                            # Format the response based on result type
                            if isinstance(iteration_result, list):
                                result_str = f"[{', '.join(iteration_result)}]"
                            else:
                                result_str = str(iteration_result)

                            iteration_response.append(
                                f"In iteration {iteration + 1} you called {func_name} with {arguments} parameters, "
                                f"and the function returned {result_str}.\n"
                            )
                            last_response = iteration_result

                        except Exception as e:
                            print(f"DEBUG: Error details: {str(e)}")
                            print(f"DEBUG: Error type: {type(e)}")
                            import traceback

                            traceback.print_exc()
                            iteration_response.append(
                                f"Error in iteration {iteration + 1}: {str(e)}"
                            )
                            break

                    elif response_text.startswith("FINAL_ANSWER:"):
                        print(
                            f"\n{COLORS['yellow']}=== Agent Execution Complete ==={COLORS['reset']}"
                        )
                        break

                    iteration += 1

    except Exception as e:
        print(f"Error in main execution: {e}")
        import traceback

        traceback.print_exc()
    finally:
        reset_state()  # Reset at the end of main


if __name__ == "__main__":
    asyncio.run(main())
