# basic import
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
import sys
from use_paint_preview_with_mac import *


# instantiate an MCP server client
mcp = FastMCP("Calculator")

# DEFINE TOOLS


# addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Given two numbers, return the sum of the two numbers

    Args:
        a (int): First number
        b (int): Second number

    Returns:
        int: The sum of the given two numbers
    """
    print("CALLED: add(a: int, b: int) -> int:")
    return int(a + b)


@mcp.tool()
def can_I_listify_a_number(a: int) -> str:
    """Given a number, check if it can be further listified

    Args:
        a (int): A natural number

    Returns:
        str: A message indicating if the number can be listified or not and the reason why
    """
    print("CALLED: can_listify_a_number(a: int) -> bool:")
    if a > 9:
        return f"{a} can be converted into a list of digits since there are more than 1 digits in the number"
    else:
        return f"{a} cannot be converted into a list of digits since only the unit's place is filled"


# tool to convert a number into a list of it's digits
@mcp.tool()
def listify_number(a: int) -> list[int]:
    """Given a number, convert it to a list of its digits

    Args:
        a (int): A natural number

    Returns:
        list[int]: A list of the digits of the given number.
    """
    print("CALLED: listify_number(a: int) -> list[int]:")
    digits = []
    while a > 0:
        digits.append(a % 10)
        a = a // 10
    digits = digits[::-1]
    return digits


# tool to add numbers in a list
@mcp.tool()
def summify_list(a: list) -> int:
    """Given a list of natural numbers, sum the numbers and return the result

    Args:
        a (list[int]): A list of natural numbers

    Returns:
        int: The sum of the given list of numbers
    """
    print("CALLED: summify_list(a:list[int]) -> int")
    sum_of_elements = a[0]
    for i in range(1, len(a)):
        sum_of_elements = add(sum_of_elements, a[i])
    return sum_of_elements


# subtraction tool
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Given two numbers, return the difference of the two numbers (second deducted from the first)

    Args:
        a (int): First number
        b (int): Second number

    Returns:
        int: Subtract the second number from the first and return the result
    """
    print("CALLED: subtract(a: int, b: int) -> int:")
    return int(a - b)


# check integer equality
@mcp.tool()
def check_integer_equality(a: int, b: int) -> str:
    """Given two numbers, compare if the two numbers are equal or not

    Args:
        a (int): First number
        b (int): Second number

    Returns:
        str: A message indicating if the two numbers are equal or not
    """
    print("CALLED: check_integer_equality(a: int, b: int) -> bool:")
    if int(a) == int(b):
        return f"{int(a)} and {int(b)} are exactly the same"
    else:
        return f"{int(a)} and {int(b)} are not the same"


@mcp.tool()
async def add_text_in_paint(text: str) -> dict:
    """Given a text, take that text, create a new image, open it in mac preview, create a rectangle on the image and add the text to the rectangle

    Args:
        text (str): Text to add to the image

    Returns:
        dict: A message indicating if the text was added succesully or not and a helpful error message if it wasn't added successfully
    """
    try:
        open_paint_with_text_mac(text)
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Text:'{text}' added successfully to the paint application",
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Could not add the text to paint application. Error: {str(e)}.",
                )
            ]
        }


# DEFINE RESOURCES


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    print("CALLED: get_greeting(name: str) -> str:")
    return f"Hello, {name}!"


# DEFINE AVAILABLE PROMPTS
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"
    print("CALLED: review_code(code: str) -> str:")


@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]


if __name__ == "__main__":
    # Check if running with mcp dev command
    print("STARTING")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution
