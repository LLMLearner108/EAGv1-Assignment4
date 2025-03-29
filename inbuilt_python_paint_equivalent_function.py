import tkinter as tk
import time

def open_paint_with_text(text):
    root = tk.Tk()
    root.title("Paint App with Text")

    canvas_width, canvas_height = 500, 400
    root.geometry(f"{canvas_width}x{canvas_height}")

    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
    canvas.pack()

    rect_x1, rect_y1 = canvas_width // 4, canvas_height // 3
    rect_x2, rect_y2 = 3 * canvas_width // 4, 2 * canvas_height // 3
    
    time.sleep(3)
    print("Creating Rectangle")

    canvas.create_rectangle(
        rect_x1, rect_y1, rect_x2, rect_y2, fill="lightblue", outline="black"
    )

    time.sleep(3)
    print("Creating Text")

    canvas.create_text(
        (rect_x1 + rect_x2) // 2,
        (rect_y1 + rect_y2) // 2,
        text=text,
        font=("Arial", 14, "bold"),
        fill="black",
    )

    root.mainloop()


# Example usage
open_paint_with_text("Hello, World!")
