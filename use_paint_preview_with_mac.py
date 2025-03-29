import pyautogui
import time
import subprocess
from PIL import Image


def open_paint_with_text_mac(text):
    # Step 1: Create a blank white image
    img = Image.new("RGB", (800, 600), "white")
    img_path = "/tmp/blank.png"  # Temporary file
    img.save(img_path)

    # Step 2: Open the image in Preview
    subprocess.run(["open", img_path])
    time.sleep(2)  # Wait for Preview to open

    # Step 3: Enter full-screen mode (Ctrl + Cmd + F)
    pyautogui.hotkey("ctrl", "command", "f")
    time.sleep(2)  # Wait for the transition to full screen

    # Step 4: Open the markup toolbar (CMD + Shift + A)
    pyautogui.hotkey("command", "shift", "a")
    time.sleep(1)

    # # Step 7: Open the markup pane
    # pyautogui.moveTo(736, 53)  # Move to toolbar area (adjust if needed)
    # pyautogui.click(button="left")  # Click the toolbar
    # time.sleep(0.5)

    # Step 5: Select the rectangle tool (Shift + R)
    pyautogui.moveTo(220, 95)
    pyautogui.click(button="left")
    time.sleep(0.5)

    pyautogui.moveTo(233, 159)
    pyautogui.click(button="left")
    time.sleep(0.5)

    # Step 8: Click the text tool from the toolbar
    pyautogui.moveTo(272, 95)  # Move to toolbar area (adjust if needed)
    pyautogui.click(button="left")  # Click the toolbar
    time.sleep(0.5)

    # Step 8: Click inside the rectangle to place text
    pyautogui.click(406, 419, button="left")
    time.sleep(0.5)

    # Step 9: Type the text
    pyautogui.typewrite(text, interval=0.1)

    print("Text added to Preview in full-screen mode!")


# Example usage
open_paint_with_text_mac("Hello, macOS!")
