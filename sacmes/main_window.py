#!/usr/bin/env python3

import tkinter as tk

from config import cg
import tkinter.ttk as ttk
from input_frame import InputFrame


###############################################
#   Graphical User Interface     #######
###############################################


#############################################
# Class that contains all of the frames ###
#############################################
class MainWindow(tk.Tk):

    # --- Initialize the GUI ---#
    def __init__(self, master=None, *args, **kwargs):

        # tk.Tk.__init__(self, *args, **kwargs)
        self.master = master
        self.master.wm_title("SACMES")

        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)

        # --- Create a frame for the UI ---#
        cg.container = tk.Frame(self.master, relief="flat", bd=5)
        cg.container.grid(
            row=0, rowspan=11, padx=10, sticky="nsew"
        )  # container object has UI frame in column 0
        cg.container.rowconfigure(
            0, weight=1
        )  # and PlotContainer (visualization) in column 1
        cg.container.columnconfigure(0, weight=1)

        # --- Raise the frame for initial UI ---#
        cg.ShowFrames = {}  # Key: frame handle / Value: tk.Frame object
        cg.input_frame = InputFrame(cg.container, self.master)  # was frame
        cg.ShowFrames[InputFrame] = cg.input_frame  # was frame
        cg.input_frame.grid(row=0, column=0, sticky="nsew")  # was frame
        self.show_frame(InputFrame)

        self._create_toolbar()

        # --- High and Low Frequency Dictionary ---#
        cg.HighLowList = {}

    # --- Function to visualize different frames ---#
    def _create_toolbar(self):

        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        #################
        # Edit Menu ###
        #################
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_separator()
        editmenu.add_command(
            label="Customize File Format",
            command=self.extraction_adjustment_frame,  # was lambda
        )
        self.delimiter_value = tk.IntVar()
        self.delimiter_value.set(1)

        self.extension_value = tk.IntVar()
        self.extension_value.set(1)

        self.byte_menu = tk.Menu(menubar)
        self.onethousand = self.byte_menu.add_command(
            label="   1000", command=lambda: self.set_bytes("1000", 0)
        )
        self.twothousand = self.byte_menu.add_command(
            label="   2000", command=lambda: self.set_bytes("2000", 1)
        )
        self.threethousand = self.byte_menu.add_command(
            label="✓ 3000", command=lambda: self.set_bytes("3000", 2)
        )
        self.fourthousand = self.byte_menu.add_command(
            label="   4000", command=lambda: self.set_bytes("4000", 3)
        )
        self.fivethousand = self.byte_menu.add_command(
            label="   5000", command=lambda: self.set_bytes("5000", 4)
        )
        self.fivethousand = self.byte_menu.add_command(
            label="   7500", command=lambda: self.set_bytes("7500", 5)
        )

        editmenu.add_cascade(label="Byte Limit", menu=self.byte_menu)

        menubar.add_cascade(label="Settings", menu=editmenu)

    def extraction_adjustment_frame(self):

        win = tk.Toplevel()
        win.wm_title("Customize File Format")

        # -- new frame --#
        row_value = 0
        container = tk.Frame(win, relief="groove", bd=2)
        container.grid(row=row_value, column=0, columnspan=2, padx=5, pady=5, ipadx=3)

        container_value = 0
        lc = tk.Label(container, text="Current is in Column:")
        lc.grid(row=container_value, column=0)

        container_value += 1
        self.list_val_entry = tk.Entry(container, width=5)
        self.list_val_entry.insert(tk.END, cg.current_column)
        self.list_val_entry.grid(row=container_value, column=0, pady=5)

        container_value = 0
        lv = tk.Label(container, text="Voltage is in Column:")
        lv.grid(row=container_value, column=1)

        container_value += 1
        self.voltage_column = tk.Entry(container, width=5)
        self.voltage_column.insert(tk.END, cg.voltage_column)
        self.voltage_column.grid(row=container_value, column=1, pady=5)

        container_value += 1
        lm = tk.Label(
            container, text="Multipotentiostat Settings\nSpace Between Current Columns:"
        )
        lm.grid(row=container_value, column=0, columnspan=2)

        # -- frameception --#
        container_value += 1
        inner_frame = tk.Frame(container)
        inner_frame.grid(row=container_value, column=0, columnspan=2)
        self.spacing_label = tk.Label(inner_frame, text="\t         Columns").grid(
            row=0, column=0
        )

        self.spacing_val_entry = tk.Entry(inner_frame, width=4)
        self.spacing_val_entry.insert(tk.END, 3)
        self.spacing_val_entry.grid(row=0, column=0, pady=1)

        # -- new frame --#

        row_value += 1
        box = tk.Frame(win, relief="groove", bd=2)
        box.grid(row=row_value, column=0, columnspan=2, pady=7)

        box_value = 0
        ld = tk.Label(box, text="Delimiter between\ndata columns:")
        ld.grid(row=box_value, column=0)

        box_value += 1
        self.space_delimiter = tk.Radiobutton(
            box, text="Space", variable=self.delimiter_value, value=1
        )
        self.space_delimiter.grid(row=box_value, column=0, pady=5)

        box_value += 1
        self.tab_delimiter = tk.Radiobutton(
            box, text="Tab", variable=self.delimiter_value, value=2
        )
        self.tab_delimiter.grid(row=box_value, column=0, pady=3)

        box_value += 1
        self.tab_delimiter = tk.Radiobutton(
            box, text="Comma", variable=self.delimiter_value, value=3
        )
        self.tab_delimiter.grid(row=box_value, column=0, pady=3)

        box_value = 0
        lf = tk.Label(box, text="File Extension")
        lf.grid(row=box_value, column=1)

        box_value += 1
        self.txt_value = tk.Radiobutton(
            box, text="txt", variable=self.extension_value, value=1
        )
        self.txt_value.grid(row=box_value, column=1, pady=5)

        box_value += 1
        self.csv_value = tk.Radiobutton(
            box, text="csv", variable=self.extension_value, value=2
        )
        self.csv_value.grid(row=box_value, column=1, pady=3)

        box_value += 1
        self.dta_value = tk.Radiobutton(
            box, text="dta", variable=self.extension_value, value=3
        )
        self.dta_value.grid(row=box_value, column=1, pady=3)

        row_value += 1
        apply_list_val = ttk.Button(
            win, text="Apply", command=self.get_list_val  # was lambda
        )
        apply_list_val.grid(row=row_value, column=0, pady=6)

        exitButton = ttk.Button(win, text="Exit", command=win.destroy)  # was lambda
        exitButton.grid(row=row_value, column=1, pady=3)

    def get_list_val(self):
        cg.current_column = int(self.list_val_entry.get())
        cg.current_column_index = cg.current_column - 1

        cg.spacing_index = int(self.spacing_val_entry.get())

        cg.voltage_column = int(self.voltage_column.get())
        cg.voltage_column_index = cg.voltage_column - 1

        # Set the delimiter and extension ###
        cg.delimiter = self.delimiter_value.get()
        cg.extension = self.extension_value.get()

    def set_bytes(self, the_bytes, index):
        # -- reset the self.byte_menu widgets --#
        self.byte_menu.entryconfigure(index, label="✓%s" % the_bytes)
        self.byte_menu.entryconfigure(cg.byte_index, label="   %s" % str(cg.byte_limit))

        # -- now change the current data being used --#
        cg.byte_limit = int(the_bytes)
        cg.byte_index = index

    @staticmethod
    def show_frame(cont):

        frame = cg.ShowFrames[cont]
        frame.tkraise()

    def onExit(self):
        self.master.destroy()
        self.master.quit()
        quit()
