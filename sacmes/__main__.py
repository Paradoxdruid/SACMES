#!/usr/bin/env python3

import tkinter as tk
import tkinter.ttk as ttk
from config import cg


def main():
    """Initialize SACMES and open main window, runniong tkinter mainloop."""

    cg.root = tk.Tk()
    from main_window import MainWindow

    _ = MainWindow(cg.root)

    style = ttk.Style()
    style.configure(
        "On.TButton", foreground="blue", font=cg.LARGE_FONT, relief="raised", border=100
    )
    style.configure(
        "Off.TButton",
        foreground="black",
        font=cg.MEDIUM_FONT,
        relief="sunken",
        border=5,
    )

    while True:
        # --- initiate the mainloop ---#
        try:
            cg.root.mainloop()
        # --- escape scrolling error ---#
        except UnicodeDecodeError:
            pass


if __name__ == "__main__":
    main()
