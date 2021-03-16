# ------------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------------#

########################
# Import Libraries ###
########################


# ---Clear mac terminal memory---#
import os
import matplotlib

matplotlib.use("TkAgg")
# os.system("clear")

# ---Import Modules---#
import time
import datetime
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, Menu


from matplotlib import style
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import csv

from numpy import sqrt
from scipy.signal import savgol_filter

# from itertools import *  # noqa
import threading
from queue import Queue

# global variables moved to dataclass
from config import Config

cg = Config()

# ---Filter out error warnings---#
import warnings

warnings.simplefilter("ignore", np.RankWarning)  # numpy polyfit_deg warning
warnings.filterwarnings(
    action="ignore", module="scipy", message="^internal gelsd"
)  # RuntimeWarning

style.use("ggplot")


# ------------------------------------------------------------------------------------#
# -----------------------------------------------------------------__-----------------#

# -- file handle variable --#
cg.handle_variable = ""  # default handle variable is nothing
cg.e_var = "single"  # default input file is 'Multichannel', or a single file
# containing all electrodes
PHE_method = "Abs"  # default PHE Extraction is difference between absolute max/min

# ------------------------------------------------------------#

cg.InputFrequencies = [
    30,
    80,
    240,
]  # frequencies initially displayed in Frequency Listbox
electrodes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]

# ------------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------------#

########################
# Global Variables ###
########################

########################################
# Polynomial Regression Parameters ###
########################################
cg.sg_window = (
    5  # Savitzky-Golay window (in mV range), must be odd number (increase signal:noise)
)
cg.sg_degree = 1  # Savitzky-Golay polynomial degree
cg.polyfit_deg = 15  # degree of polynomial fit

cg.cutoff_frequency = 50  # frequency that separates 'low' and 'high'
# frequencies for regression analysis and
# smoothing manipulation

#############################
# Checkpoint Parameters ###
#############################
cg.key = 0  # SkeletonKey
search_lim = 15  # Search limit (sec)
cg.PoisonPill = False  # Stop Animation variable
cg.FoundFilePath = False  # If the user-inputted file is found
cg.ExistVar = False  # If Checkpoints are not met ExistVar = True
cg.AlreadyInitiated = False  # indicates if the user has already initiated analysis
cg.HighAlreadyReset = False  # If data for high frequencies has been reset
cg.LowAlreadyReset = False  # If data for low frequencies has been reset
cg.analysis_complete = False  # If analysis has completed, begin PostAnalysis

##################################
# Data Extraction Parameters ###
##################################
cg.delimiter = 1  # default delimiter is a space; 2 = tab
cg.extension = 1
cg.current_column = 4  # column index for list_val.
cg.current_column_index = 3
# list_val = column_index + 3
# defauly column is the second (so index = 1)
cg.voltage_column = 1
cg.voltage_column_index = 0
cg.spacing_index = 3

# -- set the initial limit in bytes to filter out preinitialized files < 3000b
cg.byte_limit = 3000
# - set the initial bite index to match the checkbutton
# - index in the toolbar menu MainWindow.byte_menu
cg.byte_index = 2

######################################################
# Low frequency baseline manipulation Parameters ###
######################################################
cg.LowFrequencyOffset = 0  # Vertical offset of normalized data for
# user specified 'Low Frequency'
cg.LowFrequencySlope = 0  # Slope manipulation of norm data for user
# specified 'Low Frequency'


###############
# Styling ###
###############
HUGE_FONT = ("Verdana", 18)
LARGE_FONT = ("Verdana", 11)
MEDIUM_FONT = ("Verdnana", 10)
SMALL_FONT = ("Verdana", 8)


########################
# Global Functions ###
########################


##############################
# Retrieve the file name ###
##############################
def _retrieve_file(file, electrode, frequency):
    try:
        if cg.method == "Continuous Scan":

            if cg.e_var == "single":
                filename = "%s%dHz_%d%s" % (
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename2 = "%s%dHz__%d%s" % (
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename3 = "%s%dHz_#%d%s" % (
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename4 = "%s%dHz__#%d%s" % (
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )

            elif cg.e_var == "multiple":
                filename = "E%s_%s%sHz_%d%s" % (
                    electrode,
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename2 = "E%s_%s%sHz__%d%s" % (
                    electrode,
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename3 = "E%s_%s%sHz_#%d%s" % (
                    electrode,
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename4 = "E%s_%s%sHz__#%d%s" % (
                    electrode,
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )

            return filename, filename2, filename3, filename4

        if cg.method == "Frequency Map":

            if cg.e_var == "single":
                filename = "%s%dHz%s" % (cg.handle_variable, frequency, cg.extension)
                filename2 = "%s%dHz_%s" % (cg.handle_variable, frequency, cg.extension)
                filename3 = "%s%dHz_%d%s" % (
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename4 = "%s%dHz__%d%s" % (
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename5 = "%s%dHz_#%d%s" % (
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename6 = "%s%dHz__#%d%s" % (
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )

            elif cg.e_var == "multiple":
                filename = "E%s_%s%sHz%s" % (
                    electrode,
                    cg.handle_variable,
                    frequency,
                    cg.extension,
                )
                filename2 = "E%s_%s%sHz_%s" % (
                    electrode,
                    cg.handle_variable,
                    frequency,
                    cg.extension,
                )
                filename3 = "E%s_%s%sHz_%d%s" % (
                    electrode,
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename4 = "E%s_%s%sHz__%d%s" % (
                    electrode,
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename5 = "E%s_%s%sHz_#%d%s" % (
                    electrode,
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename6 = "E%s_%s%sHz__#%d%s" % (
                    electrode,
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )

            return filename, filename2, filename3, filename4, filename5, filename6
    except:
        print("\nError in retrieve_file\n")


def ReadData(myfile, electrode):

    try:
        ###############################################################
        # Get the index value of the data depending on if the     ###
        # electrodes are in the same .txt file or separate files  ###
        ###############################################################
        if cg.e_var == "single":
            cg.list_val = cg.current_column_index + (electrode - 1) * cg.spacing_index
        elif cg.e_var == "multiple":
            cg.list_val = cg.current_column_index

        #####################
        # Read the data ###
        #####################
        try:
            # ---Preallocate Potential and Current lists---#
            with open(myfile, "r", encoding="utf-16") as mydata:
                cg.encoding = "utf-16"

                variables = len(mydata.readlines())
                potentials = ["hold"] * variables
                # key: potential; value: current ##
                data_dict = {}

                currents = [0] * variables

        except:
            # ---Preallocate Potential and Current lists---#
            with open(myfile, "r", encoding="utf-8") as mydata:
                cg.encoding = "utf-8"

                variables = len(mydata.readlines())
                potentials = ["hold"] * variables
                # key: potential; value: current ##
                data_dict = {}

                currents = [0] * variables

        # ---Extract data and dump into lists---#
        with open(myfile, "r", encoding=cg.encoding) as mydata:
            list_num = 0
            for line in mydata:
                check_split_list = line.split(cg.delimiter)
                # delete any spaces that may come before the first value #
                while True:
                    if check_split_list[0] == "":
                        del check_split_list[0]
                    else:
                        break

                # delete any tabs that may come before the first value #
                while True:
                    if check_split_list[0] == " ":
                        del check_split_list[0]
                    else:
                        break
                check_split = check_split_list[0]
                check_split = check_split.replace(",", "")
                try:
                    check_split = float(check_split)
                    check_split = True
                except:
                    check_split = False
                if check_split:
                    # ---Currents---#
                    current_value = check_split_list[
                        cg.list_val
                    ]  # list_val is the index value of the given electrode
                    current_value = current_value.replace(",", "")
                    current_value = float(current_value)
                    current_value = current_value * 1000000
                    currents[list_num] = current_value

                    # ---Potentials---#
                    potential_value = line.split(cg.delimiter)[cg.voltage_column_index]
                    potential_value = potential_value.strip(",")
                    potential_value = float(potential_value)
                    potentials[list_num] = potential_value
                    data_dict.setdefault(potential_value, []).append(current_value)
                    list_num = list_num + 1

        # if there are 0's in the list (if the preallocation added to many)
        # then remove them
        cut_value = 0
        for value in potentials:
            if value == "hold":
                cut_value += 1

        if cut_value > 0:
            potentials = potentials[:-cut_value]
            currents = currents[:-cut_value]

        #######################
        # Return the data ###
        #######################
        return potentials, currents, data_dict
    except:
        print("\nError in ReadData()\n")


#######################################
# Retrieve the column index value ###
#######################################
def _get_listval(electrode):
    try:
        if cg.e_var == "single":
            cg.list_val = cg.current_column_index + (electrode - 1) * cg.spacing_index

        elif cg.e_var == "multiple":
            cg.list_val = cg.current_column_index

            return cg.list_val
    except:
        print("\nError in _get_listval\n")


# ------------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------------#


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
        frame = InputFrame(cg.container, self.master)
        cg.ShowFrames[InputFrame] = frame
        frame.grid(row=0, column=0, sticky="nsew")
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
        editmenu = Menu(menubar, tearoff=0)
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

    def show_frame(self, cont):

        frame = cg.ShowFrames[cont]
        frame.tkraise()

    def onExit(self):
        self.master.destroy()
        self.master.quit()
        quit()


class InputFrame(
    tk.Frame
):  # first frame that is displayed when the program is initialized
    def __init__(self, parent, controller):

        self.parent = parent
        self.controller = controller

        tk.Frame.__init__(self, parent)  # initialize the frame

        row_value = 0

        ##############################################
        # Pack all of the widgets into the frame ###
        ##############################################

        self.SelectFilePath = ttk.Button(
            self,
            style="Off.TButton",
            text="Select File Path",
            command=lambda: self.FindFile(parent),
        )
        self.SelectFilePath.grid(row=row_value, column=0, columnspan=4)
        row_value += 2

        self.NoSelectedPath = tk.Label(
            self, text="No File Path Selected", font=MEDIUM_FONT, fg="red"
        )
        self.PathWarningExists = False  # tracks the existence of a warning label

        ImportFileLabel = tk.Label(
            self, text="Import File Label", font=LARGE_FONT
        ).grid(row=row_value, column=0, columnspan=2)
        self.ImportFileEntry = tk.Entry(self)
        self.ImportFileEntry.grid(row=row_value + 1, column=0, columnspan=2, pady=5)
        self.ImportFileEntry.insert(tk.END, cg.handle_variable)

        # --- File Handle Input ---#
        HandleLabel = tk.Label(self, text="Exported File Handle:", font=LARGE_FONT)
        HandleLabel.grid(row=row_value, column=2, columnspan=2)
        self.filehandle = ttk.Entry(self)
        now = datetime.datetime.now()
        day = str(now.day)
        month = str(now.month)
        year = str(now.year)
        self.filehandle.insert(tk.END, "DataExport_%s_%s_%s.txt" % (year, month, day))
        self.filehandle.grid(row=row_value + 1, column=2, columnspan=2, pady=5)

        row_value += 2

        EmptyLabel = tk.Label(self, text="", font=LARGE_FONT).grid(
            row=row_value, rowspan=2, column=0, columnspan=10
        )
        row_value += 1

        # ---File Limit Input---#
        numFileLabel = tk.Label(self, text="Number of Files:", font=LARGE_FONT)
        numFileLabel.grid(row=row_value, column=0, columnspan=2, pady=4)
        self.numfiles = ttk.Entry(self, width=7)
        self.numfiles.insert(tk.END, "50")
        self.numfiles.grid(row=row_value + 1, column=0, columnspan=2, pady=6)

        # --- Analysis interval for event callback in ElectrochemicalAnimation ---#
        IntervalLabel = tk.Label(self, text="Analysis Interval (ms):", font=LARGE_FONT)
        IntervalLabel.grid(row=row_value, column=2, columnspan=2, pady=4)
        self.Interval = ttk.Entry(self, width=7)
        self.Interval.insert(tk.END, "10")
        self.Interval.grid(row=row_value + 1, column=2, columnspan=2, pady=6)

        row_value += 2

        # ---Sample Rate Variable---#
        SampleLabel = tk.Label(self, text="Sampling Rate (s):", font=LARGE_FONT)
        SampleLabel.grid(row=row_value, column=0, columnspan=2)
        self.sample_rate = ttk.Entry(self, width=7)
        self.sample_rate.insert(tk.END, "20")
        self.sample_rate.grid(row=row_value + 1, column=0, columnspan=2)

        self.resize_label = tk.Label(self, text="Resize Interval", font=LARGE_FONT)
        self.resize_label.grid(row=row_value, column=2, columnspan=2)
        self.resize_entry = tk.Entry(self, width=7)
        self.resize_entry.insert(tk.END, "200")
        self.resize_entry.grid(row=row_value + 1, column=2, columnspan=2)

        row_value += 2

        ##################################
        # Select and Edit Electrodes ###
        ##################################

        self.ElectrodeListboxFrame = tk.Frame(
            self
        )  # create a frame to pack in the Electrode box and
        self.ElectrodeListboxFrame.grid(
            row=row_value,
            column=0,
            columnspan=2,
            padx=10,
            pady=10,
            ipady=5,
            sticky="nsew",
        )

        # --- parameters for handling resize ---#
        self.ElectrodeListboxFrame.rowconfigure(0, weight=1)
        self.ElectrodeListboxFrame.rowconfigure(1, weight=1)
        self.ElectrodeListboxFrame.columnconfigure(0, weight=1)
        self.ElectrodeListboxFrame.columnconfigure(1, weight=1)

        self.ElectrodeListExists = False
        self.ElectrodeLabel = tk.Label(
            self.ElectrodeListboxFrame, text="Select Electrodes:", font=LARGE_FONT
        )
        self.ElectrodeLabel.grid(row=0, column=0, columnspan=2, sticky="nswe")
        self.ElectrodeCount = tk.Listbox(
            self.ElectrodeListboxFrame,
            relief="groove",
            exportselection=0,
            width=10,
            font=LARGE_FONT,
            height=6,
            selectmode="multiple",
            bd=3,
        )
        self.ElectrodeCount.bind("<<ListboxSelect>>", self.ElectrodeCurSelect)
        self.ElectrodeCount.grid(row=1, column=0, columnspan=2, sticky="nswe")
        for electrode in electrodes:
            self.ElectrodeCount.insert(tk.END, electrode)

        self.scrollbar = tk.Scrollbar(self.ElectrodeListboxFrame, orient="vertical")
        self.scrollbar.config(width=10, command=self.ElectrodeCount.yview)
        self.scrollbar.grid(row=1, column=1, sticky="nse")
        self.ElectrodeCount.config(yscrollcommand=self.scrollbar.set)

        # --- Option to have data for all electrodes in a single file ---#
        self.SingleElectrodeFile = ttk.Button(
            self.ElectrodeListboxFrame,
            text="Multichannel",
            style="On.TButton",
            command=lambda: self.ElectrodeSelect("Multichannel"),
        )
        self.SingleElectrodeFile.grid(row=2, column=0)

        # --- Option to have data for each electrode in a separate file ---#
        self.MultipleElectrodeFiles = ttk.Button(
            self.ElectrodeListboxFrame,
            text="Multiplex",
            style="Off.TButton",
            command=lambda: self.ElectrodeSelect("Multiplex"),
        )
        self.MultipleElectrodeFiles.grid(row=2, column=1)

        # --- Frame for editing electrodes ---#
        self.ElectrodeSettingsFrame = tk.Frame(self, relief="groove", bd=3)
        self.ElectrodeSettingsFrame.grid(
            row=10, column=0, columnspan=2, padx=10, pady=10, sticky="nsew"
        )
        self.ElectrodeSettingsFrame.columnconfigure(0, weight=1)
        self.ElectrodeSettingsFrame.rowconfigure(0, weight=1)
        self.ElectrodeSettingsFrame.rowconfigure(1, weight=1)
        self.ElectrodeSettingsFrame.rowconfigure(2, weight=1)

        #####################################################
        # Select and Edit Frequencies for Data Analysis ###
        #####################################################

        self.ListboxFrame = tk.Frame(
            self
        )  # create a frame to pack in the frequency box and scrollbar
        self.ListboxFrame.grid(
            row=row_value, column=2, columnspan=2, padx=10, pady=10, sticky="nsew"
        )
        frequencies = cg.InputFrequencies

        # -- resize ---#
        self.ListboxFrame.rowconfigure(0, weight=1)
        self.ListboxFrame.rowconfigure(1, weight=1)
        self.ListboxFrame.columnconfigure(0, weight=1)

        self.FrequencyLabel = tk.Label(
            self.ListboxFrame, text="Select Frequencies", font=LARGE_FONT
        )
        self.FrequencyLabel.grid(row=0, padx=10)

        # --- If more than 5 frequencies are in the listbox,
        # add a scrollbar as to not take up too much space ---#
        if len(cg.InputFrequencies) > 5:
            self.ScrollBarVal = True
        else:
            self.ScrollBarVal = False

        # --- Variable to check if the frequency_list contains frequencies ---#
        self.FrequencyListExists = False

        # --- ListBox containing the frequencies given on line 46 (InputFrequencies) -#
        self.FrequencyList = tk.Listbox(
            self.ListboxFrame,
            relief="groove",
            exportselection=0,
            width=5,
            font=LARGE_FONT,
            height=6,
            selectmode="multiple",
            bd=3,
        )
        self.FrequencyList.bind("<<ListboxSelect>>", self.FrequencyCurSelect)
        self.FrequencyList.grid(row=1, padx=10, sticky="nswe")
        for frequency in frequencies:
            self.FrequencyList.insert(tk.END, frequency)

        # --- Scroll Bar ---#
        if self.ScrollBarVal:
            self.scrollbar = tk.Scrollbar(self.ListboxFrame, orient="vertical")
            self.scrollbar.config(width=10, command=self.FrequencyList.yview)
            self.scrollbar.grid(row=1, sticky="nse")
            self.FrequencyList.config(yscrollcommand=self.scrollbar.set)

        ManipulateFrequencies = tk.Button(
            self.ListboxFrame,
            text="Edit",
            font=MEDIUM_FONT,
            command=lambda: cg.ManipulateFrequenciesFrame.tkraise(),
        ).grid(row=2, column=0, columnspan=4)

        ###########################################################
        # Frame for adding/deleting frequencies from the list ###
        ###########################################################

        cg.ManipulateFrequenciesFrame = tk.Frame(self, width=10, bd=3, relief="groove")
        cg.ManipulateFrequenciesFrame.grid(
            row=row_value, column=2, columnspan=2, padx=10, pady=10, sticky="nsew"
        )

        ManipulateFrequencyLabel = tk.Label(
            cg.ManipulateFrequenciesFrame, text="Enter Frequency(s)", font=MEDIUM_FONT
        )
        ManipulateFrequencyLabel.grid(row=0, column=0, columnspan=4)

        self.FrequencyEntry = tk.Entry(cg.ManipulateFrequenciesFrame, width=8)
        self.FrequencyEntry.grid(row=1, column=0, columnspan=4)

        AddFrequencyButton = tk.Button(
            cg.ManipulateFrequenciesFrame,
            text="Add",
            font=MEDIUM_FONT,
            command=self.AddFrequency,  # was lambda
        ).grid(row=2, column=0)
        DeleteFrequencyButton = tk.Button(
            cg.ManipulateFrequenciesFrame,
            text="Delete",
            font=MEDIUM_FONT,
            command=self.DeleteFrequency,  # was lambda
        ).grid(row=2, column=1)
        ClearFrequencyButton = tk.Button(
            cg.ManipulateFrequenciesFrame,
            text="Clear",
            font=MEDIUM_FONT,
            command=self.Clear,  # was lambda
        ).grid(row=3, column=0, columnspan=2)

        ReturnButton = tk.Button(
            cg.ManipulateFrequenciesFrame,
            text="Return",
            font=MEDIUM_FONT,
            command=self.Return,  # was lambda
        ).grid(row=4, column=0, columnspan=2)

        cg.ManipulateFrequenciesFrame.rowconfigure(0, weight=1)
        cg.ManipulateFrequenciesFrame.rowconfigure(1, weight=1)
        cg.ManipulateFrequenciesFrame.rowconfigure(2, weight=1)
        cg.ManipulateFrequenciesFrame.rowconfigure(3, weight=1)
        cg.ManipulateFrequenciesFrame.rowconfigure(4, weight=1)
        cg.ManipulateFrequenciesFrame.columnconfigure(0, weight=1)
        cg.ManipulateFrequenciesFrame.columnconfigure(1, weight=1)

        row_value += 1

        # --- Select Analysis Method---#
        Methods = ["Continuous Scan", "Frequency Map"]
        MethodsLabel = tk.Label(self, text="Select Analysis Method", font=LARGE_FONT)
        self.MethodsBox = tk.Listbox(
            self,
            relief="groove",
            exportselection=0,
            font=LARGE_FONT,
            height=len(Methods),
            selectmode="single",
            bd=3,
        )
        self.MethodsBox.bind("<<ListboxSelect>>", self.SelectMethod)
        MethodsLabel.grid(row=row_value, column=0, columnspan=4)
        row_value += 1
        self.MethodsBox.grid(row=row_value, column=0, columnspan=4)
        row_value += 1
        for method in Methods:
            self.MethodsBox.insert(tk.END, method)

        # --- Select Data to be Plotted ---#
        Options = ["Peak Height Extraction", "Area Under the Curve"]
        OptionsLabel = tk.Label(self, text="Select Data to be Plotted", font=LARGE_FONT)
        self.PlotOptions = tk.Listbox(
            self,
            relief="groove",
            exportselection=0,
            font=LARGE_FONT,
            height=len(Options),
            selectmode="single",
            bd=3,
        )
        self.PlotOptions.bind("<<ListboxSelect>>", self.SelectPlotOptions)
        OptionsLabel.grid(row=row_value, column=0, columnspan=2)
        self.PlotOptions.grid(row=row_value + 1, column=0, columnspan=2)

        for option in Options:
            self.PlotOptions.insert(tk.END, option)

        # --- Warning label for if the user does not select an analysis method ---#
        self.NoOptionsSelected = tk.Label(
            self, text="Select a Data Analysis Method", font=MEDIUM_FONT, fg="red"
        )  # will only be added to the grid (row 16) if they dont select an option
        self.NoSelection = False

        # --- Select units of the X-axis ---#
        PlotOptions = ["Experiment Time", "File Number"]
        PlotLabel = tk.Label(self, text="Select X-axis units", font=LARGE_FONT)
        self.XaxisOptions = tk.Listbox(
            self,
            relief="groove",
            exportselection=0,
            font=LARGE_FONT,
            height=len(PlotOptions),
            selectmode="single",
            bd=3,
        )
        self.XaxisOptions.bind("<<ListboxSelect>>", self.SelectXaxisOptions)
        PlotLabel.grid(row=row_value, column=2, columnspan=2)
        self.XaxisOptions.grid(row=row_value + 1, column=2, columnspan=2)
        for option in PlotOptions:
            self.XaxisOptions.insert(tk.END, option)

        row_value += 2
        ############################################################
        # Adjustment of Visualization Parameters: xstart, xend ###
        ############################################################

        # --- Create a frame that will contain all of the widgets ---#
        AdjustmentFrame = tk.Frame(self, relief="groove", bd=3)
        AdjustmentFrame.grid(row=row_value, column=0, columnspan=4, pady=15)
        row_value += 1
        AdjustmentFrame.rowconfigure(0, weight=1)
        AdjustmentFrame.rowconfigure(1, weight=1)
        AdjustmentFrame.rowconfigure(2, weight=1)
        AdjustmentFrame.rowconfigure(3, weight=1)
        AdjustmentFrame.rowconfigure(4, weight=1)
        AdjustmentFrame.columnconfigure(0, weight=1)
        AdjustmentFrame.columnconfigure(1, weight=1)
        AdjustmentFrame.columnconfigure(2, weight=1)
        AdjustmentFrame.columnconfigure(3, weight=1)

        # --- Y Limit Adjustment Variables ---#
        self.y_limit_parameter_label = tk.Label(
            AdjustmentFrame, text="Select Y Limit Parameters", font=LARGE_FONT
        )
        self.y_limit_parameter_label.grid(row=0, column=0, columnspan=4, pady=5, padx=5)

        # --- Raw Data Minimum Parameter Adjustment ---#
        self.raw_data_min_parameter_label = tk.Label(
            AdjustmentFrame, text="Raw Min. Factor", font=MEDIUM_FONT
        )
        self.raw_data_min_parameter_label.grid(row=1, column=0)
        self.raw_data_min = tk.Entry(AdjustmentFrame, width=5)
        self.raw_data_min.insert(
            tk.END, "2"
        )  # initial minimum is set to 0.5*minimum current (baseline) of file 1
        self.raw_data_min.grid(row=2, column=0, padx=5, pady=2, ipadx=2)

        # --- Raw Data Maximum Parameter Adjustment ---#
        self.raw_data_max_parameter_label = tk.Label(
            AdjustmentFrame, text="Raw Max. Factor", font=MEDIUM_FONT
        )
        self.raw_data_max_parameter_label.grid(row=3, column=0)
        self.raw_data_max = tk.Entry(AdjustmentFrame, width=5)
        self.raw_data_max.insert(
            tk.END, "2"
        )  # initial adjustment is set to 2x the max current (Peak Height) of file 1
        self.raw_data_max.grid(row=4, column=0, padx=5, pady=2, ipadx=2)

        # --- Raw Data Minimum Parameter Adjustment ---#
        self.data_min_parameter_label = tk.Label(
            AdjustmentFrame, text="Data Min. Factor", font=MEDIUM_FONT
        )
        self.data_min_parameter_label.grid(row=1, column=1)
        self.data_min = tk.Entry(AdjustmentFrame, width=5)
        self.data_min.insert(
            tk.END, "2"
        )  # initial minimum is set to 0.5*minimum current (baseline) of file 1
        self.data_min.grid(row=2, column=1, padx=5, pady=2, ipadx=2)

        # --- Raw Data Maximum Parameter Adjustment ---#
        self.data_max_parameter_label = tk.Label(
            AdjustmentFrame, text="Data Max. Factor", font=MEDIUM_FONT
        )
        self.data_max_parameter_label.grid(row=3, column=1)
        self.data_max = tk.Entry(AdjustmentFrame, width=5)
        self.data_max.insert(
            tk.END, "2"
        )  # initial adjustment is set to 2x the max current (Peak Height) of file 1
        self.data_max.grid(row=4, column=1, padx=5, pady=2, ipadx=2)

        # --- Normalized Data Minimum Parameter Adjustment ---#
        self.norm_data_min_parameter_label = tk.Label(
            AdjustmentFrame, text="Norm. Min.", font=MEDIUM_FONT
        )
        self.norm_data_min_parameter_label.grid(row=1, column=2)
        self.norm_data_min = tk.Entry(AdjustmentFrame, width=5)
        self.norm_data_min.insert(tk.END, "0")  # initial minimum is set to 0
        self.norm_data_min.grid(row=2, column=2, padx=5, pady=2, ipadx=2)

        # --- Normalized Data Maximum Parameter Adjustment ---#
        self.norm_data_max_parameter_label = tk.Label(
            AdjustmentFrame, text="Norm. Max.", font=MEDIUM_FONT
        )
        self.norm_data_max_parameter_label.grid(row=3, column=2)
        self.norm_data_max = tk.Entry(AdjustmentFrame, width=5)
        self.norm_data_max.insert(tk.END, "2")  # initial maximum is set to 2
        self.norm_data_max.grid(row=4, column=2, padx=5, pady=2, ipadx=2)

        # --- Raw Data Minimum Parameter Adjustment ---#
        self.KDM_min_label = tk.Label(
            AdjustmentFrame, text="KDM Min.", font=MEDIUM_FONT
        )
        self.KDM_min_label.grid(row=1, column=3)
        self.KDM_min = tk.Entry(AdjustmentFrame, width=5)
        self.KDM_min.insert(
            tk.END, "0"
        )  # initial minimum is set to 0.5*minimum current (baseline) of file 1
        self.KDM_min.grid(row=2, column=3, padx=5, pady=2, ipadx=2)

        # --- Raw Data Maximum Parameter Adjustment ---#
        self.KDM_Max_label = tk.Label(
            AdjustmentFrame, text="KDM Max. ", font=MEDIUM_FONT
        )
        self.KDM_Max_label.grid(row=3, column=3)
        self.KDM_max = tk.Entry(AdjustmentFrame, width=5)
        self.KDM_max.insert(
            tk.END, "2"
        )  # initial adjustment is set to 2x the max current (Peak Height) of file 1
        self.KDM_max.grid(row=4, column=3, padx=5, pady=2, ipadx=2)

        # --- Ask the User if they want to export the data to a .txt file ---#
        self.SaveVar = tk.BooleanVar()
        self.SaveVar.set(False)
        self.SaveBox = tk.Checkbutton(
            self,
            variable=self.SaveVar,
            onvalue=True,
            offvalue=False,
            text="Export Data",
        ).grid(row=row_value, column=0, columnspan=2)

        # --- Ask the User if they want to export the data to a .txt file ---#
        self.InjectionVar = tk.BooleanVar()
        self.InjectionVar.set(False)
        self.InjectionCheck = tk.Checkbutton(
            self,
            variable=self.InjectionVar,
            onvalue=True,
            offvalue=False,
            text="Injection Experiment?",
        ).grid(row=row_value, column=2, columnspan=2)
        row_value += 1

        # --- Quit Button ---#
        self.QuitButton = ttk.Button(
            self, width=9, text="Quit Program", command=quit  # was lambda
        )
        self.QuitButton.grid(row=row_value, column=0, columnspan=2, pady=10, padx=10)

        # --- Button to Initialize Data Analysis --#
        StartButton = ttk.Button(
            self, width=9, text="Initialize", command=self.CheckPoint  # was lambda
        )
        StartButton.grid(row=row_value, column=2, columnspan=2, pady=10, padx=10)
        row_value += 1

        for row in range(row_value):
            row += 1
            self.rowconfigure(row, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        # Raise the initial frame for Electrode and Frequency Selection ###
        self.ListboxFrame.tkraise()
        self.ElectrodeListboxFrame.tkraise()

    #################################################
    # Functions to track Selections and Entries ###
    #################################################

    def AddFrequency(self):
        Frequencies = self.FrequencyEntry.get()
        self.FrequencyEntry.delete(0, tk.END)

        if Frequencies is not None:
            FrequencyList = Frequencies.split(" ")
            for frequency in FrequencyList:
                if int(frequency) not in cg.InputFrequencies:
                    cg.InputFrequencies.append(int(frequency))
            cg.InputFrequencies.sort()

            self.FrequencyList.delete(0, 1)
            self.FrequencyList.delete(0, tk.END)

            for frequency in cg.InputFrequencies:
                self.FrequencyList.insert(tk.END, frequency)

    def DeleteFrequency(self):
        Frequencies = self.FrequencyEntry.get()
        self.FrequencyEntry.delete(0, tk.END)

        if Frequencies is not None:
            FrequencyList = Frequencies.split(" ")

            for Frequency in FrequencyList:

                Frequency = int(Frequency)
                if Frequency in cg.InputFrequencies:
                    cg.InputFrequencies.remove(Frequency)

                self.FrequencyList.delete(0, tk.END)

                for frequency in cg.InputFrequencies:
                    self.FrequencyList.insert(tk.END, int(frequency))

    def Clear(self):
        self.FrequencyList.delete(0, tk.END)
        cg.InputFrequencies = []

    def Return(self):
        self.ListboxFrame.tkraise()
        self.FrequencyEntry.delete(0, tk.END)

    def ElectrodeSettings(self):
        self.ElectrodeSettingsFrame.tkraise()

    def ElectrodeSelect(self, variable):

        if variable == "Multiplex":
            cg.e_var = "multiple"

            self.SingleElectrodeFile["style"] = "Off.TButton"
            self.MultipleElectrodeFiles["style"] = "On.TButton"

        elif variable == "Multichannel":
            cg.e_var = "single"

            self.SingleElectrodeFile["style"] = "On.TButton"
            self.MultipleElectrodeFiles["style"] = "Off.TButton"

    def FindFile(self, parent):

        try:

            # prompt the user to select a  ###
            # directory for  data analysis ###
            cg.FilePath = filedialog.askdirectory(parent=parent)
            cg.FilePath = "".join(cg.FilePath + "/")

            # Path for directory in which the    ###
            # exported .txt file will be placed  ###
            cg.ExportPath = cg.FilePath.split("/")

            # -- change the text of the find file button to the folder the user chose -#
            cg.DataFolder = "%s/%s" % (cg.ExportPath[-3], cg.ExportPath[-2])

            self.SelectFilePath["style"] = "On.TButton"
            self.SelectFilePath["text"] = cg.DataFolder

            del cg.ExportPath[-1]
            del cg.ExportPath[-1]
            cg.ExportPath = "/".join(cg.ExportPath)
            cg.ExportPath = "".join(cg.ExportPath + "/")

            # Indicates that the user has selected a File Path ###
            cg.FoundFilePath = True

            if self.PathWarningExists:
                self.NoSelectedPath["text"] = ""
                self.NoSelectedPath.grid_forget()

        except:
            print("\n\nInputPage.FindFile: Could Not Find File Path\n\n")

    # --- Analysis Method ---#
    def SelectMethod(self, evt):

        cg.method = str((self.MethodsBox.get(self.MethodsBox.curselection())))

    # --- Analysis Method ---#
    def SelectPlotOptions(self, evt):
        cg.SelectedOptions = str(
            (self.PlotOptions.get(self.PlotOptions.curselection()))
        )

    def SelectXaxisOptions(self, evt):
        cg.XaxisOptions = str((self.XaxisOptions.get(self.XaxisOptions.curselection())))

    # --- Electrode Selection ---#
    def ElectrodeCurSelect(self, evt):
        ###################################################
        # electrode_list: list; ints                    ##
        # electrode_dict: dict; {electrode: index}      ##
        # electrode_count: int                          ##
        ###################################################

        cg.electrode_list = [
            self.ElectrodeCount.get(idx) for idx in self.ElectrodeCount.curselection()
        ]
        cg.electrode_list = [int(electrode) for electrode in cg.electrode_list]
        cg.electrode_count = len(cg.electrode_list)

        index = 0
        cg.electrode_dict = {}
        for electrode in cg.electrode_list:
            cg.electrode_dict[electrode] = index
            index += 1

        if cg.electrode_count == 0:
            self.ElectrodeListExists = False
            self.ElectrodeLabel["fg"] = "red"

        elif cg.electrode_count != 0:
            self.ElectrodeListExists = True
            self.ElectrodeLabel["fg"] = "black"

    # --- Frequency Selection ---#
    def FrequencyCurSelect(self, evt):
        cg.frequency_list = [
            self.FrequencyList.get(idx) for idx in self.FrequencyList.curselection()
        ]

        if len(cg.frequency_list) != 0:

            self.FrequencyListExists = True
            self.FrequencyLabel["fg"] = "black"

            for var in cg.frequency_list:
                var = int(var)

            cg.LowFrequency = min(
                cg.frequency_list
            )  # Initial Low Frequency for KDM/Ratiometric analysis
            cg.HighFrequency = max(
                cg.frequency_list
            )  # Initial High Frequency for KDM/Ratiometric analysis

            cg.HighLowList["High"] = cg.HighFrequency
            cg.HighLowList["Low"] = cg.LowFrequency

            # --- Frequency Dictionary ---#
            cg.frequency_dict = {}
            count = 0
            for frequency in cg.frequency_list:
                frequency = int(frequency)
                cg.frequency_dict[frequency] = count
                count += 1

        elif len(cg.frequency_list) == 0:
            self.FrequencyListExists = False
            self.FrequencyLabel["fg"] = "red"

    # --- Functions to switch frames and plots ---#
    def show_frame(self, cont):

        frame = cg.ShowFrames[cont]
        frame.tkraise()

    # --- Function to switch between visualization frames ---#
    def show_plot(self, frame):
        frame.tkraise()

    #####################################################################
    # Check to see if the user has filled out all  required fields: ###
    # Electrodes, Frequencies, Analysis Method, and File Path. If   ###
    # they have, initialize the program                             ###
    #####################################################################
    def CheckPoint(self):

        try:
            # --- check to see if the data analysis method has been
            # selected by the user ---#
            cg.Option = cg.SelectedOptions

            # --- If a data analysis method was selected and a warning label was
            # already created, forget it ---#
            if self.NoSelection:
                self.NoSelection = False
                self.NoOptionsSelected.grid_forget()
        except:
            # --- if no selection was made, create a warning label telling the user
            # to select an analysis method ---#
            self.NoSelection = True
            self.NoOptionsSelected.grid(row=14, column=0, columnspan=2)

        #########################################################
        # Initialize Canvases and begin tracking animation  ###
        #########################################################
        try:
            cg.mypath = cg.FilePath  # file path
            cg.FileHandle = str(self.filehandle.get())  # handle for exported .txt file
            cg.ExportFilePath = "".join(cg.ExportPath + cg.FileHandle)

            if self.PathWarningExists:
                self.NoSelectedPath.grid_forget()
                self.PathWarningExists = False

        except:
            # -- if the user did not select a file path for data analysis,
            # raise a warning label ---#
            if not cg.FoundFilePath:
                self.NoSelectedPath.grid(row=1, column=0, columnspan=4)
                self.PathWarningExists = True

        if not self.FrequencyListExists:
            self.FrequencyLabel["fg"] = "red"
        elif self.FrequencyListExists:
            self.FrequencyLabel["fg"] = "black"

        if not self.ElectrodeListExists:
            self.ElectrodeLabel["fg"] = "red"
        elif self.ElectrodeListExists:
            self.ElectrodeLabel["fg"] = "black"

        if not self.PathWarningExists:
            if not self.NoSelection:
                if self.FrequencyListExists:
                    self.StartProgram()

                else:
                    print("Could Not Start Program")

    ########################################################################
    # Function To Initialize Data Acquisition, Analysis, and Animation ###
    ########################################################################

    def StartProgram(self):

        # ---Get the User Input and make it globally accessible---#

        cg.SampleRate = float(
            self.sample_rate.get()
        )  # sample rate for experiment in seconds

        if cg.method == "Continuous Scan":
            cg.numFiles = int(self.numfiles.get())  # file limit
        elif cg.method == "Frequency Map":
            cg.numFiles = 1

        cg.q = Queue()

        if cg.delimiter == 1:
            cg.delimiter = " "
        elif cg.delimiter == 2:
            cg.delimiter = "\t"
        elif cg.delimiter == 3:
            cg.delimiter = ","

        if cg.extension == 1:
            cg.extension = ".txt"
        elif cg.extension == 2:
            cg.extension = ".csv"
        elif cg.extension == 3:
            cg.extension = ".DTA"

        cg.InjectionPoint = (
            None  # None variable if user has not selected an injection point
        )
        cg.InitializedNormalization = False  # tracks if the data has been normalized
        # to the starting normalization point
        cg.RatioMetricCheck = False  # tracks changes to high and low frequencies
        cg.NormWarningExists = (
            False  # tracks if a warning label for the normalization has been created
        )

        cg.NormalizationPoint = 3
        cg.starting_file = 1

        cg.SaveVar = self.SaveVar.get()  # tracks if text file export has been activated
        cg.InjectionVar = self.InjectionVar.get()  # tracks if injection was selected
        cg.resize_interval = int(
            self.resize_entry.get()
        )  # interval at which xaxis of plots resizes
        cg.handle_variable = (
            self.ImportFileEntry.get()
        )  # string handle used for the input file

        # --- Y Limit Adjustment Parameters ---#
        cg.min_norm = float(self.norm_data_min.get())  # normalization y limits
        cg.max_norm = float(self.norm_data_max.get())
        cg.min_raw = float(
            self.raw_data_min.get()
        )  # raw data y limit adjustment variables
        cg.max_raw = float(self.raw_data_max.get())
        cg.min_data = float(
            self.data_min.get()
        )  # raw data y limit adjustment variables
        cg.max_data = float(self.data_max.get())
        cg.ratio_min = float(self.KDM_min.get())  # KDM min and max
        cg.ratio_max = float(self.KDM_max.get())

        #############################################################
        # Interval at which the program searches for files (ms) ###
        #############################################################
        cg.Interval = self.Interval.get()

        # set the resizeability of the container ##
        # frame to handle PlotContainer resize   ##
        cg.container.columnconfigure(1, weight=1)

        # --- High and Low Frequency Selection for Drift Correction (KDM) ---#
        cg.HighFrequency = max(cg.frequency_list)
        cg.LowFrequency = min(cg.frequency_list)
        cg.HighLowList["High"] = cg.HighFrequency
        cg.HighLowList["Low"] = cg.LowFrequency

        # --- Create a timevault for normalization variables if the chosen
        # normalization point has not yet been analyzed ---#
        cg.NormalizationVault = []  # timevault for Normalization Points
        cg.NormalizationVault.append(
            cg.NormalizationPoint
        )  # append the starting normalization point

        ################################################################
        # If all checkpoints have been met, initialize the program ###
        ################################################################
        if not self.NoSelection:
            if cg.FoundFilePath:

                checkpoint = CheckPoint(self.parent, self.controller)


# ------------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------------#

####################################
# Checkpoint TopLevel Instance ###
####################################
class CheckPoint:
    def __init__(self, parent, controller):
        # -- Check to see if the user's settings are accurate
        # -- Search for the presence of the files. If they exist,
        # -- initialize the functions and frames for Real Time Analysis

        self.win = tk.Toplevel()
        self.win.wm_title("CheckPoint")

        title = tk.Label(self.win, text="Searching for files...", font=HUGE_FONT).grid(
            row=0, column=0, columnspan=2, pady=10, padx=10, sticky="news"
        )

        self.parent = parent
        self.win.transient(self.parent)
        self.win.attributes("-topmost", "true")
        self.controller = controller

        row_value = 1
        self.frame_dict = {}
        self.label_dict = {}
        self.already_verified = {}
        for electrode in cg.electrode_list:
            electrode_label = tk.Label(
                self.win, text="E%s" % electrode, font=LARGE_FONT
            ).grid(row=row_value, column=0, pady=5, padx=5)
            frame = tk.Frame(self.win, relief="groove", bd=5)
            frame.grid(row=row_value, column=1, pady=5, padx=5)
            self.frame_dict[electrode] = frame
            self.label_dict[electrode] = {}
            self.already_verified[electrode] = {}
            row_value += 1

            column_value = 0
            if cg.method == "Continuous Scan":
                for frequency in cg.frequency_list:
                    label = tk.Label(frame, text="%sHz" % str(frequency), fg="red")
                    label.grid(row=0, column=column_value, padx=5, pady=5)
                    self.label_dict[electrode][frequency] = label
                    self.already_verified[electrode][frequency] = False
                    column_value += 1

            elif cg.method == "Frequency Map":
                electrode_label = tk.Label(
                    frame, text="E%s" % electrode, font=HUGE_FONT
                )
                electrode_label.grid(row=row_value, column=column_value, pady=5, padx=5)
                self.label_dict[electrode][cg.frequency_list[0]] = electrode_label
                self.already_verified[electrode][cg.frequency_list[0]] = False

                if column_value == 1:
                    column_value = 0
                    row_value += 1
                else:
                    column_value = 1

        self.stop = tk.Button(self.win, text="Stop", command=self.stop)
        self.stop.grid(row=row_value, column=0, columnspan=2, pady=5)
        self.StopSearch = False

        self.num = 0
        self.count = 0
        self.analysis_count = 0
        self.analysis_limit = cg.electrode_count * len(cg.frequency_list)
        self.electrode_limit = cg.electrode_count - 1
        self.frequency_limit = len(cg.frequency_list) - 1

        root.after(50, self.verify)

    def verify(self):

        self.electrode = cg.electrode_list[self.num]

        if not self.StopSearch:

            if cg.method == "Continuous Scan":
                for frequency in cg.frequency_list:

                    filename, filename2, filename3, filename4 = _retrieve_file(
                        1, self.electrode, frequency
                    )

                    myfile = cg.mypath + filename  # path of your file
                    myfile2 = cg.mypath + filename2
                    myfile3 = cg.mypath + filename3
                    myfile4 = cg.mypath + filename4

                    try:
                        # retrieves the size of the file in bytes
                        mydata_bytes = os.path.getsize(myfile)
                    except:
                        try:
                            mydata_bytes = os.path.getsize(myfile2)
                            myfile = myfile2
                        except:
                            try:
                                mydata_bytes = os.path.getsize(myfile3)
                                myfile = myfile3
                            except:
                                try:
                                    mydata_bytes = os.path.getsize(myfile4)
                                    myfile = myfile4
                                except:
                                    mydata_bytes = 1

                    if mydata_bytes > cg.byte_limit:

                        if cg.e_var == "single":
                            check_ = self.verify_multi(myfile)
                        else:
                            check_ = True

                        if check_:
                            if not self.already_verified[self.electrode][frequency]:
                                self.already_verified[self.electrode][frequency] = True
                                if not self.StopSearch:
                                    self.label_dict[self.electrode][frequency][
                                        "fg"
                                    ] = "green"
                                    self.analysis_count += 1

                        if self.analysis_count == self.analysis_limit:
                            if not self.StopSearch:
                                self.StopSearch = True
                                self.win.destroy()

                                root.after(10, self.proceed)

                if self.num < self.electrode_limit:
                    self.num += 1

                else:
                    self.num = 0

                if self.analysis_count < self.analysis_limit:
                    if not self.StopSearch:
                        root.after(100, self.verify)

            elif cg.method == "Frequency Map":

                frequency = cg.frequency_list[0]

                (
                    filename,
                    filename2,
                    filename3,
                    filename4,
                    filename5,
                    filename6,
                ) = _retrieve_file(1, self.electrode, frequency)

                myfile = cg.mypath + filename  # path of your file
                myfile2 = cg.mypath + filename2
                myfile3 = cg.mypath + filename3
                myfile4 = cg.mypath + filename4
                myfile5 = cg.mypath + filename5
                myfile6 = cg.mypath + filename6

                try:
                    # retrieves the size of the file in bytes
                    mydata_bytes = os.path.getsize(myfile)
                except:
                    try:
                        mydata_bytes = os.path.getsize(myfile2)
                        myfile = myfile2
                    except:
                        try:
                            mydata_bytes = os.path.getsize(myfile3)
                            myfile = myfile3
                        except:
                            try:
                                mydata_bytes = os.path.getsize(myfile4)
                                myfile = myfile4
                            except:
                                try:
                                    mydata_bytes = os.path.getsize(myfile5)
                                    myfile = myfile5
                                except:
                                    try:
                                        mydata_bytes = os.path.getsize(myfile6)
                                        myfile = myfile6
                                    except:
                                        mydata_bytes = 1

                if mydata_bytes > cg.byte_limit:

                    if cg.e_var == "single":
                        check_ = self.verify_multi(myfile)
                    else:
                        check_ = True

                    if check_:
                        if not self.already_verified[self.electrode][frequency]:
                            self.already_verified[self.electrode][frequency] = True
                            if not self.StopSearch:
                                self.label_dict[self.electrode][frequency][
                                    "fg"
                                ] = "green"
                                self.analysis_count += 1

                    if self.analysis_count == cg.electrode_count:
                        if not self.StopSearch:
                            self.StopSearch = True
                            self.win.destroy()

                            root.after(10, self.proceed)

                if self.num < self.electrode_limit:
                    self.num += 1
                else:
                    self.num = 0

                if self.analysis_count < self.analysis_limit:
                    if not self.StopSearch:
                        root.after(200, self.verify)

    def verify_multi(self, myfile):

        # changing the column index
        # ---Set the electrode index value---#
        check_ = False
        try:
            # ---Preallocate Potential and Current lists---#
            with open(myfile, "r", encoding="utf-8") as mydata:
                encoding = "utf-8"

        except:

            # ---Preallocate Potential and Current lists---#
            with open(myfile, "r", encoding="utf-16") as mydata:
                encoding = "utf-16"

        with open(myfile, "r", encoding=encoding) as mydata:

            for line in mydata:
                # delete any spaces that may come before the first value #
                check_split_list = line.split(cg.delimiter)
                while True:
                    if check_split_list[0] == "":
                        del check_split_list[0]
                    else:
                        break

                # delete any tabs that may come before the first value #
                while True:
                    if check_split_list[0] == " ":
                        del check_split_list[0]
                    else:
                        break

                check_split = check_split_list[0]
                check_split = check_split.replace(",", "")
                try:
                    check_split = float(check_split)
                    check_split = True
                except:
                    check_split = False

                if check_split:
                    cg.total_columns = len(check_split_list)
                    check_ = True
                    break

        if check_:
            cg.list_val = cg.current_column + (self.electrode - 1) * cg.spacing_index

            if cg.list_val > cg.total_columns:
                return False
            return True

        else:
            print("\nverify_multi: could not find a line\nthat began with an integer\n")
            return False

    def proceed(self):

        self.win.destroy()

        ##############################
        # Syncronization Classes ###
        ##############################
        cg.wait_time = WaitTime()
        cg.track = Track()

        ######################################################
        # Matplotlib Canvas, Figure, and Artist Creation ###
        ######################################################
        if cg.method == "Continuous Scan":
            cg.initialize = InitializeContinuousCanvas()

            #################################
            # Data Normalization Module ###
            #################################
            cg.data_normalization = DataNormalization()

            ############################
            # Post Analysis Module ###
            ############################
            cg.post_analysis = PostAnalysis(self.parent, self.controller)
            cg.ShowFrames[PostAnalysis] = cg.post_analysis
            cg.post_analysis.grid(row=0, column=0, sticky="nsew")

            ################################################
            # Initialize the RealTimeManipulationFrame ###
            ################################################
            frame = ContinuousScanManipulationFrame(cg.container, self)
            cg.ShowFrames[cg.method] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        elif cg.method == "Frequency Map":

            cg.initialize = InitializeFrequencyMapCanvas()

            ################################################
            # Initialize the RealTimeManipulationFrame ###
            ################################################
            frame = FrequencyMapManipulationFrame(cg.container, self)
            cg.ShowFrames[cg.method] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # ---When initliazed, raise the Start Page and the plot for electrode one---#
        self.show_frame(cg.method)  # raises the frame for real-time data manipulation
        self.show_plot(cg.PlotValues[0])  # raises the figure for electrode 1

    def stop(self):
        self.StopSearch = True
        self.win.destroy()

    # --- Function to switch between visualization frames ---#
    def show_plot(self, frame):
        frame.tkraise()

    def show_frame(self, cont):

        frame = cg.ShowFrames[cont]
        frame.tkraise()


# ------------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------------#


############################################################
# Frame displayed during experiment with widgets and   ###
# functions for Real-time Data Manipulation            ###
############################################################
class ContinuousScanManipulationFrame(tk.Frame):
    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)  # Initialize the frame

        #######################################
        #######################################
        # Pack the widgets into the frame ###
        #######################################
        #######################################

        # --- Display the file number ---#
        FileTitle = tk.Label(self, text="File Number", font=MEDIUM_FONT,)
        FileTitle.grid(row=0, column=0, padx=5, pady=5)
        cg.FileLabel = ttk.Label(self, text="1", font=LARGE_FONT, style="Fun.TButton")
        cg.FileLabel.grid(row=1, column=0, padx=5, pady=5)

        # --- Display the experiment duration as a function of the user-inputted
        # Sample Rate ---#
        SampleTitle = tk.Label(self, text="Experiment Time (h)", font=MEDIUM_FONT)
        SampleTitle.grid(row=0, column=1, padx=5, pady=5)
        cg.RealTimeSampleLabel = ttk.Label(self, text="0", style="Fun.TButton")
        cg.RealTimeSampleLabel.grid(row=1, column=1, padx=5, pady=5)

        # --- Real-time Normalization Variable ---#
        SetPointNormLabel = tk.Label(
            self, text="Set Normalization Point", font=MEDIUM_FONT
        )
        cg.NormalizationVar = tk.StringVar()
        NormString = str(3)
        cg.NormalizationVar.set(NormString)
        self.SetPointNorm = ttk.Entry(self, textvariable=cg.NormalizationVar, width=8)
        cg.SetPointNorm = self.SetPointNorm

        # --- Button to apply any changes to the normalization variable ---#
        NormalizeButton = ttk.Button(
            self,
            text="Apply Norm",
            command=self.RealTimeNormalization,  # was lambda
            width=10,
        )
        self.NormWarning = tk.Label(self, text="", fg="red", font=MEDIUM_FONT)
        cg.NormWarning = self.NormWarning

        if cg.InjectionVar:
            SetPointNormLabel.grid(row=2, column=0, pady=2, sticky="nsew")
            self.SetPointNorm.grid(row=3, column=0, pady=2, padx=2)
            NormalizeButton.grid(row=4, column=0, pady=2, padx=2)
            self.NormWarning.grid(row=5, column=0, pady=0)

        elif not cg.InjectionVar:
            SetPointNormLabel.grid(row=2, column=0, columnspan=4, pady=2, sticky="nsew")
            self.SetPointNorm.grid(row=3, column=0, columnspan=4, pady=2, padx=2)
            NormalizeButton.grid(row=4, column=0, columnspan=4, pady=2, padx=2)
            self.NormWarning.grid(row=5, column=0, columnspan=4, pady=0)

        # --- Real-time Injection tracking ---#
        SetInjectionLabel = tk.Label(self, text="Set Injection Range", font=MEDIUM_FONT)
        InjectionButton = ttk.Button(
            self,
            text="Apply Injection",
            command=self.RealTimeInjection,  # lambda
            width=10,
        )
        self.SetInjectionPoint = ttk.Entry(self, width=8)

        # If this is an injection experiment, grid the widgets ##
        if cg.InjectionVar:
            self.SetInjectionPoint.grid(row=3, column=1, pady=2, padx=5)
            InjectionButton.grid(row=4, column=1, pady=2, padx=2)
            SetInjectionLabel.grid(row=2, column=1, pady=2, sticky="nsew")

        row_value = 6
        if len(cg.frequency_list) > 1:

            self.FrequencyFrame = tk.Frame(self, relief="groove", bd=3)
            self.FrequencyFrame.grid(
                row=row_value, column=0, columnspan=4, pady=2, padx=3, ipady=2
            )

            # --- Drift Correction Title ---#
            self.KDM_title = tk.Label(
                self.FrequencyFrame, text="Drift Correction", font=LARGE_FONT
            )
            self.KDM_title.grid(row=0, column=0, columnspan=3, pady=1, padx=5)

            # --- High Frequency Selection for KDM and Ratiometric Analysis ---#
            self.HighFrequencyLabel = tk.Label(
                self.FrequencyFrame, text="High Frequency", font=MEDIUM_FONT
            )
            self.HighFrequencyLabel.grid(row=1, column=1, pady=5, padx=5)

            cg.HighFrequencyEntry = tk.Entry(self.FrequencyFrame, width=7)
            cg.HighFrequencyEntry.insert(tk.END, cg.HighFrequency)
            cg.HighFrequencyEntry.grid(row=2, column=1, padx=5)

            # --- Low Frequency Selection for KDM and Ratiometric Analysis ---#
            self.LowFrequencyLabel = tk.Label(
                self.FrequencyFrame, text="Low Frequency", font=MEDIUM_FONT
            )
            self.LowFrequencyLabel.grid(row=1, column=0, pady=5, padx=5)

            cg.LowFrequencyEntry = tk.Entry(self.FrequencyFrame, width=7)
            cg.LowFrequencyEntry.insert(tk.END, cg.LowFrequency)
            cg.LowFrequencyEntry.grid(row=2, column=0, padx=5)

            self.LowFrequencyOffsetLabel = tk.Label(
                self.FrequencyFrame, text="Low Frequency\n Offset", font=MEDIUM_FONT
            ).grid(row=3, column=0, pady=2, padx=2)
            self.LowFrequencyOffset = tk.Entry(self.FrequencyFrame, width=7)
            self.LowFrequencyOffset.insert(tk.END, cg.LowFrequencyOffset)
            self.LowFrequencyOffset.grid(row=4, column=0, padx=2, pady=2)

            self.LowFrequencySlopeLabel = tk.Label(
                self.FrequencyFrame,
                text="Low Frequency\n Slope Manipulation",
                font=MEDIUM_FONT,
            ).grid(row=3, column=1, pady=2, padx=2)
            self.LowFrequencySlope = tk.Entry(self.FrequencyFrame, width=7)
            self.LowFrequencySlope.insert(tk.END, cg.LowFrequencySlope)
            self.LowFrequencySlope.grid(row=4, column=1, padx=2, pady=2)

            self.ApplyFrequencies = ttk.Button(
                self.FrequencyFrame,
                text="Apply Frequencies",
                command=self.RealTimeKDM,  # lambda
            )
            self.ApplyFrequencies.grid(row=5, column=0, columnspan=4, pady=5, padx=5)

            row_value += 1

        #################################################
        # Nested Frame for Real-Time adjustment     ###
        # of voltammogram and polynomial regression ###
        #################################################

        RegressionFrame = tk.Frame(self, relief="groove", bd=5)
        RegressionFrame.grid(
            row=row_value, column=0, columnspan=4, pady=5, padx=5, ipadx=3, sticky="ns"
        )
        RegressionFrame.rowconfigure(0, weight=1)
        RegressionFrame.rowconfigure(1, weight=1)
        RegressionFrame.rowconfigure(2, weight=1)
        RegressionFrame.columnconfigure(0, weight=1)
        RegressionFrame.columnconfigure(1, weight=1)
        row_value += 1

        # --- Title ---#
        self.RegressionLabel = tk.Label(
            RegressionFrame, text="Real Time Analysis Manipulation", font=LARGE_FONT
        )
        self.RegressionLabel.grid(row=0, column=0, columnspan=4, pady=5, padx=5)

        ###################################################################
        # Real Time Manipulation of Savitzky-Golay Smoothing Function ###
        ###################################################################
        self.SmoothingLabel = tk.Label(
            RegressionFrame, text="Savitzky-Golay Window (mV)", font=LARGE_FONT
        )
        self.SmoothingLabel.grid(row=1, column=0, columnspan=4, pady=1)
        self.SmoothingEntry = tk.Entry(RegressionFrame, width=10)
        self.SmoothingEntry.grid(row=2, column=0, columnspan=4, pady=3)
        self.SmoothingEntry.insert(tk.END, cg.sg_window)

        # --- Check for the presence of high and low frequencies ---#
        if cg.frequency_list[-1] > cutoff_frequency:
            self.High = True
        else:
            self.High = False

        if cg.frequency_list[0] <= cutoff_frequency:
            self.Low = True
        else:
            self.Low = False

        ##########################################################
        # If a frequency <= cutoff_frequency exists, grid    ###
        # a frame for low frequency data manipulation        ###
        ##########################################################
        if self.Low is True:
            LowParameterFrame = tk.Frame(RegressionFrame)
            LowParameterFrame.grid(row=3, column=0, columnspan=4, sticky="nsew")
            LowParameterFrame.rowconfigure(0, weight=1)
            LowParameterFrame.rowconfigure(1, weight=1)
            LowParameterFrame.rowconfigure(2, weight=1)
            LowParameterFrame.columnconfigure(0, weight=1)
            LowParameterFrame.columnconfigure(1, weight=1)
            cg.ShowFrames["LowParameterFrame"] = LowParameterFrame

            # --- points discarded at the beginning of the voltammogram, xstart ---#
            self.low_xstart_label = tk.Label(
                LowParameterFrame, text="xstart (V)", font=MEDIUM_FONT
            ).grid(row=0, column=0)
            self.low_xstart_entry = tk.Entry(LowParameterFrame, width=7)
            self.low_xstart_entry.insert(tk.END, str(cg.low_xstart))
            self.low_xstart_entry.grid(row=1, column=0)
            cg.low_xstart_entry = self.low_xstart_entry

            # --- points discarded at the beginning of the voltammogram, xend ---#
            self.low_xend_label = tk.Label(
                LowParameterFrame, text="xend (V)", font=MEDIUM_FONT
            ).grid(row=0, column=1)
            self.low_xend_entry = tk.Entry(LowParameterFrame, width=7)
            self.low_xend_entry.insert(tk.END, str(cg.low_xend))
            self.low_xend_entry.grid(row=1, column=1)
            cg.low_xend_entry = self.low_xend_entry

        #########################################################
        # If a frequency > cutoff_frequency exists, grid    ###
        # a frame for high frequency data manipulation      ###
        #########################################################
        if self.High is True:
            HighParameterFrame = tk.Frame(RegressionFrame)
            HighParameterFrame.grid(row=3, column=0, columnspan=4, sticky="nsew")
            HighParameterFrame.rowconfigure(0, weight=1)
            HighParameterFrame.rowconfigure(1, weight=1)
            HighParameterFrame.rowconfigure(2, weight=1)
            HighParameterFrame.columnconfigure(0, weight=1)
            HighParameterFrame.columnconfigure(1, weight=1)
            cg.ShowFrames["HighParameterFrame"] = HighParameterFrame

            # --- points discarded at the beginning of the voltammogram, xstart ---#
            self.high_xstart_label = tk.Label(
                HighParameterFrame, text="xstart (V)", font=MEDIUM_FONT
            ).grid(row=0, column=0)
            self.high_xstart_entry = tk.Entry(HighParameterFrame, width=7)
            self.high_xstart_entry.insert(tk.END, str(cg.high_xstart))
            self.high_xstart_entry.grid(row=1, column=0)
            cg.high_xstart_entry = self.high_xstart_entry

            # --- points discarded at the beginning of the voltammogram, xend ---#
            self.high_xend_label = tk.Label(
                HighParameterFrame, text="xend (V)", font=MEDIUM_FONT
            ).grid(row=0, column=1)
            self.high_xend_entry = tk.Entry(HighParameterFrame, width=7)
            self.high_xend_entry.insert(tk.END, str(cg.high_xend))
            self.high_xend_entry.grid(row=1, column=1)
            cg.high_xend_entry = self.high_xend_entry

        ############################################################
        # If both high and low frequencies are being analyzed, ###
        # create buttons to switch between the two             ###
        ############################################################
        if self.High is True:
            if self.Low is True:
                self.SelectLowParameters = ttk.Button(
                    RegressionFrame,
                    style="Off.TButton",
                    text="f <= %dHz" % cutoff_frequency,
                    command=lambda: self.show_frame("LowParameterFrame"),
                )
                self.SelectLowParameters.grid(row=4, column=0, pady=5, padx=5)

                self.SelectHighParameters = ttk.Button(
                    RegressionFrame,
                    style="On.TButton",
                    text="f > %dHz" % cutoff_frequency,
                    command=lambda: self.show_frame("HighParameterFrame"),
                )
                self.SelectHighParameters.grid(row=4, column=1, pady=5, padx=5)

        # --- Button to apply adjustments ---#
        self.AdjustParameterButton = tk.Button(
            RegressionFrame,
            text="Apply Adjustments",
            font=LARGE_FONT,
            command=self.AdjustParameters,  # lambda
        )
        self.AdjustParameterButton.grid(row=5, column=0, columnspan=4, pady=10, padx=10)

        # ---Buttons to switch between electrode frames---#
        frame_value = 0
        column_value = 0
        for value in cg.PlotValues:
            Button = ttk.Button(
                self,
                text=cg.frame_list[frame_value],
                command=lambda frame_value=frame_value: self.show_plot(
                    cg.PlotValues[frame_value]
                ),
            )
            Button.grid(row=row_value, column=column_value, pady=2, padx=5)

            # allows .grid() to alternate between
            # packing into column 1 and column 2
            if column_value == 1:
                column_value = 0
                row_value += 1

            # if gridding into the 1st column,
            # grid the next into the 2nd column
            else:
                column_value += 1
            frame_value += 1
        row_value += 1

        # --- Start ---#
        StartButton = ttk.Button(
            self, text="Start", style="Fun.TButton", command=self.SkeletonKey  # lambda
        )
        StartButton.grid(row=row_value, column=0, pady=5, padx=5)

        # --- Reset ---#
        Reset = ttk.Button(
            self, text="Reset", style="Fun.TButton", command=self.Reset  # lambda
        )
        Reset.grid(row=row_value, column=1, pady=5, padx=5)
        row_value += 1

        # --- Quit ---#
        QuitButton = ttk.Button(self, text="Quit Program", command=quit)  # lambda
        QuitButton.grid(row=row_value, column=0, columnspan=4, pady=5)

        for row in range(row_value):
            row += 1
            self.rowconfigure(row, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        ###################################################
        ###################################################
        # Real Time Data Manipulation Functions ######
        ###################################################
        ###################################################

    #####################################
    # Manipulation of the Injection ###
    # Point for visualization       ###
    #####################################
    def RealTimeInjection(self):

        cg.InjectionPoint = int(self.SetInjectionPoint.get())

        print("\nNew Injection Point: %s\n" % str(cg.InjectionPoint))

    #################################################
    # Adjustment of points discarded at the     ###
    # beginning and end of Regression Analysis  ###
    #################################################
    def AdjustParameters(self):

        ###############################################
        # Polynomical Regression Range Parameters ###
        ###############################################

        if self.Low:

            # --- parameters for frequencies equal or below cutoff_frequency ---#
            cg.low_xstart = float(
                self.low_xstart_entry.get()
            )  # xstart/xend adjust the points at the start and end of the
            # voltammogram/smoothed currents, respectively
            cg.low_xend = float(self.low_xend_entry.get())

        if self.High:

            # --- parameters for frequencies above cutoff_frequency ---#
            cg.high_xstart = float(self.high_xstart_entry.get())
            cg.high_xend = float(self.high_xend_entry.get())

        #######################################
        # Savitzky-Golay Smoothing Window ###
        #######################################
        cg.sg_window = float(self.SmoothingEntry.get())
        print("\n\n\nAdjustParamaters: SG_Window (mV) %d\n\n\n" % cg.sg_window)

    #########################################################
    # Real-time adjustment of High and Low frequencies  ###
    # used for KDM and ratiometric analysis             ###
    #########################################################
    def RealTimeKDM(self):

        TempHighFrequency = int(cg.HighFrequencyEntry.get())
        TempLowFrequency = int(cg.LowFrequencyEntry.get())

        cg.LowFrequencyOffset = float(self.LowFrequencyOffset.get())
        cg.LowFrequencySlope = float(self.LowFrequencySlope.get())

        # --- Reset the variable for the Warning Label (WrongFrequencyLabel) ---#
        CheckVar = 0

        if int(cg.HighFrequency) not in cg.frequency_list:
            CheckVar += 3

        if int(cg.LowFrequency) not in cg.frequency_list:
            CheckVar += 1

        # --- if only the HighFrequency does not exist ---#
        if CheckVar == 3:
            if cg.ExistVar:
                cg.WrongFrequencyLabel.grid_forget()
            cg.WrongFrequencyLabel = tk.Label(
                self.FrequencyFrame, text="High Frequency Does Not Exist", fg="red"
            )
            cg.WrongFrequencyLabel.grid(row=6, column=0, columnspan=4)
            if not cg.ExistVar:
                cg.ExistVar = True

        # --- if only the LowFrequency does not exist ---#
        elif CheckVar == 1:
            if cg.ExistVar:
                cg.WrongFrequencyLabel.grid_forget()
            cg.WrongFrequencyLabel = tk.Label(
                self.FrequencyFrame, text="Low Frequency Does Not Exist", fg="red"
            )
            cg.WrongFrequencyLabel.grid(row=6, column=0, columnspan=4)
            if not cg.ExistVar:
                cg.ExistVar = True

        # --- if both the HighFrequency and LowFrequency do not exist ---#
        elif CheckVar == 4:
            if cg.ExistVar:
                cg.WrongFrequencyLabel.grid_forget()
            cg.WrongFrequencyLabel = tk.Label(
                self.FrequencyFrame,
                text="High and Low Frequencies Do Not Exist",
                fg="red",
            )
            cg.WrongFrequencyLabel.grid(row=6, column=0, columnspan=4)
            if not cg.ExistVar:
                cg.ExistVar = True

        # --- else, if they both exist, remove the warning label ---#
        else:
            cg.HighLowList["High"] = TempHighFrequency
            cg.HighLowList["Low"] = TempLowFrequency

            cg.data_normalization.ResetRatiometricData()

            # --- if a warning label exists, forget it ---#
            if cg.ExistVar:
                cg.WrongFrequencyLabel.grid_forget()

            # --- Tells RawVoltammogramVisualization to revisualize data for new
            # High and Low frequencies ---#
            if not cg.RatioMetricCheck:
                cg.RatioMetricCheck = True

            if cg.analysis_complete:
                cg.post_analysis._adjust_data()

    # --- Function for Real-time Normalization ---#
    def RealTimeNormalization(self):

        cg.NormalizationPoint = int(self.SetPointNorm.get())
        file = int(cg.FileLabel["text"])
        index = file - 1

        if file >= cg.NormalizationPoint:
            cg.wait_time.NormalizationWaitTime()

        elif cg.NormalizationPoint > file:
            cg.NormWarning["fg"] = "red"
            cg.NormWarning["text"] = "File %s has \nnot been analyzed" % str(
                cg.NormalizationPoint
            )

        if cg.analysis_complete:
            cg.post_analysis._adjust_data()

    ########################################################
    # Function to Reset and raise the user input frame ###
    ########################################################
    def Reset(self):

        cg.key = 0
        cg.PoisonPill = True
        cg.AlreadyInitiated = False  # reset the start variable

        if self.High:
            cg.HighAlreadyReset = True

        if self.Low:
            cg.LowAlreadyReset = True

        # Raise the initial user input frame
        self.show_frame(InputFrame)
        self.close_frame(cg.method)

        cg.post_analysis._reset()

        # Take resize weight away from the Visualization Canvas
        cg.container.columnconfigure(1, weight=0)

        cg.analysis_complete = False

    ##########################################################
    # Function to raise frame to the front of the canvas ###
    ##########################################################
    def show_frame(self, cont):

        frame = cg.ShowFrames[cont]  # Key: frame handle / Value: tk.Frame object
        frame.tkraise()  # raise the frame objext

        if cont == "LowParameterFrame":
            self.SelectLowParameters["style"] = "On.TButton"
            self.SelectHighParameters["style"] = "Off.TButton"

        elif cont == "HighParameterFrame":
            self.SelectLowParameters["style"] = "Off.TButton"
            self.SelectHighParameters["style"] = "On.TButton"

    ###################################################
    # Function to start returning visualized data ###
    ###################################################
    def SkeletonKey(self):

        if not cg.AlreadyInitiated:

            ######################################################################
            # Initialize Animation (Visualization) for each electrode figure ###
            ######################################################################
            fig_count = 0  # index value for the frame
            for figure in cg.figures:
                fig, self.ax = figure
                electrode = cg.electrode_list[fig_count]
                cg.anim.append(
                    ElectrochemicalAnimation(
                        fig, electrode, resize_interval=cg.resize_interval, fargs=None
                    )
                )
                fig_count += 1

            cg.AlreadyInitiated = True

            # --- reset poison pill variables --#
            cg.PoisonPill = False

            if cg.key == 0:  # tells Generate() to start data analysis
                cg.key += 100
        else:
            print("\n\nProgram has already been initiaed\n\n")

    ######################################################
    # Function to raise frame for specific electrode ###
    ######################################################
    def show_plot(self, frame):
        frame.tkraise()

    #####################################
    # Destory the frames on Reset() ###
    #####################################
    def close_frame(self, cont):
        frame = cg.ShowFrames[cont]
        frame.grid_forget()

        # close all matplotlib figures
        plt.close("all")

        # destory the frames holding the figures
        for frame in cg.PlotValues:
            frame.destroy()

        # destory the container holding those frames
        cg.PlotContainer.destroy()


############################################################
# Frame displayed during experiment with widgets and   ###
# functions for Real-time Data Manipulation            ###
############################################################
class FrequencyMapManipulationFrame(tk.Frame):
    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)  # Initialize the frame

        #######################################
        #######################################
        # Pack the widgets into the frame ###
        #######################################
        #######################################

        #################################################
        # Nested Frame for Real-Time adjustment     ###
        # of voltammogram, polynomial regression,   ###
        # and savitzky-golay Smoothing              ###
        #################################################

        RegressionFrame = tk.Frame(self, relief="groove", bd=5)
        RegressionFrame.grid(
            row=7, column=0, columnspan=4, pady=5, padx=5, ipadx=3, sticky="ns"
        )
        RegressionFrame.rowconfigure(0, weight=1)
        RegressionFrame.rowconfigure(1, weight=1)
        RegressionFrame.rowconfigure(2, weight=1)
        RegressionFrame.columnconfigure(0, weight=1)
        RegressionFrame.columnconfigure(1, weight=1)

        # --- Title ---#
        self.RegressionLabel = tk.Label(
            RegressionFrame, text="Real Time Analysis Manipulation", font=LARGE_FONT
        )
        self.RegressionLabel.grid(row=0, column=0, columnspan=4, pady=5, padx=5)

        ###################################################################
        # Real Time Manipulation of Savitzky-Golay Smoothing Function ###
        ###################################################################
        self.SmoothingLabel = tk.Label(
            RegressionFrame, text="Savitzky-Golay Window (mV)", font=LARGE_FONT
        )
        self.SmoothingLabel.grid(row=1, column=0, columnspan=4, pady=1)
        self.SmoothingEntry = tk.Entry(RegressionFrame, width=10)
        self.SmoothingEntry.grid(row=2, column=0, columnspan=4, pady=3)
        self.SmoothingEntry.insert(tk.END, cg.sg_window)

        # --- Check for the presence of high and low frequencies ---#
        if cg.frequency_list[-1] > 50:
            self.High = True
        else:
            self.High = False
        if cg.frequency_list[0] <= 50:
            self.Low = True
        else:
            self.Low = False
        ###################################################
        # If a frequency <= 50Hz exists, grid a frame ###
        # for low frequency data manipulation         ###
        ###################################################
        if self.Low is True:
            LowParameterFrame = tk.Frame(RegressionFrame)
            LowParameterFrame.grid(row=3, column=0, columnspan=4, sticky="nsew")
            LowParameterFrame.rowconfigure(0, weight=1)
            LowParameterFrame.rowconfigure(1, weight=1)
            LowParameterFrame.rowconfigure(2, weight=1)
            LowParameterFrame.columnconfigure(0, weight=1)
            LowParameterFrame.columnconfigure(1, weight=1)
            cg.ShowFrames["LowParameterFrame"] = LowParameterFrame

            # --- points discarded at the beginning of the voltammogram, xstart ---#
            self.low_xstart_label = tk.Label(
                LowParameterFrame, text="xstart (V)", font=MEDIUM_FONT
            ).grid(row=0, column=0)
            self.low_xstart_entry = tk.Entry(LowParameterFrame, width=7)
            self.low_xstart_entry.insert(tk.END, str(cg.low_xstart))
            self.low_xstart_entry.grid(row=1, column=0)
            cg.low_xstart_entry = self.low_xstart_entry

            # --- points discarded at the beginning of the voltammogram, xend ---#
            self.low_xend_label = tk.Label(
                LowParameterFrame, text="xend (V)", font=MEDIUM_FONT
            ).grid(row=0, column=1)
            self.low_xend_entry = tk.Entry(LowParameterFrame, width=7)
            self.low_xend_entry.insert(tk.END, str(cg.low_xend))
            self.low_xend_entry.grid(row=1, column=1)
            cg.low_xend_entry = self.low_xend_entry

        ##################################################
        # If a frequency > 50Hz exists, grid a frame ###
        # for high frequency data manipulation       ###
        ##################################################
        if self.High is True:
            HighParameterFrame = tk.Frame(RegressionFrame)
            HighParameterFrame.grid(row=3, column=0, columnspan=4, sticky="nsew")
            HighParameterFrame.rowconfigure(0, weight=1)
            HighParameterFrame.rowconfigure(1, weight=1)
            HighParameterFrame.rowconfigure(2, weight=1)
            HighParameterFrame.columnconfigure(0, weight=1)
            HighParameterFrame.columnconfigure(1, weight=1)
            cg.ShowFrames["HighParameterFrame"] = HighParameterFrame

            # --- points discarded at the beginning of the voltammogram, xstart ---#
            self.high_xstart_label = tk.Label(
                HighParameterFrame, text="xstart (V)", font=MEDIUM_FONT
            ).grid(row=0, column=0)
            self.high_xstart_entry = tk.Entry(HighParameterFrame, width=7)
            self.high_xstart_entry.insert(tk.END, str(cg.high_xstart))
            self.high_xstart_entry.grid(row=1, column=0)
            cg.high_xstart_entry = self.high_xstart_entry

            # --- points discarded at the beginning of the voltammogram, xend ---#
            self.high_xend_label = tk.Label(
                HighParameterFrame, text="xend (V)", font=MEDIUM_FONT
            ).grid(row=0, column=1)
            self.high_xend_entry = tk.Entry(HighParameterFrame, width=7)
            self.high_xend_entry.insert(tk.END, str(cg.high_xend))
            self.high_xend_entry.grid(row=1, column=1)
            cg.high_xend_entry = self.high_xend_entry

        ############################################################
        # If both high and low frequencies are being analyzed, ###
        # create buttons to switch between the two             ###
        ############################################################
        if self.High is True:
            if self.Low is True:
                self.SelectLowParameters = ttk.Button(
                    RegressionFrame,
                    style="Off.TButton",
                    text="f <= 50Hz",
                    command=lambda: self.show_frame("LowParameterFrame"),
                )
                self.SelectLowParameters.grid(row=4, column=0, pady=5, padx=5)

                self.SelectHighParameters = ttk.Button(
                    RegressionFrame,
                    style="On.TButton",
                    text="f > 50Hz",
                    command=lambda: self.show_frame("HighParameterFrame"),
                )
                self.SelectHighParameters.grid(row=4, column=1, pady=5, padx=5)

        # --- Button to apply adjustments ---#
        self.AdjustParameterButton = tk.Button(
            RegressionFrame,
            text="Apply Adjustments",
            font=LARGE_FONT,
            command=self.AdjustParameters,  # was lambda
        )
        self.AdjustParameterButton.grid(row=5, column=0, columnspan=4, pady=10, padx=10)

        # ---Buttons to switch between electrode frames---#
        frame_value = 0
        row_value = 8
        column_value = 0
        for value in cg.PlotValues:
            Button = ttk.Button(
                self,
                text=cg.frame_list[frame_value],
                command=lambda frame_value=frame_value: self.show_plot(
                    cg.PlotValues[frame_value]
                ),
            )
            Button.grid(row=row_value, column=column_value, pady=2, padx=5)

            # allows .grid() to alternate between
            # packing into column 1 and column 2
            if column_value == 1:
                column_value = 0
                row_value += 1

            # if gridding into the 1st column,
            # grid the next into the 2nd column
            else:
                column_value += 1
            frame_value += 1
        row_value += 1

        # --- Start ---#
        StartButton = ttk.Button(
            self,
            text="Start",
            style="Fun.TButton",
            command=self.SkeletonKey,  # was lambda
        )
        StartButton.grid(row=row_value, column=0, pady=5, padx=5)

        # --- Reset ---#
        Reset = ttk.Button(
            self, text="Reset", style="Fun.TButton", command=self.Reset  # was lambda
        )
        Reset.grid(row=row_value, column=1, pady=5, padx=5)
        row_value += 1

        # --- Quit ---#
        QuitButton = ttk.Button(self, text="Quit Program", command=quit)  # was lambda
        QuitButton.grid(row=row_value, column=0, columnspan=4, pady=5)

        for row in range(row_value):
            row += 1
            self.rowconfigure(row, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        ###################################################
        ###################################################
        # Real Time Data Manipulation Functions ######
        ###################################################
        ###################################################

    #################################################
    # Adjustment of points discarded at the     ###
    # beginning and end of Regression Analysis  ###
    #################################################
    def AdjustParameters(self):
        # --- Adjusts the parameters used to visualize the raw voltammogram,
        # smoothed currents, and polynomial fit

        ###############################################
        # Polynomical Regression Range Parameters ###
        ###############################################

        if self.Low:
            # --- parameters for frequencies equal or below 50Hz ---#
            cg.low_xstart = float(
                self.low_xstart_entry.get()
            )  # xstart/xend adjust the points at the start and end of the
            # voltammogram/smoothed currents, respectively
            cg.low_xend = float(self.low_xend_entry.get())
        if self.High:
            # --- parameters for frequencies above 50Hz ---#
            cg.high_xstart = float(self.high_xstart_entry.get())
            cg.high_xend = float(self.high_xend_entry.get())

        #######################################
        # Savitzky-Golay Smoothing Window ###
        #######################################
        cg.sg_window = float(self.SmoothingEntry.get())
        print("\n\n\nAdjustParamaters: SG_Window (mV) %d\n\n\n" % cg.sg_window)

    ########################################################
    # Function to Reset and raise the user input frame ###
    ########################################################
    def Reset(self):

        cg.key = 0
        cg.PoisonPill = True
        cg.AlreadyInitiated = False  # reset the start variable
        cg.AlreadyReset = True

        # Raise the initial user input frame
        self.show_frame(InputFrame)
        self.close_frame(cg.method)

    ##########################################################
    # Function to raise frame to the front of the canvas ###
    ##########################################################
    def show_frame(self, cont):

        frame = cg.ShowFrames[cont]  # Key: frame handle / Value: tk.Frame object
        frame.tkraise()  # raise the frame objext

        if cont == "LowParameterFrame":
            self.SelectLowParameters["style"] = "On.TButton"
            self.SelectHighParameters["style"] = "Off.TButton"

        elif cont == "HighParameterFrame":
            self.SelectLowParameters["style"] = "Off.TButton"
            self.SelectHighParameters["style"] = "On.TButton"

    ###################################################
    # Function to start returning visualized data ###
    ###################################################
    def SkeletonKey(self):

        if not cg.AlreadyInitiated:

            ######################################################################
            # Initialize Animation (Visualization) for each electrode figure ###
            ######################################################################
            fig_count = 0  # index value for the frame
            for figure in cg.figures:
                fig, self.ax = figure
                electrode = cg.electrode_list[fig_count]
                cg.anim.append(
                    ElectrochemicalAnimation(
                        fig, electrode, resize_interval=None, fargs=None
                    )
                )
                fig_count += 1

            cg.AlreadyInitiated = True

            # --- reset poison pill variables --#
            cg.PoisonPill = False

            if cg.key == 0:  # tells Generate() to start data analysis
                cg.key += 100
        else:
            print("\n\nProgram has already been initiaed\n\n")

    ######################################################
    # Function to raise frame for specific electrode ###
    ######################################################
    def show_plot(self, frame):
        frame.tkraise()

    #####################################
    # Destory the frames on Reset() ###
    #####################################
    def close_frame(self, cont):
        frame = cg.ShowFrames[cont]
        frame.grid_forget()

        for value in cg.PlotValues:
            value.destroy()

        cg.PlotContainer.destroy()


# ------------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------------#


#########################################################
# Electrode Frame Class for data visualization      ###
# displayed next to the RealTimeManipulationFrame   ###
#                                                   ###
#    Embeds a canvas within the tkinter             ###
#    MainWindow containing figures that             ###
#    visualize the data for that electrode          ###
#########################################################


class ContinuousScanVisualizationFrame(tk.Frame):
    def __init__(self, electrode, count, parent, controller):

        tk.Frame.__init__(self, parent)

        # --- for resize ---#
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=2)

        ElectrodeLabel = tk.Label(self, text="%s" % electrode, font=HUGE_FONT)
        ElectrodeLabel.grid(row=0, column=0, pady=5, sticky="n")

        cg.FrameFileLabel = tk.Label(self, text="", font=MEDIUM_FONT)
        cg.FrameFileLabel.grid(row=0, column=1, pady=3, sticky="ne")

        # --- Voltammogram, Raw Peak Height, and Normalized Figure and Artists ---#
        fig, ax = cg.figures[count]  # Call the figure and artists for the electrode
        canvas = FigureCanvasTkAgg(fig, self)  # and place the artists within the frame
        canvas.draw()  # initial draw call to create the artists that will be blitted
        canvas.get_tk_widget().grid(
            row=1, columnspan=2, pady=6, ipady=5, sticky="news"
        )  # does not affect size of figure within plot container

        if len(cg.frequency_list) > 1:
            # --- Ratiometric Figure and Artists ---#
            fig, ax = cg.ratiometric_figures[
                count
            ]  # Call the figure and artists for the electrode
            canvas = FigureCanvasTkAgg(
                fig, self
            )  # and place the artists within the frame
            canvas.draw()
            canvas.get_tk_widget().grid(
                row=2, columnspan=2, pady=6, ipady=5, sticky="sew"
            )  # does not affect size of figure within plot container

            # --- add weight to the second row for resizing ---#
            self.rowconfigure(2, weight=2)


class FrequencyMapVisualizationFrame(tk.Frame):
    def __init__(self, electrode, count, parent, controller):

        tk.Frame.__init__(self, parent)

        # --- for resize ---#
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=2)

        ElectrodeLabel = tk.Label(self, text="%s" % electrode, font=HUGE_FONT)
        ElectrodeLabel.grid(row=0, column=0, pady=5, sticky="n")

        cg.FrameFileLabel = tk.Label(self, text="", font=MEDIUM_FONT)
        cg.FrameFileLabel.grid(row=0, column=1, pady=3, sticky="ne")

        # --- Voltammogram, Raw Peak Height, and Normalized Figure and Artists ---#
        fig, ax = cg.figures[count]  # Call the figure and artists for the electrode
        canvas = FigureCanvasTkAgg(fig, self)  # and place the artists within the frame
        canvas.draw()  # initial draw call to create the artists that will be blitted
        canvas.get_tk_widget().grid(
            row=1, columnspan=2, pady=6, ipady=5, sticky="news"
        )  # does not affect size of figure within plot container

        #############################################################
        #############################################################
        #                   End of GUI Classes                  ###
        #############################################################
        #############################################################


# ------------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------------#

#############################################################
#############################################################
# Creation of Matplotlib Canvas, Figures, Axes, Artists ###
# and all other decorators (e.g. axis labels, titles)   ###
#############################################################
#############################################################


class InitializeContinuousCanvas:
    def __init__(self):

        ##############################################
        # Generate global lists for data storage ###
        ##############################################

        self.length = len(cg.frequency_list)
        cg.electrode_count = int(cg.electrode_count)

        # --- Animation list ---#
        cg.anim = []

        # --- Figure lists ---#
        cg.figures = []
        cg.ratiometric_figures = []

        ############################################
        # Create global lists for data storage ###
        ############################################
        cg.data_list = [0] * cg.electrode_count  # Peak Height/AUC data (after smoothing
        # and polynomial regression)
        avg_data_list = (
            []
        )  # Average Peak Height/AUC across all electrodes for each frequency
        std_data_list = []  # standard deviation between electrodes for each frequency
        cg.normalized_data_list = [0] * cg.electrode_count  # normalized data
        cg.offset_normalized_data_list = [
            0
        ] * cg.electrode_count  # to hold data with low frequency offset
        cg.normalized_ratiometric_data_list = []  # ratio of normalized peak heights
        cg.KDM_list = []  # hold the data for kinetic differential measurements

        for num in range(cg.electrode_count):
            cg.data_list[num] = [0] * self.length  # a data list for each eletrode
            cg.normalized_data_list[num] = [0] * self.length
            cg.offset_normalized_data_list[num] = [0] * cg.numFiles
            for count in range(
                self.length
            ):  # a data list for each frequency for that electrode
                cg.data_list[num][count] = [
                    0
                ] * cg.numFiles  # use [0]*numFiles to preallocate list space
                cg.normalized_data_list[num][count] = [0] * cg.numFiles

        for num in range(cg.electrode_count):
            cg.normalized_ratiometric_data_list.append([])
            cg.KDM_list.append([])

        # --- Lists of Frames and Artists ---#
        cg.plot_list = []
        cg.ratiometric_plots = []
        cg.empty_ratiometric_plots = []
        cg.frame_list = []

        # --- Misc Lists ---#
        cg.file_list = []  # Used for len(file_list)
        cg.sample_list = []  # For plotting Peak Height vs. sample rate

        ######################################################
        # Create a figure and artists for each electrode ###
        ######################################################
        for num in range(cg.electrode_count):
            electrode = cg.electrode_list[num]
            figure = self.MakeFigure(electrode)
            cg.figures.append(figure)

            if len(cg.frequency_list) > 1:
                ratio_figure = self.MakeRatiometricFigure(electrode)
                cg.ratiometric_figures.append(ratio_figure)

        #####################################################
        # Create a frame for each electrode and embed   ###
        # within it the figure containing its artists   ###
        #####################################################

        cg.PlotFrames = {}  # Dictionary of frames for each electrode
        cg.PlotValues = []  # create a list of frames

        # --- Create a container that can be created and destroyed when Start()
        # or Reset() is called, respectively ---#
        cg.PlotContainer = tk.Frame(cg.container, relief="groove", bd=3)
        cg.PlotContainer.grid(row=0, column=1, sticky="nsew")
        cg.PlotContainer.rowconfigure(0, weight=1)
        cg.PlotContainer.columnconfigure(0, weight=1)

        frame_count = 0
        FileLabelList = []
        for (
            electrode_frame
        ) in cg.frame_list:  # Iterate through the frame of each electrode

            # --- create an instance of the frame and append it to the global
            # frame dictionary ---#
            cg.FrameReference = ContinuousScanVisualizationFrame(
                electrode_frame, frame_count, cg.PlotContainer, self
            )  # PlotContainer is the 'parent' frame
            cg.FrameReference.grid(
                row=0, column=0, sticky="nsew"
            )  # sticky must be 'nsew' so it expands and contracts with resize
            cg.PlotFrames[electrode_frame] = cg.FrameReference

            frame_count += 1

        # --- Create a list containing the Frame objects for each electrode ---#
        for reference, frame in cg.PlotFrames.items():
            cg.PlotValues.append(frame)

        #################################
        # Initiate .txt File Export ###
        #################################

        # --- If the user has indicated that text file export should be activated ---#
        if cg.SaveVar:
            print("Initializing Text File Export")
            cg.text_file_export = TextFileExport()

        else:
            cg.text_file_export = None
            print("Text File Export Deactivated")

    ############################################
    # Create the figure and artist objects ###
    ############################################
    def MakeFigure(self, electrode):

        print("Make Figure: Continuous Scan")
        try:
            ########################
            # Setup the Figure ###
            ########################
            length = self.length
            fig, ax = plt.subplots(
                nrows=3, ncols=length, squeeze=False, figsize=(9, 4.5)
            )  # figsize=(width, height)
            plt.subplots_adjust(
                bottom=0.1, hspace=0.6, wspace=0.3
            )  # adjust the spacing between subplots

            # changing the column index
            # ---Set the electrode index value---#
            if cg.e_var == "single":
                cg.list_val = (
                    cg.current_column_index + (electrode - 1) * cg.spacing_index
                )
                # changing
            elif cg.e_var == "multiple":
                cg.list_val = cg.current_column_index

            #######################
            # Set axis labels ###
            #######################

            ax[0, 0].set_ylabel("Current\n(µA)", fontweight="bold")
            if cg.SelectedOptions == "Peak Height Extraction":
                ax[1, 0].set_ylabel("Peak Height\n(µA)", fontweight="bold")
            elif cg.SelectedOptions == "Area Under the Curve":
                ax[1, 0].set_ylabel("AUC (a.u.)", fontweight="bold")
            ax[2, 0].set_ylabel("Normalized", fontweight="bold")

            ##########################################
            # Set suplot axes for each frequency ###
            ##########################################
            electrode_plot = []
            subplot_count = 0
            for freq in range(length):
                frequency = cg.frequency_list[freq]
                ax[0, subplot_count].set_xlabel("Potential (V)")

                # --- if the resize interval is larger than the number of files, ---#
                # --- make the x lim the number of files (& vice versa)          ---#
                if cg.resize_interval > cg.numFiles:
                    xlim_factor = cg.numFiles
                elif cg.resize_interval is None:
                    xlim_factor = cg.numFiles
                elif cg.resize_interval <= cg.numFiles:
                    xlim_factor = cg.resize_interval

                if cg.XaxisOptions == "Experiment Time":
                    ax[1, subplot_count].set_xlim(
                        0, (xlim_factor * cg.SampleRate) / 3600 + (cg.SampleRate / 7200)
                    )
                    ax[2, subplot_count].set_xlim(
                        0, (xlim_factor * cg.SampleRate) / 3600 + (cg.SampleRate / 7200)
                    )
                    ax[2, subplot_count].set_xlabel("Time (h)")

                elif cg.XaxisOptions == "File Number":
                    ax[1, subplot_count].set_xlim(-0.05, xlim_factor + 0.1)
                    ax[2, subplot_count].set_xlim(-0.05, xlim_factor + 0.1)
                    ax[2, subplot_count].set_xlabel("File Number")

                #######################################################################
                #######################################################################
                #       Analyze the first file and create the Y limits of the subplots
                #               depending on the data range of the first file
                ######################################################################
                self.InitializeSubplots(ax, frequency, electrode, subplot_count)

                ######################################################################
                ######################################################################

                # ---Set Subplot Title---#
                frequency = str(frequency)
                ax[0, subplot_count].set_title(
                    "".join(frequency + " Hz"), fontweight="bold"
                )

                # ---Initiate the subplots---#
                # this assigns a Line2D artist object to the artist object (Axes)
                (smooth,) = ax[0, subplot_count].plot([], [], "ko", Markersize=2)
                (regress,) = ax[0, subplot_count].plot([], [], "r-")
                (linear,) = ax[0, subplot_count].plot([], [], "r-")

                (peak,) = ax[1, subplot_count].plot([], [], "ko", MarkerSize=1)
                (peak_injection,) = ax[1, subplot_count].plot(
                    [], [], "bo", MarkerSize=1
                )
                (normalization,) = ax[2, subplot_count].plot([], [], "ko", markersize=1)
                (norm_injection,) = ax[2, subplot_count].plot(
                    [], [], "ro", markersize=1
                )

                # --- shading for AUC ---#
                verts = [(0, 0), *zip([], []), (0, 0)]
                poly = Polygon(verts, alpha=0.5)
                ax[0, subplot_count].add_patch(poly)

                #####################################################
                # Create a list of the primitive artists        ###
                # (Line2D objects) that will be returned        ###
                # to ElectrochemicalAnimation to be visualized  ###
                #####################################################

                # this is the list that will be returned as _drawn_artists
                # to the Funcanimation class
                plots = [
                    smooth,
                    regress,
                    peak,
                    peak_injection,
                    normalization,
                    norm_injection,
                    poly,
                    linear,
                ]

                # --- And append that list to keep a global reference ---#
                electrode_plot.append(
                    plots
                )  # 'plots' is a list of artists that are passed to animate
                electrode_frame = "Electrode %s" % str(electrode)
                if electrode_frame not in cg.frame_list:
                    cg.frame_list.append(electrode_frame)

                # --- Create empty plots to return to animate for initializing---#
                cg.EmptyPlots = [smooth, regress, peak, normalization]

                subplot_count += 1

            cg.plot_list.append(
                electrode_plot
            )  # 'plot_list' is a list of lists containing 'plots' for each electrode

            # -- Return both the figure and the axes to be stored as global variables -#
            return fig, ax

        except:
            print("Error in MakeFigure")

    #################################################################
    # Make Figures for Ratiometric Data                         ###
    # (e.g. Kinetic Differential Measurement, Normalized Ratio) ###
    #################################################################
    def MakeRatiometricFigure(self, electrode):

        try:
            figure, axes = plt.subplots(
                nrows=1, ncols=2, squeeze=False, figsize=(8.5, 1.85)
            )
            plt.subplots_adjust(
                bottom=0.3, hspace=0.6, wspace=0.3
            )  # adjust the spacing between subplots

            ##########################################################################
            # If the number of files is less than the resize interval, make         ###
            # the x-axis the length of numFiles. Elif the resize_interval is       ###
            # smaller than numFiles, make the x-axis the length of the first interval #
            ##########################################################################
            if cg.resize_interval > cg.numFiles:
                xlim_factor = cg.numFiles
            elif cg.resize_interval <= cg.numFiles:
                xlim_factor = cg.resize_interval

            ################################################
            # Set the X and Y axes for the Ratriometric  ##
            # Plots (KDM and Norm Ratio)                 ##
            ################################################
            axes[0, 0].set_ylabel("% Signal", fontweight="bold")
            axes[0, 1].set_ylabel("% Signal", fontweight="bold")

            if cg.XaxisOptions == "Experiment Time":
                axes[0, 0].set_xlim(
                    0, (xlim_factor * cg.SampleRate) / 3600 + (cg.SampleRate / 7200)
                )
                axes[0, 1].set_xlim(
                    0, (xlim_factor * cg.SampleRate) / 3600 + (cg.SampleRate / 7200)
                )
                axes[0, 0].set_xlabel("Time (h)")
                axes[0, 1].set_xlabel("Time (h)")

            elif cg.XaxisOptions == "File Number":
                axes[0, 0].set_xlim(0, xlim_factor + 0.1)
                axes[0, 1].set_xlim(0, xlim_factor + 0.1)
                axes[0, 0].set_xlabel("File Number")
                axes[0, 1].set_xlabel("File Number")

            axes[0, 0].set_ylim(100 * cg.min_norm, 100 * cg.max_norm)
            axes[0, 1].set_ylim(100 * cg.ratio_min, 100 * cg.ratio_max)
            axes[0, 0].set_title("Normalized Ratio")
            axes[0, 1].set_title("KDM")

            #####################################################
            # Create the primitive artists (Line2D objects) ###
            # that will contain the data that will be       ###
            # visualized by ElectrochemicalAnimation       ###
            #####################################################
            (norm_ratiometric_plot,) = axes[0, 0].plot(
                [], [], "ro", markersize=1
            )  # normalized ratio of high and low freq's
            (KDM,) = axes[0, 1].plot([], [], "ro", markersize=1)

            # if InjectionPoint =! None, these will
            # visualize the points after the injection
            (norm_injection,) = axes[0, 0].plot([], [], "bo", markersize=1)
            (KDM_injection,) = axes[0, 1].plot([], [], "bo", markersize=1)

            ratio_plots = [norm_ratiometric_plot, norm_injection, KDM, KDM_injection]
            cg.ratiometric_plots.append(ratio_plots)

            (empty_norm_ratiometric,) = axes[0, 0].plot([], [], "ro", markersize=1)
            (empty_KDM,) = axes[0, 1].plot([], [], "ro", markersize=1)
            cg.EmptyRatioPlots = [
                norm_ratiometric_plot,
                norm_injection,
                KDM,
                KDM_injection,
            ]

            return figure, axes

        except:
            print("\n ERROR IN MAKE RATIOMETRIC FIGURES \n")

    ##################################################################################
    # Initalize Y Limits of each figure depending on the y values of the first file ###
    ##################################################################################
    def InitializeSubplots(self, ax, frequency, electrode, subplot_count):

        print("Initialize Subplots: Continuous Scan")

        self.list_val = _get_listval(electrode)

        frequency = int(frequency)

        try:

            filename, filename2, filename3, filename4 = _retrieve_file(
                1, electrode, frequency
            )

            myfile = cg.mypath + filename  # path of your file
            myfile2 = cg.mypath + filename2
            myfile3 = cg.mypath + filename3
            myfile4 = cg.mypath + filename4

            try:
                # retrieves the size of the file in bytes
                mydata_bytes = os.path.getsize(myfile)
            except:
                try:
                    mydata_bytes = os.path.getsize(myfile2)
                    myfile = myfile2
                except:
                    try:
                        mydata_bytes = os.path.getsize(myfile3)
                        myfile = myfile3
                    except:
                        try:
                            mydata_bytes = os.path.getsize(myfile4)
                            myfile = myfile4
                        except:
                            mydata_bytes = 1

            if mydata_bytes > cg.byte_limit:
                print("Found File %s" % myfile)
                self.RunInitialization(myfile, ax, subplot_count, electrode, frequency)

            else:
                return False

        except:
            print("could not find file for electrode %d" % electrode)
            # --- If search time has not met the search limit keep searching ---#
            root.after(
                1000, self.InitializeSubplots, ax, frequency, electrode, subplot_count
            )

    def RunInitialization(self, myfile, ax, subplot_count, electrode, frequency):

        try:
            #########################
            # Retrieve the data ###
            #########################

            potentials, currents, data_dict = ReadData(myfile, electrode)

            ##########################################
            # Set the x axes of the voltammogram ###
            ##########################################
            MIN_POTENTIAL = min(potentials)
            MAX_POTENTIAL = max(potentials)
            # -- Reverse voltammogram to match the 'Texas' convention --#
            ax[0, subplot_count].set_xlim(MAX_POTENTIAL, MIN_POTENTIAL)

            #######################################
            # Get the high and low potentials ###
            #######################################

            if int(frequency) > cutoff_frequency:

                if not cg.HighAlreadyReset:
                    cg.high_xstart = max(potentials)
                    cg.high_xend = min(potentials)

                # -- set the local variables to the global ---#
                xend = cg.high_xend
                xstart = cg.high_xstart

            elif int(frequency) <= cutoff_frequency:

                if not cg.LowAlreadyReset:
                    cg.low_xstart = max(potentials)
                    cg.low_xend = min(potentials)

                # -- set the local variables to the global ---#
                xstart = cg.low_xstart
                xend = cg.low_xend

            cut_value = 0
            for value in potentials:
                if value == 0:
                    cut_value += 1

            if cut_value > 0:
                potentials = potentials[:-cut_value]
                currents = currents[:-cut_value]

            adjusted_potentials = [
                value for value in potentials if xend <= value <= xstart
            ]

            #########################################
            # Savitzky-Golay smoothing          ###
            #########################################
            smooth_currents = savgol_filter(currents, 15, sg_degree)
            data_dict = dict(zip(potentials, smooth_currents))

            #######################################
            # adjust the smooth currents to   ###
            # match the adjusted potentials   ###
            #######################################
            adjusted_currents = []
            for potential in adjusted_potentials:
                adjusted_currents.append(data_dict[potential])

            ######################
            # Polynomial fit ###
            ######################
            polynomial_coeffs = np.polyfit(
                adjusted_potentials, adjusted_currents, polyfit_deg
            )
            eval_regress = np.polyval(polynomial_coeffs, adjusted_potentials).tolist()
            regression_dict = dict(
                zip(eval_regress, adjusted_potentials)
            )  # dictionary with current: potential

            fit_half = round(len(eval_regress) / 2)
            min1 = min(eval_regress[:-fit_half])
            min2 = min(eval_regress[fit_half:])
            max1 = max(eval_regress[:-fit_half])
            max2 = max(eval_regress[fit_half:])

            linear_fit = np.polyfit(
                [regression_dict[min1], regression_dict[min2]], [min1, min2], 1
            )
            linear_regression = np.polyval(
                linear_fit, [regression_dict[min1], regression_dict[min2]]
            ).tolist()

            if cg.SelectedOptions == "Peak Height Extraction":
                Peak_Height = max(max1, max2) - min(min1, min2)
                data = Peak_Height

            if cg.SelectedOptions == "Area Under the Curve":
                AUC_index = 1
                AUC = 0

                AUC_potentials = adjusted_potentials
                AUC_min = min(adjusted_currents)
                AUC_currents = [Y - AUC_min for Y in adjusted_currents]

                while AUC_index <= len(AUC_currents) - 1:
                    AUC_height = (
                        AUC_currents[AUC_index] + AUC_currents[AUC_index - 1]
                    ) / 2
                    AUC_width = (
                        AUC_potentials[AUC_index] - AUC_potentials[AUC_index - 1]
                    )
                    AUC += AUC_height * AUC_width
                    AUC_index += 1

                data = AUC

            # --- calculate the baseline current ---#
            minimum_current = min(min1, min2)
            maximum_current = max(max1, max2)

            # - Voltammogram -#
            ax[0, subplot_count].set_ylim(
                minimum_current - abs(cg.min_raw * minimum_current),
                maximum_current + abs(cg.max_raw * maximum_current),
            )

            # - PHE/AUC Data -#
            ax[1, subplot_count].set_ylim(
                data - abs(cg.min_data * data), data + abs(cg.max_data * data)
            )

            # - Normalized Data -#
            ax[2, subplot_count].set_ylim(cg.min_norm, cg.max_norm)

            print("RunInitialization Complete")

            return True

        except:
            print("\n\nError in RunInitialization\n\n")


##################################################################
# Real Time Data Animation Canvas for Frequency Map Analysis ###
##################################################################
class InitializeFrequencyMapCanvas:
    def __init__(self):

        ##############################################
        # Generate global lists for data storage ###
        ##############################################

        self.length = len(cg.frequency_list)
        cg.electrode_count = int(cg.electrode_count)

        # --- Animation list ---#
        cg.anim = []

        # --- file list ---#
        cg.file_list = [0] * cg.numFiles

        # --- Figure lists ---#
        cg.figures = []

        ############################################
        # Create global lists for data storage ###
        ############################################
        cg.data_list = [0] * cg.electrode_count  # Peak Height/AUC data (after smoothing
        # and polynomial regression)

        for num in range(cg.electrode_count):
            cg.data_list[num] = [0] * self.length  # a data list for each eletrode
            for count in range(
                self.length
            ):  # a data list for each frequency for that electrode
                cg.data_list[num][count] = [0] * cg.numFiles

        # --- Lists of Frames and Artists ---#
        cg.plot_list = []
        cg.frame_list = []

        ######################################################
        # Create a figure and artists for each electrode ###
        ######################################################
        for num in range(cg.electrode_count):
            electrode = cg.electrode_list[num]
            figure = self.MakeFigure(electrode)
            cg.figures.append(figure)

        #####################################################
        # Create a frame for each electrode and embed   ###
        # within it the figure containing its artists   ###
        #####################################################

        cg.PlotFrames = {}  # Dictionary of frames for each electrode
        cg.PlotValues = []  # create a list of frames

        # --- Create a container that can be created and destroyed when Start()
        # or Reset() is called, respectively ---#
        cg.PlotContainer = tk.Frame(cg.container, relief="groove", bd=3)
        cg.PlotContainer.grid(row=0, column=1, sticky="nsew")
        cg.PlotContainer.rowconfigure(0, weight=1)
        cg.PlotContainer.columnconfigure(0, weight=1)

        frame_count = 0
        for (
            electrode_frame
        ) in cg.frame_list:  # Iterate through the frame of each electrode

            # --- create an instance of the frame and append it to
            # the global frame dictionary ---#
            cg.FrameReference = FrequencyMapVisualizationFrame(
                electrode_frame, frame_count, cg.PlotContainer, self
            )  # PlotContainer is the 'parent' frame
            cg.FrameReference.grid(
                row=0, column=0, sticky="nsew"
            )  # sticky must be 'nsew' so it expands and contracts with resize
            cg.PlotFrames[electrode_frame] = cg.FrameReference

            frame_count += 1

        # --- Create a list containing the Frame objects for each electrode ---#
        for reference, frame in cg.PlotFrames.items():
            cg.PlotValues.append(frame)

        #################################
        # Initiate .txt File Export ###
        #################################

        # --- If the user has indicated that text file export should be activated ---#
        if cg.SaveVar:
            print("Initializing Text File Export")
            cg.text_file_export = TextFileExport()

        else:
            cg.text_file_export = None
            print("Text File Export Deactivated")

    ############################################
    # Create the figure and artist objects ###
    ############################################
    def MakeFigure(self, electrode):

        try:
            ##########################################
            # Setup the Figure for voltammograms ###
            ##########################################
            fig, ax = plt.subplots(
                nrows=2, ncols=1, squeeze=False, figsize=(9, 4.5)
            )  # figsize=(width, height)
            plt.subplots_adjust(
                bottom=0.2, hspace=0.6, wspace=0.3
            )  # adjust the spacing between subplots

            # ---Set the electrode index value---#
            if cg.e_var == "single":
                cg.list_val = (
                    cg.current_column_index + (electrode - 1) * cg.spacing_index
                )
            elif cg.e_var == "multiple":
                cg.list_val = cg.current_column_index

            #######################
            # Set axis labels ###
            #######################
            ax[0, 0].set_ylabel("Current (µA)", fontweight="bold")
            ax[0, 0].set_xlabel("Voltage (V)", fontweight="bold")

            ax[1, 0].set_ylabel("Charge (uC)", fontweight="bold")
            ax[1, 0].set_xlabel("Frequency (Hz)", fontweight="bold")
            ##########################################
            # Set suplot axes for each frequency ###
            ##########################################
            electrode_plot = []

            max_frequency = cg.frequency_list[-1]
            ax[1, 0].set_xscale("log")
            ##########################################################################
            ##########################################################################
            #       Analyze the first file and create the Y limits of the subplots   ###
            #               depending on the data range of the first file            ###
            ##########################################################################

            self.InitializeSubplots(ax, electrode)

            #########################################################################
            #########################################################################

            # ---Initiate the subplots---#
            # this assigns a Line2D artist object to the artist object (Axes)
            (smooth,) = ax[0, 0].plot([], [], "ko", Markersize=2)
            (regress,) = ax[0, 0].plot([], [], "r-")
            (charge,) = ax[1, 0].plot([], [], "ko", MarkerSize=1)

            # --- shading for AUC ---#
            verts = [(0, 0), *zip([], []), (0, 0)]
            poly = Polygon(verts, alpha=0.5)
            ax[0, 0].add_patch(poly)

            #####################################################
            # Create a list of the primitive artists        ###
            # (Line2D objects) that will be returned        ###
            # to ElectrochemicalAnimation to be visualized  ###
            #####################################################

            # this is the list that will be returned as _drawn_artists
            # to the Funcanimation class
            plots = [smooth, regress, charge, poly]

            # --- And append that list to keep a global reference ---#
            electrode_plot.append(
                plots
            )  # 'plots' is a list of artists that are passed to animate
            electrode_frame = "Electrode %s" % str(electrode)
            if electrode_frame not in cg.frame_list:
                cg.frame_list.append(electrode_frame)

            # --- Create empty plots to return to animate for initializing---#
            cg.EmptyPlots = [smooth, regress, charge]

            cg.plot_list.append(
                plots
            )  # 'plot_list' is a list of lists containing 'plots' for each electrode

            # -- Return both the figure and the axes to be stored as global variables -#
            return fig, ax

        except:
            print("Error in MakeFigure")

    ##################################################################################
    # Initalize Y Limits of each figure depending on the y values of the first file ###
    ##################################################################################
    def InitializeSubplots(self, ax, electrode):

        self.list_val = _get_listval(electrode)

        try:
            frequency = cg.frequency_list[0]
            (
                filename,
                filename2,
                filename3,
                filename4,
                filename5,
                filename6,
            ) = _retrieve_file(1, electrode, frequency)

            myfile = cg.mypath + filename  # path of your file
            myfile2 = cg.mypath + filename2
            myfile3 = cg.mypath + filename3
            myfile4 = cg.mypath + filename4
            myfile5 = cg.mypath + filename5
            myfile6 = cg.mypath + filename6
            try:
                # retrieves the size of the file in bytes
                mydata_bytes = os.path.getsize(myfile)
            except:
                try:
                    mydata_bytes = os.path.getsize(myfile2)
                    myfile = myfile2
                except:
                    try:
                        mydata_bytes = os.path.getsize(myfile3)
                        myfile = myfile3
                    except:
                        try:
                            mydata_bytes = os.path.getsize(myfile4)
                            myfile = myfile4
                        except:
                            try:
                                mydata_bytes = os.path.getsize(myfile5)
                                myfile = myfile5
                            except:
                                try:
                                    mydata_bytes = os.path.getsize(myfile6)
                                    myfile = myfile6
                                except:
                                    mydata_bytes = 1

            if mydata_bytes > cg.byte_limit:
                print("Found File %s" % myfile)
                self.RunInitialization(myfile, ax, electrode)

            else:
                return False

        except:
            print("could not find file for electrode %d" % electrode)
            # --- If search time has not met the search limit keep searching ---#
            root.after(1000, self.InitializeSubplots, ax, electrode)

    def RunInitialization(self, myfile, ax, electrode):

        try:
            #########################
            # Retrieve the data ###
            #########################
            potentials, currents, data_dict = ReadData(myfile, electrode)
            ##########################################
            # Set the x axes of the voltammogram ###
            ##########################################
            MIN_POTENTIAL = min(potentials)
            MAX_POTENTIAL = max(potentials)

            # -- Reverse voltammogram to match the 'Texas' convention --#
            ax[0, 0].set_xlim(MAX_POTENTIAL, MIN_POTENTIAL)

            #######################################
            # Get the high and low potentials ###
            #######################################

            # -- set the local variables to the global ---#
            xstart = max(potentials)
            xend = min(potentials)

            cg.low_xstart = xstart
            cg.high_xstart = xstart
            cg.low_xend = xend
            cg.high_xend = xend

            cut_value = 0
            for value in potentials:
                if value == 0:
                    cut_value += 1

            if cut_value > 0:
                potentials = potentials[:-cut_value]
                currents = currents[:-cut_value]

            adjusted_potentials = [
                value for value in potentials if xend <= value <= xstart
            ]

            #########################################
            # Savitzky-Golay smoothing          ###
            #########################################
            smooth_currents = savgol_filter(currents, 15, sg_degree)
            data_dict = dict(zip(potentials, smooth_currents))

            #######################################
            # adjust the smooth currents to   ###
            # match the adjusted potentials   ###
            #######################################
            adjusted_currents = []
            for potential in adjusted_potentials:
                adjusted_currents.append(data_dict[potential])

            ######################
            # Polynomial fit ###
            ######################
            polynomial_coeffs = np.polyfit(
                adjusted_potentials, adjusted_currents, polyfit_deg
            )
            eval_regress = np.polyval(polynomial_coeffs, adjusted_potentials).tolist()
            regression_dict = dict(
                zip(eval_regress, adjusted_potentials)
            )  # dictionary with current: potential

            fit_half = round(len(eval_regress) / 2)
            min1 = min(eval_regress[:-fit_half])
            min2 = min(eval_regress[fit_half:])
            max1 = max(eval_regress[:-fit_half])
            max2 = max(eval_regress[fit_half:])

            linear_fit = np.polyfit(
                [regression_dict[min1], regression_dict[min2]], [min1, min2], 1
            )
            linear_regression = np.polyval(
                linear_fit, [regression_dict[min1], regression_dict[min2]]
            ).tolist()

            Peak_Height = max(max1, max2) - min(min1, min2)

            if cg.SelectedOptions == "Area Under the Curve":
                AUC_index = 1
                AUC = 0

                AUC_potentials = [abs(potential) for potential in adjusted_potentials]
                AUC_min = min(adjusted_currents)
                AUC_currents = [Y - AUC_min for Y in adjusted_currents]

                while AUC_index <= len(AUC_currents) - 1:
                    AUC_height = (
                        AUC_currents[AUC_index] + AUC_currents[AUC_index - 1]
                    ) / 2
                    AUC_width = (
                        AUC_potentials[AUC_index] - AUC_potentials[AUC_index - 1]
                    )
                    AUC += AUC_height * AUC_width
                    AUC_index += 1

            # --- calculate the baseline current ---#
            minimum_current = min(min1, min2)
            maximum_current = max(max1, max2)
            peak_current = maximum_current - minimum_current
            charge = peak_current / (cg.frequency_list[0])

            # Reverse voltammogram to match the 'Texas' convention ##
            ax[0, 0].set_xlim(MAX_POTENTIAL, MIN_POTENTIAL)
            ax[0, 0].set_ylim(
                minimum_current - abs(cg.min_raw * minimum_current),
                maximum_current + abs(cg.max_raw * maximum_current),
            )  # voltammogram

            # set the limits of the lovric plot ##
            ax[1, 0].set_ylim(
                charge - abs(cg.min_data * charge), charge + abs(cg.max_data * charge)
            )
            ax[1, 0].set_xlim(int(cg.frequency_list[0]), int(cg.frequency_list[-1]))

            return True

        except:
            print("\n\nError in RunInitialization\n\n")

            #############################################################
            #############################################################
            #              END OF INITIATION FUNCTIONS              ###
            #############################################################
            #############################################################


# ------------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------------#


##########################################################################
##########################################################################
#   ANIMATION FUNCTION TO HANDLE ALL DATA ANALYSIS AND VISUALIZATION ###
##########################################################################
##########################################################################


class ElectrochemicalAnimation:
    def __init__(
        self,
        fig,
        electrode,
        generator=None,
        func=None,
        resize_interval=None,
        fargs=None,
    ):

        self.electrode = electrode  # Electrode for this class instance
        self.num = cg.electrode_dict[self.electrode]  # Electrode index value
        self.spacer = "".join(
            ["       "] * self.electrode
        )  # Spacer value for print statements
        self.file = cg.starting_file  # Starting File
        self.index = 0  # File Index Value
        self.count = 0  # Frequency index value
        self.frequency_limit = (
            len(cg.frequency_list) - 1
        )  # ' -1 ' so it matches the index value

        # Lists for sample rate (time passed)  ###
        # and file count for each electrode    ###
        self.sample_list = []
        self.file_list = []

        self.frequency_axis = []
        self.charge_axis = []

        ##############################
        # Set the generator object ##
        ##############################
        if generator is not None:
            self.generator = generator
        else:
            self.generator = self._raw_generator

        ################################
        # Set the animation function ##
        ################################
        if func is not None:
            self._func = func
        elif cg.method == "Continuous Scan":
            self._func = self._continuous_func
        elif cg.method == "Frequency Map":
            self._func = self._frequency_map_func

        if resize_interval is not None:
            self.resize_interval = resize_interval
        else:
            self.resize_interval = None

        self.resize_limit = self.resize_interval  # set the first limit

        if fargs:
            self._args = fargs
        else:
            self._args = ()

        self._fig = fig

        # Disables blitting for backends that don't support it.  This
        # allows users to request it if available, but still have a
        # fallback that works if it is not.
        self._blit = fig.canvas.supports_blit

        # Instead of starting the event source now, we connect to the figure's
        # draw_event, so that we only start once the figure has been drawn.
        self._first_draw_id = fig.canvas.mpl_connect("draw_event", self._start)

        # Connect to the figure's close_event so that we don't continue to
        # fire events and try to draw to a deleted figure.
        self._close_id = self._fig.canvas.mpl_connect("close_event", self._stop)

        self._setup_blit()

    def _start(self, *args):

        # Starts interactive animation. Adds the draw frame command to the GUI
        # andler, calls show to start the event loop.

        # First disconnect our draw event handler
        self._fig.canvas.mpl_disconnect(self._first_draw_id)
        self._first_draw_id = None  # So we can check on save

        # Now do any initial draw
        self._init_draw()

        # Create a thread to analyze obtain the file from a Queue
        # and analyze the data.

        class _threaded_animation(threading.Thread):
            def __init__(self, Queue):
                # global PoisonPill

                threading.Thread.__init__(self)  # initiate the thread

                self.q = Queue

                # -- set the poison pill event for Reset --#
                self.PoisonPill = tk.Event()
                PoisonPill = self.PoisonPill  # global reference

                self.file = 1

                root.after(10, self.start)  # initiate the run() method

            def run(self):

                while True:
                    try:
                        task = self.q.get(block=False)

                    except:
                        break
                    else:
                        if not cg.PoisonPill:
                            root.after(cg.Interval, task)

                if not cg.analysis_complete:
                    if not cg.PoisonPill:
                        root.after(10, self.run)

        threaded_animation = _threaded_animation(Queue=cg.q)

        self._step()

    def _stop(self, *args):
        # On stop we disconnect all of our events.
        self._fig.canvas.mpl_disconnect(self._resize_id)
        self._fig.canvas.mpl_disconnect(self._close_id)

    def _setup_blit(self):
        # Setting up the blit requires: a cache of the background for the
        # axes
        self._blit_cache = dict()
        self._drawn_artists = []
        self._resize_id = self._fig.canvas.mpl_connect(
            "resize_event", self._handle_resize
        )
        self._post_draw(True)

    def _blit_clear(self, artists, bg_cache):
        # Get a list of the axes that need clearing from the artists that
        # have been drawn. Grab the appropriate saved background from the
        # cache and restore.
        axes = {a.axes for a in artists}
        for a in axes:
            if a in bg_cache:
                a.figure.canvas.restore_region(bg_cache[a])

    #######################################################################
    # Initialize the drawing by returning a sequence of blank artists ###
    #######################################################################
    def _init_draw(self):

        self._drawn_artists = cg.EmptyPlots

        for a in self._drawn_artists:
            a.set_animated(self._blit)

    def _redraw_figures(self):
        print("\nREDRAWING FIGURES\nRESIZE LIMIT = %d" % self.resize_limit)

        ############################################
        # Resize raw and normalized data plots ###
        ############################################
        fig, ax = cg.figures[self.num]
        for count in range(len(cg.frequency_list)):

            if cg.XaxisOptions == "Experiment Time":
                ax[1, count].set_xlim(
                    0,
                    (self.resize_limit * cg.SampleRate) / 3600 + (cg.SampleRate / 7200),
                )
                ax[2, count].set_xlim(
                    0,
                    (self.resize_limit * cg.SampleRate) / 3600 + (cg.SampleRate / 7200),
                )

            elif cg.XaxisOptions == "File Number":
                ax[1, count].set_xlim(0, self.resize_limit + 0.1)
                ax[2, count].set_xlim(0, self.resize_limit + 0.1)

        ##################################
        # Readjust Ratiometric Plots ###
        ##################################
        if len(cg.frequency_list) > 1:
            fig, ax = cg.ratiometric_figures[self.num]

            if cg.XaxisOptions == "File Number":
                ax[0, 0].set_xlim(0, self.resize_limit + 0.1)
                ax[0, 1].set_xlim(0, self.resize_limit + 0.1)

            elif cg.XaxisOptions == "Experiment Time":
                ax[0, 0].set_xlim(
                    0,
                    (self.resize_limit * cg.SampleRate) / 3600 + (cg.SampleRate / 7200),
                )
                ax[0, 1].set_xlim(
                    0,
                    (self.resize_limit * cg.SampleRate) / 3600 + (cg.SampleRate / 7200),
                )

        #####################################################
        # Set up the new canvas with an idle draw event ###
        #####################################################
        self._post_draw(True)

    def _handle_resize(self, *args):
        # On resize, we need to disable the resize event handling so we don't
        # get too many events. Also stop the animation events, so that
        # we're paused. Reset the cache and re-init. Set up an event handler
        # to catch once the draw has actually taken place.

        #################################################
        # Stop the event source and clear the cache ###
        #################################################
        self._fig.canvas.mpl_disconnect(self._resize_id)
        self._blit_cache.clear()
        self._init_draw()
        self._resize_id = self._fig.canvas.mpl_connect("draw_event", self._end_redraw)

    def _end_redraw(self, evt):
        # Now that the redraw has happened, do the post draw flushing and
        # blit handling. Then re-enable all of the original events.
        self._post_draw(True)
        self._fig.canvas.mpl_disconnect(self._resize_id)
        self._resize_id = self._fig.canvas.mpl_connect(
            "resize_event", self._handle_resize
        )

    def _draw_next_frame(self, framedata, fargs=None):
        # Breaks down the drawing of the next frame into steps of pre- and
        # post- draw, as well as the drawing of the frame itself.
        self._pre_draw(framedata)
        self._draw_frame(framedata, fargs)
        self._post_draw(False)

    def _pre_draw(self, framedata):
        # Perform any cleaning or whatnot before the drawing of the frame.
        # This default implementation allows blit to clear the frame.
        self._blit_clear(self._drawn_artists, self._blit_cache)

    ###########################################################################
    # Retrieve the data from _animation and blit the data onto the canvas ###
    ###########################################################################
    def _draw_frame(self, framedata, fargs):

        # Ratiometric #
        if fargs:
            if fargs == "ratiometric_analysis":
                self._drawn_artists = self._ratiometric_animation(
                    framedata, *self._args
                )
                self._drawn_artists = sorted(
                    self._drawn_artists, key=lambda x: x.get_zorder()
                )
                for a in self._drawn_artists:
                    a.set_animated(self._blit)

        else:

            self._drawn_artists = self._func(framedata, *self._args)

            if self._drawn_artists is None:
                raise RuntimeError(
                    "The animation function must return a "
                    "sequence of Artist objects."
                )
            self._drawn_artists = sorted(
                self._drawn_artists, key=lambda x: x.get_zorder()
            )

            for a in self._drawn_artists:
                a.set_animated(self._blit)

    def _post_draw(self, redraw):
        # After the frame is rendered, this handles the actual flushing of
        # the draw, which can be a direct draw_idle() or make use of the
        # blitting.

        if redraw:

            # Data plots #
            self._fig.canvas.draw()

            # ratiometric plots
            if cg.method == "Continuous Scan":
                if len(cg.frequency_list) > 1:
                    ratio_fig, ratio_ax = cg.ratiometric_figures[self.num]
                    ratio_fig.canvas.draw()

        elif self._drawn_artists:

            self._blit_draw(self._drawn_artists, self._blit_cache)

    # The rest of the code in this class is to facilitate easy blitting
    def _blit_draw(self, artists, bg_cache):
        # Handles blitted drawing, which renders only the artists given instead
        # of the entire figure.
        updated_ax = []
        for a in artists:
            # If we haven't cached the background for this axes object, do
            # so now. This might not always be reliable, but it's an attempt
            # to automate the process.
            if a.axes not in bg_cache:
                bg_cache[a.axes] = a.figure.canvas.copy_from_bbox(a.axes.bbox)
            a.axes.draw_artist(a)
            updated_ax.append(a.axes)

        # After rendering all the needed artists, blit each axes individually.
        for ax in set(updated_ax):
            ax.figure.canvas.blit(ax.bbox)

    # callback that is called every 'interval' ms ##
    def _step(self):
        if self.file not in self.file_list:
            self.file_list.append(self.file)
            self.sample_list.append((len(self.file_list) * cg.SampleRate) / 3600)

        # look for the file here ###
        frequency = int(cg.frequency_list[self.count])

        if cg.method == "Continuous Scan":
            self.electrode = cg.electrode_list[self.num]

            filename, filename2, filename3, filename4 = _retrieve_file(
                self.file, self.electrode, frequency
            )

            # path of your file
            myfile = cg.mypath + filename
            myfile2 = cg.mypath + filename2
            myfile3 = cg.mypath + filename3
            myfile4 = cg.mypath + filename4

            try:
                # retrieves the size of the file in bytes
                mydata_bytes = os.path.getsize(myfile)
            except:
                try:
                    mydata_bytes = os.path.getsize(myfile2)
                    myfile = myfile2
                except:
                    try:
                        mydata_bytes = os.path.getsize(myfile3)
                        myfile = myfile3
                    except:
                        try:
                            mydata_bytes = os.path.getsize(myfile4)
                            myfile = myfile4
                        except:
                            mydata_bytes = 1

        elif cg.method == "Frequency Map":

            (
                filename,
                filename2,
                filename3,
                filename4,
                filename5,
                filename6,
            ) = _retrieve_file(self.file, self.electrode, frequency)

            myfile = cg.mypath + filename  # path of your file
            myfile2 = cg.mypath + filename2
            myfile3 = cg.mypath + filename3
            myfile4 = cg.mypath + filename4
            myfile5 = cg.mypath + filename5
            myfile6 = cg.mypath + filename6

            try:
                # retrieves the size of the file in bytes
                mydata_bytes = os.path.getsize(myfile)
            except:
                try:
                    mydata_bytes = os.path.getsize(myfile2)
                    myfile = myfile2
                    filename = filename2
                except:
                    try:
                        mydata_bytes = os.path.getsize(myfile3)
                        myfile = myfile3
                        filename = filename3
                    except:
                        try:
                            mydata_bytes = os.path.getsize(myfile4)
                            myfile = myfile4
                            filename = filename4
                        except:
                            try:
                                mydata_bytes = os.path.getsize(myfile5)
                                myfile = myfile5
                                filename = filename5
                            except:
                                try:
                                    mydata_bytes = os.path.getsize(myfile6)
                                    myfile = myfile6
                                    filename = filename6
                                except:
                                    mydata_bytes = 1

        if mydata_bytes > cg.byte_limit:
            print("%s%d: Queueing %s" % (self.spacer, self.electrode, filename))
            cg.q.put(lambda: self._run_analysis(myfile, frequency))

        else:
            if not cg.PoisonPill:
                root.after(100, self._step)

    def _check_queue(self):

        while True:
            try:
                print("%sChecking Queue" % self.spacer)
                task = cg.q.get(block=False)
            except:
                print("%sQueue Empty" % self.spacer)
                break
            else:
                if not cg.PoisonPill:
                    root.after(1, self.task)

        if not cg.analysis_complete:
            if not cg.PoisonPill:
                root.after(5, self._check_queue)

    def _run_analysis(self, myfile, frequency):

        #######################################################
        # Perform the next iteration of the data analysis ###
        #######################################################
        try:
            framedata = self.generator(myfile, frequency)
            self._draw_next_frame(framedata)

            if cg.method == "Frequency Map":
                cg.track.tracking(self.file, frequency)

        except StopIteration:
            return False

        ##########################################################################
        # if the resize limit has been reached, resize and redraw the figure ###
        ##########################################################################
        if self.file == self.resize_limit:

            # Dont redraw if this is the already the last file #
            if self.resize_limit < cg.numFiles:

                ###############################################################
                # If this is the last frequency, move onto the next limit ###
                ###############################################################
                if self.count == self.frequency_limit:
                    self.resize_limit = self.resize_limit + self.resize_interval

                    # If the resize limit is above the number of files (e.g.
                    # going out of bounds for the last resize event) then
                    # readjust the final interval to the number of files
                    if self.resize_limit >= cg.numFiles:
                        self.resize_limit = cg.numFiles

                ############################################################
                # 'if' statement used to make sure the plots dont get  ###
                # erased when there are no more files to be visualized ###
                ############################################################
                try:
                    self._redraw_figures()
                except:
                    print("\nCould not redraw figure\n")

        ##################################################################
        # If the function has analyzed each frequency for this file, ###
        # move onto the next file and reset the frequency index      ###
        ##################################################################
        if self.count == self.frequency_limit:

            ######################################################
            # If there are multiple frequencies, perform     ###
            # ratiometric analysis and visualize the data on ###
            ######################################################
            if cg.method == "Continuous Scan":
                if len(cg.frequency_list) > 1:
                    try:
                        framedata = self._ratiometric_generator()
                        self._draw_next_frame(framedata, fargs="ratiometric_analysis")

                    except StopIteration:
                        return False

                cg.track.tracking(self.file, None)

            #########################################################################
            # If the function has analyzed the final final, remove the callback ###
            #########################################################################
            if self.file == cg.numFiles:
                print(
                    "\n%sFILE %s.\n%sElectrode %d\n%sData Analysis Complete\n"
                    % (
                        self.spacer,
                        str(self.file),
                        self.spacer,
                        self.electrode,
                        self.spacer,
                    )
                )

                if cg.method == "Continuous Scan":
                    cg.post_analysis._analysis_finished()

            else:
                self.file += 1
                self.index += 1
                self.count = 0
                root.after(1, self._step)

        ##########################################################
        # Elif the function has not analyzed each frequency  ###
        # for this file, move onto the next frequency        ###
        ##########################################################
        elif self.count < self.frequency_limit:
            self.count += 1

            root.after(1, self._step)

    def _raw_generator(self, myfile, frequency):

        ########################################
        # Polynomical Regression Range (V) ###
        ########################################
        # --- if the frequency is equal or below cutoff_frequency,
        # use the low freq parameters ---#
        if frequency <= cutoff_frequency:
            xstart = cg.low_xstart
            xend = cg.low_xend

        # --- if the frequency is above cutoff_frequency,
        # use the high freq parameters ---#
        else:
            xstart = cg.high_xstart
            xend = cg.high_xend

        ###################################
        # Retrieve data from the File ###
        ###################################
        potentials, currents, data_dict = ReadData(myfile, self.electrode)

        cut_value = 0
        for value in potentials:
            if value == 0:
                cut_value += 1

        if cut_value > 0:
            potentials = potentials[:-cut_value]
            currents = currents[:-cut_value]

        ################################################################
        # Adjust the potentials depending on user-input parameters ###
        ################################################################
        adjusted_potentials = [value for value in potentials if xend <= value <= xstart]

        #########################################
        # Savitzky-Golay Smoothing          ###
        #########################################
        min_potential = min(potentials)  # find the min potential
        sg_limit = cg.sg_window / 1000  # mV --> V

        # shift all values positive
        sg_potentials = [x - min_potential for x in potentials]

        # find how many points fit within the sg potential window
        # this will be how many points are included in the rolling average
        sg_range = len([x for x in sg_potentials if x <= sg_limit])

        # --- Savitzky-golay Window must be greater than the range ---#
        if sg_range <= sg_degree:
            sg_range = sg_degree + 1

        # -- if the range is even, make it odd --#
        if sg_range % 2 == 0:
            sg_range = sg_range + 1

        # Apply the smoothing function and create a dictionary pairing
        # each potential with its corresponding current
        try:
            smooth_currents = savgol_filter(currents, sg_range, sg_degree)
            data_dict = dict(zip(potentials, smooth_currents))
        except ValueError:
            smooth_currents = savgol_filter(currents, 15, sg_degree)
            data_dict = dict(zip(potentials, smooth_currents))

        #######################################
        # adjust the smooth currents to   ###
        # match the adjusted potentials   ###
        #######################################
        adjusted_currents = []
        for potential in adjusted_potentials:
            adjusted_currents.append(data_dict[potential])

        ######################
        # Polynomial fit ###
        ######################
        polynomial_coeffs = np.polyfit(
            adjusted_potentials, adjusted_currents, polyfit_deg
        )

        #############################
        # Polynomial Regression ###
        #############################
        eval_regress = np.polyval(polynomial_coeffs, adjusted_potentials).tolist()
        regression_dict = dict(
            zip(eval_regress, adjusted_potentials)
        )  # dictionary with current: potential

        ###############################################
        # Absolute Max/Min Peak Height Extraction ###
        ###############################################
        # -- If the user selects 'Absolute Max/Min' in the 'Peak Height
        # Extraction Settings'
        # -- within the Settings toolbar this analysis method will be used for PHE
        fit_half = round(len(eval_regress) / 2)

        min1 = min(eval_regress[:fit_half])
        min2 = min(eval_regress[fit_half:])
        max1 = max(eval_regress[:fit_half])
        max2 = max(eval_regress[fit_half:])

        ################################################################
        # If the user selected Peak Height Extraction, analyze PHE ###
        ################################################################
        Peak_Height = max(max1, max2) - min(min1, min2)
        if cg.SelectedOptions == "Peak Height Extraction":
            data = Peak_Height

        ########################################################
        # If the user selected AUC extraction, analyze AUC ###
        ########################################################

        elif cg.SelectedOptions == "Area Under the Curve":
            ##################################
            # Integrate Area Under the   ###
            # Curve using a Riemmann Sum  ###
            ##################################
            AUC_index = 1
            AUC = 0

            AUC_potentials = adjusted_potentials

            # --- Find the minimum value and normalize it to 0 ---#
            AUC_min = min(adjusted_currents)
            AUC_currents = [Y - AUC_min for Y in adjusted_currents]

            # --- Midpoint Riemann Sum ---#
            while AUC_index <= len(AUC_currents) - 1:
                AUC_height = (AUC_currents[AUC_index] + AUC_currents[AUC_index - 1]) / 2
                AUC_width = AUC_potentials[AUC_index] - AUC_potentials[AUC_index - 1]
                AUC += AUC_height * AUC_width
                AUC_index += 1

            data = AUC

        #######################################
        # Save the data into global lists ###
        #######################################
        cg.data_list[self.num][self.count][self.index] = data

        if cg.method == "Continuous Scan":
            cg.data_normalization.Normalize(
                self.file, data, self.num, self.count, self.index
            )

        elif cg.method == "Frequency Map":
            frequency = cg.frequency_list[self.count]
            self.frequency_axis.append(int(frequency))

            charge = (Peak_Height / frequency) * 100000
            self.charge_axis.append(Peak_Height / frequency)

        #####################################################
        # Return data to the animate function as 'args' ###
        #####################################################

        return (
            potentials,
            adjusted_potentials,
            smooth_currents,
            adjusted_currents,
            eval_regress,
        )

    def _continuous_func(self, framedata, *args):

        if cg.key > 0:
            while True:

                (
                    potentials,
                    adjusted_potentials,
                    smooth_currents,
                    adjusted_currents,
                    regression,
                ) = framedata

                print(
                    "\n%s%d: %dHz\n%s_animate"
                    % (
                        self.spacer,
                        self.electrode,
                        cg.frequency_list[self.count],
                        self.spacer,
                    )
                )

                #############################################################
                # Acquire the current frequency and get the xstart/xend ###
                # parameters that will manipulate the visualized data   ###
                #############################################################
                frequency = cg.frequency_list[self.count]

                ###################################
                # Set the units of the X-axis ###
                ###################################
                if cg.XaxisOptions == "Experiment Time":
                    Xaxis = self.sample_list
                elif cg.XaxisOptions == "File Number":
                    Xaxis = self.file_list

                ################################################################
                # Acquire the artists for this electrode at this frequency ###
                # and get the data that will be visualized                 ###
                ################################################################
                plots = cg.plot_list[self.num][
                    self.count
                ]  # 'count' is the frequency index value

                ##########################
                # Visualize the data ###
                ##########################

                # --- Peak Height ---#

                data = cg.data_list[self.num][self.count][
                    : len(self.file_list)
                ]  # 'num' is the electrode index value

                if cg.frequency_list[self.count] == cg.HighLowList["Low"]:
                    NormalizedDataList = cg.offset_normalized_data_list[self.num][
                        : len(self.file_list)
                    ]
                else:
                    NormalizedDataList = cg.normalized_data_list[self.num][self.count][
                        : len(self.file_list)
                    ]

                ####################################################
                # Set the data of the artists to be visualized ###
                ####################################################
                if cg.InjectionPoint is None:
                    plots[0].set_data(
                        potentials, smooth_currents
                    )  # Smooth current voltammogram
                    plots[1].set_data(adjusted_potentials, regression)
                    plots[2].set_data(Xaxis, data)  # Raw Data
                    plots[4].set_data(Xaxis, NormalizedDataList)  # Norm Data

                ##########################################################
                # If an Injection Point has been set, visualize the  ###
                # data before and after the injection separately     ###
                ##########################################################
                elif cg.InjectionPoint is not None:

                    if self.file >= cg.InjectionPoint:
                        InjectionIndex = cg.InjectionPoint - 1

                        ####################################################
                        # Set the data of the artists to be visualized ###
                        ####################################################

                        plots[0].set_data(
                            potentials, smooth_currents
                        )  # Smooth current voltammogram
                        plots[1].set_data(
                            adjusted_potentials, regression
                        )  # Regression voltammogram
                        plots[2].set_data(
                            Xaxis[:InjectionIndex], data[:InjectionIndex]
                        )  # Raw Data up until injection point
                        plots[3].set_data(
                            Xaxis[InjectionIndex:], data[InjectionIndex:]
                        )  # Raw Data after injection point
                        plots[4].set_data(
                            Xaxis[:InjectionIndex], NormalizedDataList[:InjectionIndex]
                        )  # Norm Data before injection point
                        plots[5].set_data(
                            Xaxis[InjectionIndex:], NormalizedDataList[InjectionIndex:]
                        )  # Norm Data before injection point

                    elif cg.InjectionPoint > self.file:
                        plots[0].set_data(
                            potentials, smooth_currents
                        )  # Smooth current voltammogram
                        plots[1].set_data(adjusted_potentials, regression)
                        plots[2].set_data(Xaxis, data)  # Raw Data
                        plots[3].set_data([], [])  # Clear the injection artist
                        plots[4].set_data(Xaxis, NormalizedDataList)  # Norm Data
                        plots[5].set_data([], [])  # Clear the injection artist

                if cg.SelectedOptions == "Area Under the Curve":
                    # --- Shaded region of Area Under the Curve ---#
                    vertices = [
                        (adjusted_potentials[0], adjusted_currents[0]),
                        *zip(adjusted_potentials, adjusted_currents),
                        (adjusted_potentials[-1], adjusted_currents[-1]),
                    ]
                    plots[6].set_xy(vertices)

                print("returning plots!")
                return plots

        else:
            file = 1
            EmptyPlots = framedata
            time.sleep(0.1)
            print("\n Yielding Empty Plots in Animation \n")
            return EmptyPlots

    def _frequency_map_func(self, framedata, *args):

        if cg.key > 0:
            while True:

                (
                    potentials,
                    adjusted_potentials,
                    smooth_currents,
                    adjusted_currents,
                    regression,
                ) = framedata

                print(
                    "\n%s%d: %dHz\n%s_animate"
                    % (
                        self.spacer,
                        self.electrode,
                        cg.frequency_list[self.count],
                        self.spacer,
                    )
                )

                ################################################################
                # Acquire the artists for this electrode at this frequency ###
                # and get the data that will be visualized                 ###
                ################################################################
                plots = cg.plot_list[self.num]

                ##########################
                # Visualize the data ###
                ##########################

                # --- Peak Height ---#

                data = cg.data_list[self.num][self.count][
                    : len(self.file_list)
                ]  # 'num' is the electrode index value

                ####################################################
                # Set the data of the artists to be visualized ###
                ####################################################
                plots[0].set_data(
                    potentials, smooth_currents
                )  # Smooth current voltammogram
                plots[1].set_data(
                    adjusted_potentials, regression
                )  # Regression voltammogram
                plots[2].set_data(self.frequency_axis, self.charge_axis)

                print("returning plots!")
                return plots

        else:
            file = 1
            EmptyPlots = framedata
            time.sleep(0.1)
            print("\n Yielding Empty Plots in Animation \n")
            return EmptyPlots

    ############################
    # Ratiometric Analysis ###
    ############################
    def _ratiometric_generator(self):

        index = self.file - 1

        HighFrequency = cg.HighLowList["High"]
        LowFrequency = cg.HighLowList["Low"]

        HighCount = cg.frequency_dict[HighFrequency]
        LowCount = cg.frequency_dict[LowFrequency]

        HighPoint = cg.normalized_data_list[self.num][HighCount][self.index]
        LowPoint = cg.offset_normalized_data_list[self.num][self.index]

        NormalizedRatio = HighPoint / LowPoint
        KDM = (HighPoint - LowPoint) + 1

        # -- save the data to global lists --#
        cg.normalized_ratiometric_data_list[self.num].append(NormalizedRatio)
        cg.KDM_list[self.num].append(KDM)

        return NormalizedRatio, KDM

    def _ratiometric_animation(self, framedata, *args):

        NormalizedRatio, KDM = framedata

        plots = cg.ratiometric_plots[self.num]

        if cg.XaxisOptions == "Experiment Time":
            Xaxis = self.sample_list
        elif cg.XaxisOptions == "File Number":
            Xaxis = self.file_list

        norm = [X * 100 for X in cg.normalized_ratiometric_data_list[self.num]]
        KDM = [X * 100 for X in cg.KDM_list[self.num]]

        ##########################################
        # If an injection point has not been   ##
        # chosen, visualize the data as usual  ##
        ##########################################
        if cg.InjectionPoint is None:
            plots[0].set_data(Xaxis, norm)
            plots[2].set_data(Xaxis, KDM)

        ############################################
        # If an injection point has been chosen  ##
        # chosen, visualize the injection        ##
        # points separately                      ##
        ############################################
        elif cg.InjectionPoint is not None:

            # -- list index value for the injection point --#
            InjectionIndex = cg.InjectionPoint - 1

            # -- if the injection point has already been --#
            # -- analyzed, separate the visualized data  --#
            if self.file >= cg.InjectionPoint:
                plots[0].set_data(Xaxis[:InjectionIndex], norm[:InjectionIndex])
                plots[1].set_data(Xaxis[InjectionIndex:], norm[InjectionIndex:])
                plots[2].set_data(Xaxis[:InjectionIndex], KDM[:InjectionIndex])
                plots[3].set_data(Xaxis[InjectionIndex:], KDM[InjectionIndex:])

            # -- if the file is below the injectionpoint, wait until  --#
            # -- the point is reached to visualize the injection data --#
        elif self.file < cg.InjectionPoint:
            plots[0].set_data(Xaxis, norm)
            plots[1].set_data([], [])
            plots[2].set_data(Xaxis, KDM)
            plots[3].set_data([], [])

        return plots

        ##############################
        ##############################
        # END OF ANIMATION CLASS ###
        ##############################
        ##############################


# ------------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------------#


##############################
# Normalization Function ###
##############################
class DataNormalization:
    def __init__(self):
        pass

    def Normalize(self, file, data, num, count, index):

        sample = len(cg.file_list) * cg.SampleRate / 3600
        #######################################################
        # Check the frequency and apply the baseline offset ##
        #######################################################
        frequency = cg.frequency_list[count]
        if frequency == cg.HighLowList["Low"]:
            if cg.XaxisOptions == "Experiment Time":
                Offset = (sample * cg.LowFrequencySlope) + cg.LowFrequencyOffset
            elif cg.XaxisOptions == "File Number":
                Offset = (file * cg.LowFrequencySlope) + cg.LowFrequencyOffset
        else:
            Offset = 0

        NormalizationIndex = int(cg.NormalizationPoint) - 1

        # --- If the file being used as the standard has been analyzed,
        # normalize the data to that point ---#
        if file >= cg.NormalizationPoint:

            if cg.NormalizationPoint not in cg.NormalizationVault:
                cg.NormalizationVault.append(cg.NormalizationPoint)

            # -- if the software has still been normalizing to the first file,
            # start normalizing to the normalization point --#
            if not cg.InitializedNormalization:
                cg.InitializedNormalization = True

            ###########################################################
            # If the rest of the data has already been normalized ###
            # to this point, continue to normalize the data for   ###
            # the current file to the normalization point         ###
            ###########################################################
            cg.normalized_data_list[num][count][index] = (
                data / cg.data_list[num][count][NormalizationIndex]
            )

            ###########################################################################
            # If this is a low frequency, apply the offset to the normalized data ###
            ###########################################################################
            if frequency == cg.HighLowList["Low"]:
                cg.offset_normalized_data_list[num][index] = (
                    cg.normalized_data_list[num][count][index] + Offset
                )

        #######################################################################
        # Elif the chosen normalization point is greater than the current ###
        # file, continue to normalize to the previous normalization point ###
        #######################################################################
        elif cg.InitializedNormalization:

            # Acquire the normalization point that was previously selected ###
            TempNormalizationPoint = cg.NormalizationVault[-1]
            TempNormalizationIndex = TempNormalizationPoint - 1

            cg.normalized_data_list[num][count][index] = (
                data / cg.data_list[num][count][TempNormalizationIndex]
            )

            ###########################################################################
            # If this is a low frequency, apply the offset to the normalized data ###
            ###########################################################################
            if cg.frequency_list[count] == cg.HighLowList["Low"]:
                cg.offset_normalized_data_list[num][index] = (
                    cg.normalized_data_list[num][count][index] + Offset
                )

        # --- Else, if the initial normalization point has not yet been reached,
        # normalize to the first file ---#
        elif not cg.InitializedNormalization:
            cg.normalized_data_list[num][count][index] = (
                data / cg.data_list[num][count][0]
            )

            ###########################################################################
            # If this is a low frequency, apply the offset to the normalized data ###
            ###########################################################################
            if cg.frequency_list[count] == cg.HighLowList["Low"]:
                cg.offset_normalized_data_list[num][index] = (
                    cg.normalized_data_list[num][count][index] + Offset
                )

    ################################################################
    # If the normalization point has been changed, renormalize ###
    # the data list to the new normalization point             ###
    ################################################################
    def RenormalizeData(self, file):
        ##############################################################
        # If the normalization point equals the current file,      ##
        # normalize all of the data to the new normalization point ##
        #############################################################
        if file == cg.NormalizationPoint:
            index = file - 1
            NormalizationIndex = cg.NormalizationPoint - 1
            for num in range(cg.electrode_count):
                for count in range(len(cg.frequency_list)):

                    cg.normalized_data_list[num][count][:index] = [
                        (idx / cg.data_list[num][count][NormalizationIndex])
                        for idx in cg.data_list[num][count][:index]
                    ]

                    ##################################################
                    # If the frequency is below cutoff_frequency, ###
                    # add the baseline Offset                     ###
                    ##################################################
                    if cg.frequency_list[count] == cg.HighLowList["Low"]:
                        for index in range(len(cg.file_list)):

                            ##########################
                            # Calculate the offset ##
                            ##########################
                            sample = cg.sample_list[index]
                            file = cg.file_list[index]
                            if cg.XaxisOptions == "Experiment Time":
                                Offset = (
                                    sample * cg.LowFrequencySlope
                                ) + cg.LowFrequencyOffset
                            elif cg.XaxisOptions == "File Number":
                                Offset = (
                                    file * cg.LowFrequencySlope
                                ) + cg.LowFrequencyOffset

                            cg.offset_normalized_data_list[num][index] = (
                                cg.normalized_data_list[num][count][index] + Offset
                            )

            ################################################
            # Analyze KDM using new normalization data ###
            ################################################
            if len(cg.frequency_list) > 1:
                self.ResetRatiometricData()

            ###############################
            # GUI Normalization Label ###
            ###############################
            cg.NormWarning["fg"] = "green"
            cg.NormWarning["text"] = "Normalized to file %s" % str(
                cg.NormalizationPoint
            )

            ########################################################################
            # If .txt file export has been activated, update the exported data ###
            ########################################################################
            if cg.SaveVar:
                cg.text_file_export.TxtFileNormalization()

        #########################################################################
        # If the Normalization Point has been changed and the current file is ##
        # greater than the new point, renormalize the data to the new point   ##
        #########################################################################
        if cg.NormalizationWaiting:
            index = file - 1
            NormalizationIndex = cg.NormalizationPoint - 1
            for num in range(cg.electrode_count):
                for count in range(len(cg.frequency_list)):

                    ##########################
                    # Renormalize the data ##
                    ##########################
                    cg.normalized_data_list[num][count][:index] = [
                        idx / cg.data_list[num][count][NormalizationIndex]
                        for idx in cg.data_list[num][count][:index]
                    ]
                    ##################################################
                    # If the frequency is below cutoff_frequency,  ##
                    # add the baseline Offset                      ##
                    ##################################################
                    if cg.frequency_list[count] == cg.HighLowList["Low"]:
                        for index in range(len(cg.file_list)):

                            ##########################
                            # Calculate the offset ##
                            ##########################
                            sample = cg.sample_list[index]
                            file = index + 1

                            if cg.XaxisOptions == "Experiment Time":
                                Offset = (
                                    sample * cg.LowFrequencySlope
                                ) + cg.LowFrequencyOffset
                            elif cg.XaxisOptions == "File Number":
                                Offset = (
                                    file * cg.LowFrequencySlope
                                ) + cg.LowFrequencyOffset

                            cg.offset_normalized_data_list[num][index] = (
                                cg.normalized_data_list[num][count][index] + Offset
                            )

            ################################################
            # Using the newly normalized data, calculate ##
            # the Normalized Ratio and KDM               ##
            # for each file that has been analyzed       ##
            ################################################
            if len(cg.frequency_list) > 1:
                self.ResetRatiometricData()

            # --- Indicate that the data has been normalized to the
            # new NormalizationPoint ---#
            cg.NormWarning["fg"] = "green"
            cg.NormWarning["text"] = "Normalized to file %s" % str(
                cg.NormalizationPoint
            )
            cg.wait_time.NormalizationProceed()

            # -- if .txt file export has been activated, update the exported data ---#
            if cg.SaveVar:
                cg.text_file_export.TxtFileNormalization()

    #############################################################
    # Readjust the data to the new user-inputted parameters ###
    #############################################################
    def ResetRatiometricData(self):

        ############################################
        # Readjust Low Frequencies with Offset ###
        ############################################

        # -- Iterate through every frequency --#
        for frequency in cg.frequency_list:

            # -- Only apply the offset if the frequency is below cutoff_frequency --#
            if frequency == cg.HighLowList["Low"]:
                count = cg.frequency_dict[frequency]

                # -- Apply the offset to every file --#
                for index in range(len(cg.file_list)):

                    sample = cg.sample_list[index]
                    file = cg.file_list[index]

                    if cg.XaxisOptions == "Experiment Time":
                        Offset = (sample * cg.LowFrequencySlope) + cg.LowFrequencyOffset
                    elif cg.XaxisOptions == "File Number":
                        Offset = (file * cg.LowFrequencySlope) + cg.LowFrequencyOffset

                    for num in range(cg.electrode_count):
                        cg.offset_normalized_data_list[num][
                            index
                        ] = cg.normalized_data_list[num][count][index] + float(Offset)

        ####################################################
        # Readjust KDM with newly adjusted frequencies ###
        ####################################################
        for file in cg.file_list:
            index = file - 1
            for num in range(cg.electrode_count):

                # grab the index value for the current high and low frequencies
                # used for ratiometric analysis #
                HighCount = cg.frequency_dict[cg.HighFrequency]

                HighPoint = cg.normalized_data_list[num][HighCount][index]
                LowPoint = cg.offset_normalized_data_list[num][index]

                NormalizedDataRatio = HighPoint / LowPoint
                cg.normalized_ratiometric_data_list[num][index] = NormalizedDataRatio

                # -- KDM ---#
                KDM = (HighPoint - LowPoint) + 1
                cg.KDM_list[num][index] = KDM

        # -- if .txt file export has been activated, update the exported data ---#
        if cg.SaveVar:
            if not cg.analysis_complete:
                cg.text_file_export.TxtFileNormalization()


##################################################
# Post Analysis Module for data manipulation ###
# after the completion of data analysis      ###
##################################################


class PostAnalysis(tk.Frame):
    def __init__(self, parent, container):

        ############################
        # Class-wide variables ###
        ############################
        self.parent = parent
        self.container = container

        # -- global boolean to control activation of this class --#
        cg.analysis_complete = False
        self.ExportTopLevelExists = False

        # -- once completion value == electrode_count, analysis_complete --#
        # -- will be changed from False to True                          --#
        self.completion_value = 0

        # --- Check for the presence of high and low frequencies ---#
        if cg.frequency_list[-1] > cutoff_frequency:
            self.High = True
        else:
            self.High = False

        if cg.frequency_list[0] <= cutoff_frequency:
            self.Low = True
        else:
            self.Low = False

        ##########################################
        # Initialize the Post Analysis Frame ###
        ##########################################
        self._initialize_frame()

    def _initialize_frame(self):

        ###################################################
        # Initialize the Frame and create its Widgets ###
        ###################################################
        tk.Frame.__init__(self, self.parent)  # initialize the frame

        self.Title = tk.Label(self, text="Post Analysis", font=HUGE_FONT).grid(
            row=0, column=0, columnspan=2
        )

        DataAdjustmentFrame = tk.Frame(self, relief="groove", bd=3)
        DataAdjustmentFrame.grid(
            row=1, column=0, columnspan=2, pady=5, ipadx=50, padx=2, sticky="ns"
        )

        NormalizationFrame = tk.Frame(DataAdjustmentFrame)
        NormalizationFrame.grid(row=1, column=0, pady=5)

        # --- Real-time Normalization Variable ---#
        cg.SetPointNormLabel = tk.Label(
            NormalizationFrame, text="Set Normalization Point", font=MEDIUM_FONT
        ).grid(row=0, column=0, pady=5)
        cg.NormalizationVar = tk.StringVar()
        NormString = str(cg.NormalizationPoint)
        cg.NormalizationVar.set(NormString)
        self.SetPointNorm = ttk.Entry(
            NormalizationFrame, textvariable=cg.NormalizationVar, width=8
        )
        self.SetPointNorm.grid(row=1, column=0, pady=5)
        cg.SetPointNorm = self.SetPointNorm

        # --- Button to apply any changes to the normalization variable ---#
        NormalizeButton = ttk.Button(
            NormalizationFrame,
            text="Apply Norm",
            command=self.PostAnalysisNormalization,  # lambda
            width=10,
        )
        NormalizeButton.grid(row=2, column=0)
        self.NormWarning = tk.Label(
            NormalizationFrame, text="", fg="red", font=MEDIUM_FONT
        )
        cg.NormWarning = self.NormWarning

        if len(cg.frequency_list) > 1:

            self.FrequencyFrame = tk.Frame(DataAdjustmentFrame, relief="groove", bd=3)
            self.FrequencyFrame.grid(row=2, column=0, pady=10, padx=3, ipady=2)

            # --- Drift Correction Title ---#
            self.KDM_title = tk.Label(
                self.FrequencyFrame, text="Drift Correction", font=LARGE_FONT
            )
            self.KDM_title.grid(row=0, column=0, columnspan=3, pady=1, padx=5)

            # --- High Frequency Selection for KDM and Ratiometric Analysis ---#
            self.HighFrequencyLabel = tk.Label(
                self.FrequencyFrame, text="High Frequency", font=MEDIUM_FONT
            )
            self.HighFrequencyLabel.grid(row=1, column=1, pady=5, padx=5)

            self.HighFrequencyEntry = tk.Entry(self.FrequencyFrame, width=7)
            self.HighFrequencyEntry.insert(tk.END, cg.HighFrequency)
            self.HighFrequencyEntry.grid(row=2, column=1, padx=5)

            # --- Low Frequency Selection for KDM and Ratiometric Analysis ---#
            self.LowFrequencyLabel = tk.Label(
                self.FrequencyFrame, text="Low Frequency", font=MEDIUM_FONT
            )
            self.LowFrequencyLabel.grid(row=1, column=0, pady=5, padx=5)

            self.LowFrequencyEntry = tk.Entry(self.FrequencyFrame, width=7)
            self.LowFrequencyEntry.insert(tk.END, cg.LowFrequency)
            self.LowFrequencyEntry.grid(row=2, column=0, padx=5)

            self.LowFrequencyOffsetLabel = tk.Label(
                self.FrequencyFrame, text="Low Frequency\n Offset", font=MEDIUM_FONT
            ).grid(row=3, column=0, pady=2, padx=2)
            self.LowFrequencyOffset = tk.Entry(self.FrequencyFrame, width=7)
            self.LowFrequencyOffset.insert(tk.END, cg.LowFrequencyOffset)
            self.LowFrequencyOffset.grid(row=4, column=0, padx=2, pady=2)

            self.LowFrequencySlopeLabel = tk.Label(
                self.FrequencyFrame,
                text="Low Frequency\n Slope Manipulation",
                font=MEDIUM_FONT,
            ).grid(row=3, column=1, pady=2, padx=2)
            self.LowFrequencySlope = tk.Entry(self.FrequencyFrame, width=7)
            self.LowFrequencySlope.insert(tk.END, cg.LowFrequencySlope)
            self.LowFrequencySlope.grid(row=4, column=1, padx=2, pady=2)

            self.ApplyFrequencies = ttk.Button(
                self.FrequencyFrame,
                text="Apply Frequencies",
                command=self.PostAnalysisKDM,  # lambda
            )
            self.ApplyFrequencies.grid(row=5, column=0, columnspan=2, pady=5, padx=5)

        self.RedrawButton = ttk.Button(
            DataAdjustmentFrame,
            text="Redraw Figures",
            command=self._draw,  # lambda
            width=12,
        )
        self.RedrawButton.grid(row=3, column=0, pady=7)

        DataAdjustmentFrame.columnconfigure(0, weight=1)
        row_value = 3

        self.DataExportFrame = tk.Frame(self, relief="groove", bd=2)
        self.DataExportFrame.grid(row=row_value, column=0, pady=5, ipady=5)

        self.DataExportSettings = tk.Button(
            self.DataExportFrame,
            text="Data Export Settings",
            command=lambda: self.DataExportTopLevel,
        )

        # ---Buttons to switch between electrode frames---#
        frame_value = 0
        column_value = 0
        for value in cg.PlotValues:
            Button = ttk.Button(
                self,
                text=cg.frame_list[frame_value],
                command=lambda frame_value=frame_value: self.show_plot(
                    cg.PlotValues[frame_value]
                ),
            )
            Button.grid(row=row_value, column=column_value, pady=2, padx=5)

            # allows .grid() to alternate between
            # packing into column 1 and column 2
            if column_value == 1:
                column_value = 0
                row_value += 1

            # if gridding into the 1st column,
            # grid the next into the 2nd column
            else:
                column_value += 1
            frame_value += 1
        row_value += 1

        ExportSettings = tk.Frame(self)
        ExportSettings.grid(row=row_value, column=0, columnspan=2, pady=5, ipady=10)

        ExportSettingsButton = tk.Button(
            ExportSettings,
            text="Post Analysis Data Export",
            command=self.DataExportTopLevel,
        )
        ExportSettingsButton.grid(row=0, column=0, padx=5)

        ExportSettings.columnconfigure(1, weight=1)
        ExportSettings.rowconfigure(1, weight=1)

        row_value += 1

        # --- Reset ---#
        Reset = ttk.Button(
            self, text="Reset", style="Fun.TButton", command=self._reset  # lambda
        )
        Reset.grid(row=row_value, column=1, pady=5, padx=5)

        # --- Quit ---#
        QuitButton = ttk.Button(self, text="Quit Program", command=quit)  # lambda
        QuitButton.grid(row=row_value, column=0, pady=5)

        for row in range(row_value):
            row += 1
            self.rowconfigure(row, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def _analysis_finished(self):

        self.completion_value += 1

        if self.completion_value == cg.electrode_count:
            cg.analysis_complete = True

            #####################################
            # Raise the Post Analysis Frame ###
            #####################################
            cg.ShowFrames[PostAnalysis].tkraise()

    def _adjust_data(self):

        ###################################
        # Renormalize all of the data ###
        ###################################
        NormalizationIndex = cg.NormalizationPoint - 1

        if cg.NormalizationPoint <= cg.numFiles:
            for num in range(cg.electrode_count):
                for count in range(len(cg.frequency_list)):
                    cg.normalized_data_list[num][count] = [
                        (idx / cg.data_list[num][count][NormalizationIndex])
                        for idx in cg.data_list[num][count]
                    ]
                    ##################################################
                    # If the frequency is below cutoff_frequency,  ##
                    # add the baseline Offset                      ##
                    ##################################################
                    if cg.frequency_list[count] == cg.HighLowList["Low"]:
                        for index in range(cg.numFiles):

                            ##########################
                            # Calculate the offset ##
                            ##########################
                            sample = cg.sample_list[index]
                            file = cg.file_list[index]

                            if cg.XaxisOptions == "Experiment Time":
                                Offset = (
                                    sample * cg.LowFrequencySlope
                                ) + cg.LowFrequencyOffset
                            elif cg.XaxisOptions == "File Number":
                                Offset = (
                                    file * cg.LowFrequencySlope
                                ) + cg.LowFrequencyOffset

                            cg.offset_normalized_data_list[num][index] = (
                                cg.normalized_data_list[num][count][index] + Offset
                            )

        cg.data_normalization.ResetRatiometricData()

        self.NormWarning["fg"] = "green"
        self.NormWarning["text"] = "Normalized to File %d" % cg.NormalizationPoint

        if cg.SaveVar:
            cg.text_file_export.TxtFileNormalization()

        # Draw the readjusted data
        self._draw()

    def _draw(self):

        for num in range(cg.electrode_count):

            # get the figure for the electrode ##
            fig, ax = cg.figures[num]

            subplot_count = 0
            for count in range(len(cg.frequency_list)):

                frequency = cg.frequency_list[count]

                ###################################
                # Set the units of the X-axis ###
                ###################################
                if cg.XaxisOptions == "Experiment Time":
                    Xaxis = cg.sample_list
                elif cg.XaxisOptions == "File Number":
                    Xaxis = cg.file_list

                ################################################################
                # Acquire the artists for this electrode at this frequency ###
                # and get the data that will be visualized                 ###
                ################################################################
                plots = cg.plot_list[num][count]  # 'count' is the frequency index value

                ##########################
                # Visualize the data ###
                ##########################

                # --- Peak Height ---#

                data = cg.data_list[num][count]  # 'num' is the electrode index value

                if cg.frequency_list[count] == cg.HighLowList["Low"]:
                    NormalizedDataList = cg.offset_normalized_data_list[num]
                else:
                    NormalizedDataList = cg.normalized_data_list[num][count]

                # Draw new data ###
                ax[1, subplot_count].clear()
                cg.peak = ax[1, subplot_count].plot(Xaxis, data, "bo", markersize=1)

                ax[2, subplot_count].clear()
                cg.norm = ax[2, subplot_count].plot(
                    Xaxis, NormalizedDataList, "ko", markersize=1
                )

                #####################
                # Set the Y Label ##
                #####################
                ax[0, 0].set_ylabel("Current\n(µA)", fontweight="bold")
                if cg.SelectedOptions == "Peak Height Extraction":
                    ax[1, 0].set_ylabel("Peak Height\n(µA)", fontweight="bold")
                elif cg.SelectedOptions == "Area Under the Curve":
                    ax[1, 0].set_ylabel("AUC (a.u.)", fontweight="bold")
                ax[2, 0].set_ylabel("Normalized", fontweight="bold")

                # If necessary, redraw ratiometric data ###
                if len(cg.frequency_list) > 1:
                    ratio_fig, ratio_ax = cg.ratiometric_figures[num]

                    cg.norm = [
                        X * 100 for X in cg.normalized_ratiometric_data_list[num]
                    ]
                    KDM = [X * 100 for X in cg.KDM_list[num]]

                    # -- Clear the Plots --#
                    ratio_ax[0, 0].clear()
                    ratio_ax[0, 1].clear()

                    # -- Redraw the titles --#
                    ratio_ax[0, 0].set_title("Normalized Ratio")
                    ratio_ax[0, 1].set_title("KDM")
                    ratio_ax[0, 0].set_ylabel("% Signal", fontweight="bold")
                    ratio_ax[0, 1].set_ylabel("% Signal", fontweight="bold")

                    # -- Plot the Data --#
                    ratio_ax[0, 0].plot(
                        Xaxis, cg.norm, "ro", markersize=1
                    )  # normalized ratio of high and low freq'
                    ratio_ax[0, 1].plot(Xaxis, KDM, "ro", markersize=1)

                subplot_count += 1

            fig.canvas.draw_idle()

            if len(cg.frequency_list) > 1:

                ratio_fig.canvas.draw_idle()

    #########################################################
    # Post Analysis adjustment of High and Low          ###
    # frequencies used for KDM and ratiometric analysis ###
    #########################################################
    def PostAnalysisKDM(self):

        cg.HighFrequency = int(self.HighFrequencyEntry.get())
        cg.LowFrequency = int(self.LowFrequencyEntry.get())

        cg.LowFrequencyOffset = float(self.LowFrequencyOffset.get())
        cg.LowFrequencySlope = float(self.LowFrequencySlope.get())

        # --- Reset the variable for the Warning Label (WrongFrequencyLabel) ---#
        CheckVar = 0

        if int(cg.HighFrequency) not in cg.frequency_list:
            CheckVar += 3

        if int(cg.LowFrequency) not in cg.frequency_list:
            CheckVar += 1

        # --- if only the HighFrequency does not exist ---#
        if CheckVar == 3:
            if cg.ExistVar:
                cg.WrongFrequencyLabel.grid_forget()
            cg.WrongFrequencyLabel = tk.Label(
                self.FrequencyFrame, text="High Frequency Does Not Exist", fg="red"
            )
            cg.WrongFrequencyLabel.grid(row=6, column=0, columnspan=4)
            if not cg.ExistVar:
                cg.ExistVar = True

        # --- if only the LowFrequency does not exist ---#
        elif CheckVar == 1:
            if cg.ExistVar:
                cg.WrongFrequencyLabel.grid_forget()
            cg.WrongFrequencyLabel = tk.Label(
                self.FrequencyFrame, text="Low Frequency Does Not Exist", fg="red"
            )
            cg.WrongFrequencyLabel.grid(row=6, column=0, columnspan=4)
            if not cg.ExistVar:
                cg.ExistVar = True

        # --- if both the HighFrequency and LowFrequency do not exist ---#
        elif CheckVar == 4:
            if cg.ExistVar:
                cg.WrongFrequencyLabel.grid_forget()
            cg.WrongFrequencyLabel = tk.Label(
                self.FrequencyFrame,
                text="High and Low Frequencies Do Not Exist",
                fg="red",
            )
            cg.WrongFrequencyLabel.grid(row=6, column=0, columnspan=4)
            if not cg.ExistVar:
                cg.ExistVar = True

        # --- else, if they both exist, remove the warning label ---#
        else:
            cg.HighLowList["High"] = cg.HighFrequency
            cg.HighLowList["Low"] = cg.LowFrequency

            cg.data_normalization.ResetRatiometricData()

            # --- if a warning label exists, forget it ---#
            if cg.ExistVar:
                cg.WrongFrequencyLabel.grid_forget()

            # --- Tells RawVoltammogramVisualization to revisualize data for
            # new High and Low frequencies ---#
            if not cg.RatioMetricCheck:
                cg.RatioMetricCheck = True

            self._adjust_data()

    # --- Function for Real-time Normalization ---#
    def PostAnalysisNormalization(self):

        cg.NormalizationPoint = int(self.SetPointNorm.get())
        file = int(cg.FileLabel["text"])
        index = file - 1

        if file >= cg.NormalizationPoint:
            cg.wait_time.NormalizationWaitTime()

        elif cg.NormalizationPoint > file:
            cg.NormWarning["fg"] = "red"
            cg.NormWarning["text"] = "File %s has \nnot been analyzed" % str(
                cg.NormalizationPoint
            )

        if cg.analysis_complete:
            cg.post_analysis._adjust_data()

    ######################################################
    # Data Export TopWindow and Associated Functions ###
    ######################################################

    def DataExportTopLevel(self):

        self.win = tk.Toplevel()
        self.win.wm_title("Post Analysis Data Export")

        self.ExportTopLevelExists = True

        ##############################################
        # Pack all of the widgets into the frame ###
        ##############################################

        # --- File Path ---#
        self.SelectFilePath = ttk.Button(
            self.win,
            style="On.TButton",
            text="%s" % cg.DataFolder,
            command=lambda: self.FindFile(self.parent),
        )
        self.SelectFilePath.grid(row=0, column=0, columnspan=2)

        self.NoSelectedPath = tk.Label(
            self.win, text="No File Path Selected", font=MEDIUM_FONT, fg="red"
        )
        self.PathWarningExists = False  # tracks the existence of a warning label

        # --- File Handle Input ---#
        HandleLabel = tk.Label(self.win, text="Exported File Handle:", font=LARGE_FONT)
        HandleLabel.grid(row=4, column=0, columnspan=2)
        self.filehandle = ttk.Entry(self.win)
        self.filehandle.insert(tk.END, cg.FileHandle)
        self.filehandle.grid(row=5, column=0, columnspan=2, pady=5)

        self.ElectrodeLabel = tk.Label(
            self.win, text="Select Electrodes:", font=LARGE_FONT
        )
        self.ElectrodeLabel.grid(row=10, column=0, sticky="nswe")
        self.ElectrodeCount = tk.Listbox(
            self.win,
            relief="groove",
            exportselection=0,
            width=10,
            font=LARGE_FONT,
            height=6,
            selectmode="multiple",
            bd=3,
        )
        self.ElectrodeCount.bind("<<ListboxSelect>>", self.ElectrodeCurSelect)
        self.ElectrodeCount.grid(row=11, column=0, padx=10, sticky="nswe")
        for electrode in cg.electrode_list:
            self.ElectrodeCount.insert(tk.END, electrode)

        # --- ListBox containing the frequencies given on line 46 (InputFrequencies)-#

        self.FrequencyLabel = tk.Label(
            self.win, text="Select Frequencies", font=LARGE_FONT
        )
        self.FrequencyLabel.grid(row=10, column=1, padx=10)
        self.FrequencyList = tk.Listbox(
            self.win,
            relief="groove",
            exportselection=0,
            width=5,
            font=LARGE_FONT,
            height=5,
            selectmode="multiple",
            bd=3,
        )
        self.FrequencyList.bind("<<ListboxSelect>>", self.FrequencyCurSelect)
        self.FrequencyList.grid(row=11, column=1, padx=10, sticky="nswe")
        for frequency in cg.frequency_list:
            self.FrequencyList.insert(tk.END, frequency)

        ExportData = tk.Button(
            self.win, text="Export Data", command=self.PostAnalysisDataExport  # lambda
        )
        ExportData.grid(row=15, column=0, columnspan=2)

        CloseButton = tk.Button(
            self.win, text="Close", command=self.win.destroy  # lambda
        )
        CloseButton.grid(row=16, column=0, columnspan=2, pady=10)

    def ElectrodeCurSelect(self, evt):

        ###################################################
        # electrode_list: list; ints                    ##
        # electrode_dict: dict; {electrode: index}      ##
        # electrode_count: int                          ##
        ###################################################

        self.electrode_list = [
            self.ElectrodeCount.get(idx) for idx in self.ElectrodeCount.curselection()
        ]
        self.electrode_list = [int(electrode) for electrode in self.electrode_list]

        if cg.electrode_count == 0:
            self.ElectrodeListExists = False
            self.ElectrodeLabel["fg"] = "red"

        elif cg.electrode_count != 0:
            self.ElectrodeListExists = True
            self.ElectrodeLabel["fg"] = "black"

    # --- Frequency Selection ---#
    def FrequencyCurSelect(self, evt):
        self.frequency_list = [
            self.FrequencyList.get(idx) for idx in self.FrequencyList.curselection()
        ]

        if len(cg.frequency_list) != 0:

            self.FrequencyListExists = True
            self.FrequencyLabel["fg"] = "black"

            for var in cg.frequency_list:
                var = int(var)

        elif len(cg.frequency_list) == 0:
            self.FrequencyListExists = False
            self.FrequencyLabel["fg"] = "red"

    def FindFile(self, parent):
        try:

            # prompt the user to select a  ###
            # directory for  data analysis ###
            cg.FilePath = filedialog.askdirectory(parent=parent)
            cg.FilePath = "".join(cg.FilePath + "/")

            # Path for directory in which the    ###
            # exported .txt file will be placed  ###
            cg.ExportPath = cg.FilePath.split("/")

            # -- change the text of the find file button to the folder the user chose -#
            cg.DataFolder = "%s/%s" % (cg.ExportPath[-3], cg.ExportPath[-2])

            self.SelectFilePath["style"] = "On.TButton"
            self.SelectFilePath["text"] = cg.DataFolder

            del cg.ExportPath[-1]
            cg.ExportPath = "/".join(cg.ExportPath)
            cg.ExportPath = "".join(cg.ExportPath + "/")
            # Indicates that the user has selected a File Path ###
            cg.FoundFilePath = True

            if self.PathWarningExists:
                self.NoSelectedPath["text"] = ""
                self.NoSelectedPath.grid_forget()

        except:
            cg.FoundFilePath = False
            self.NoSelectedPath.grid(row=1, column=0, columnspan=4)
            self.PathWarningExists = True
            self.SelectFilePath["style"] = "Off.TButton"
            self.SelectFilePath["text"] = ""

    def PostAnalysisDataExport(self):

        FileHandle = str(self.filehandle.get())
        cg.ExportFilePath = "".join(cg.ExportPath + FileHandle)

        post_analysis_export = TextFileExport(
            electrodes=self.electrode_list, frequencies=self.frequency_list
        )
        post_analysis_export.TxtFileNormalization(
            electrodes=self.electrode_list, frequencies=self.frequency_list
        )

    def _reset(self):

        self.completion_value = 0
        cg.analysis_complete = False

        if self.ExportTopLevelExists is True:
            self.win.destroy()

        cg.key = 0
        cg.PoisonPill = True
        cg.AlreadyInitiated = False  # reset the start variable

        if self.High:
            cg.HighAlreadyReset = True

        if self.Low:
            cg.LowAlreadyReset = True

        # Raise the initial user input frame
        self.show_frame(InputFrame)
        self.close_frame(PostAnalysis)

        # Take resize weight away from the Visualization Canvas
        cg.container.columnconfigure(1, weight=0)

    # --- Function to switch between visualization frames ---#
    def show_plot(self, frame):
        frame.tkraise()

    def show_frame(self, cont):

        frame = cg.ShowFrames[cont]
        frame.tkraise()

    #####################################
    # Destory the frames on Reset() ###
    #####################################
    def close_frame(self, cont):
        frame = cg.ShowFrames[cont]
        frame.grid_forget()

        # close all matplotlib figures
        plt.close("all")

        # destory the frames holding the figures
        for frame in cg.PlotValues:
            frame.destroy()

        # destory the container holding those frames
        cg.PlotContainer.destroy()


# ------------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------------#


###############################################################################
###############################################################################
# Classes and Functions for Real-Time Tracking and Text File Export ######
###############################################################################
###############################################################################


class WaitTime:
    def __init__(self):

        cg.NormalizationWaiting = False

    def NormalizationWaitTime(self):

        cg.NormalizationWaiting = True

    def NormalizationProceed(self):

        cg.NormalizationWaiting = False


class Track:
    def __init__(self):

        self.track_list = [1] * cg.numFiles

    def tracking(self, file, frequency):

        index = file - 1

        if self.track_list[index] == cg.electrode_count:

            if cg.method == "Continuous Scan":

                # Global File List
                _update_global_lists(file)

                HighFrequency = cg.HighLowList["High"]
                LowFrequency = cg.HighLowList["Low"]

                cg.data_normalization.RenormalizeData(file)

                if cg.SaveVar:
                    cg.text_file_export.ContinuousScanExport(file)

                # --- if the high and low frequencies have been changed,
                # adjust the data ---#
                if cg.RatioMetricCheck:

                    cg.data_normalization.ResetRatiometricData()

                    # -- if the data is being exported,
                    # reset the exported data file --#
                    if cg.SaveVar:
                        cg.text_file_export.TxtFileNormalization()

                    cg.RatioMetricCheck = False

            elif cg.method == "Frequency Map":

                if self.track_list[index] == cg.electrode_count:

                    if cg.SaveVar:
                        cg.text_file_export.FrequencyMapExport(file, frequency)

            self.track_list[index] = 1

        else:
            self.track_list[index] += 1


# ------------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------------#


################################################
################################################
# Functions for Real Time Text File Export ###
################################################
################################################


##################################
# Real-Time Text File Export ###
##################################
class TextFileExport:

    ###############################
    # Initialize the .txt file ###
    ###############################
    def __init__(self, electrodes=None, frequencies=None):

        if electrodes is None:
            self.electrode_list = cg.electrode_list
        else:
            self.electrode_list = electrodes

        self.electrode_count = len(self.electrode_list)

        if frequencies is None:
            self.frequency_list = cg.frequency_list
        else:
            self.frequency_list = frequencies

        self.TextFileHandle = cg.ExportFilePath

        if cg.method == "Continuous Scan":
            TxtList = []
            TxtList.append("File")
            TxtList.append("Time(Hrs)")

            for frequency in self.frequency_list:
                for electrode in self.electrode_list:
                    if cg.SelectedOptions == "Peak Height Extraction":
                        TxtList.append("PeakHeight_E%d_%dHz" % (electrode, frequency))
                    elif cg.SelectedOptions == "Area Under the Curve":
                        TxtList.append("AUC_E%d_%dHz" % (electrode, frequency))

            if self.electrode_count > 1:
                for frequency in self.frequency_list:
                    if cg.SelectedOptions == "Peak Height Extraction":
                        TxtList.append("Avg_PeakHeight_%dHz" % frequency)
                    elif cg.SelectedOptions == "Area Under the Curve":
                        TxtList.append("Avg_AUC_%dHz" % frequency)

            for frequency in self.frequency_list:
                for electrode in self.electrode_list:
                    TxtList.append("Norm_E%d_%dHz" % (electrode, frequency))

            if self.electrode_count > 1:
                for frequency in self.frequency_list:
                    TxtList.append("Average_Norm_%dHz" % frequency)

                for frequency in self.frequency_list:
                    TxtList.append("SD_Norm_%dHz" % frequency)

            if len(self.frequency_list) > 1:
                for electrode in self.electrode_list:
                    TxtList.append("NormalizedRatio_E%d" % electrode)

                if self.electrode_count > 1:
                    TxtList.append("NormalizedRatioAvg")
                    TxtList.append("NormalizedRatioSTD")

                for electrode in self.electrode_list:
                    TxtList.append("KDM_E%d" % electrode)

                if self.electrode_count > 1:
                    TxtList.append("AvgKDM")
                    TxtList.append("KDM_STD")

            with open(
                self.TextFileHandle, "w+", encoding="utf-8", newline=""
            ) as our_input:
                writer = csv.writer(our_input, delimiter=" ")
                writer.writerow(TxtList)

        elif cg.method == "Frequency Map":

            TxtList = []
            TxtList.append("Frequency(Hz)")

            E_count = 1
            for electrode in cg.frame_list:
                if cg.SelectedOptions == "Peak Height Extraction":
                    TxtList.append("PeakHeight_E%d(uA)" % (E_count))
                elif cg.SelectedOptions == "Area Under the Curve":
                    TxtList.append("AUC_E%d" % (E_count))
                TxtList.append("Charge_E%d(uC)" % (E_count))
                E_count += 1

            if self.electrode_count > 1:
                TxtList.append("Avg.PeakHeight(uA)")
                TxtList.append("Standard_Deviation(uA)")
                TxtList.append("Avg.Charge(uC)")
                TxtList.append("Standard_Deviation(uC)")

            with open(self.TextFileHandle, "w+", encoding="utf-8", newline="") as input:
                writer = csv.writer(input, delimiter=" ")
                writer.writerow(TxtList)

    #################################################################
    # Write the data from the current file into the Export File ###
    #################################################################
    def ContinuousScanExport(self, _file_):

        index = _file_ - 1
        our_list = []
        AvgList = []
        our_list.append(str(_file_))
        our_list.append(str((_file_ * cg.SampleRate) / 3600))
        # --- Peak Height ---#
        for count in range(len(cg.frequency_list)):
            for num in range(cg.electrode_count):
                our_list.append(cg.data_list[num][count][index])

        # --- Avg. Peak Height ---#
        if self.electrode_count > 1:
            for count in range(len(cg.frequency_list)):
                average = 0
                for num in range(cg.electrode_count):
                    average += cg.data_list[num][count][index]
                average = average / cg.electrode_count
                our_list.append(average)

        # --- Peak Height/AUC Data Normalization ---#
        for count in range(len(cg.frequency_list)):
            for num in range(cg.electrode_count):
                if cg.frequency_list[count] == cg.HighLowList["Low"]:
                    our_list.append(cg.offset_normalized_data_list[num][index])
                else:
                    our_list.append(cg.normalized_data_list[num][count][index])

        # --- Average normalized data across all electrodes for each frequency ---#
        if self.electrode_count > 1:
            for count in range(len(cg.frequency_list)):
                NormalizedFrequencyCurrents = []
                for num in range(cg.electrode_count):
                    if cg.frequency_list[count] == cg.HighLowList["Low"]:
                        NormalizedFrequencyCurrents.append(
                            cg.offset_normalized_data_list[num][index]
                        )
                    else:
                        NormalizedFrequencyCurrents.append(
                            cg.normalized_data_list[num][count][index]
                        )

                # -- calculate the average
                average = 0  # start at 0
                for item in NormalizedFrequencyCurrents:
                    average += item  # add every item
                average = average / cg.electrode_count
                AverageNorm = sum(NormalizedFrequencyCurrents) / cg.electrode_count
                our_list.append(AverageNorm)

        # --- Standard Deviation ---#
        if self.electrode_count > 1:
            for count in range(len(cg.frequency_list)):
                NormalizedFrequencyCurrents = []
                for num in range(cg.electrode_count):
                    NormalizedFrequencyCurrents.append(
                        cg.normalized_data_list[num][count][index]
                    )

                AverageNorm = sum(NormalizedFrequencyCurrents) / cg.electrode_count
                STDList = [(X - AverageNorm) ** 2 for X in NormalizedFrequencyCurrents]
                StandardDeviation = float(
                    sqrt(sum(STDList) / (cg.electrode_count - 1))
                )  # standard deviation of a sample
                our_list.append(StandardDeviation)

        if len(cg.frequency_list) > 1:
            # --- Append Normalized Ratiometric Data ---#
            NormList = []

            for num in range(cg.electrode_count):
                our_list.append(cg.normalized_ratiometric_data_list[num][index])
                NormList.append(cg.normalized_ratiometric_data_list[num][index])

            if self.electrode_count > 1:
                NormAverage = sum(NormList) / cg.electrode_count
                our_list.append(NormAverage)

                NormSTDlist = [(X - NormAverage) ** 2 for X in NormList]
                NormStandardDeviation = sqrt(
                    sum(NormSTDlist) / (cg.electrode_count - 1)
                )  # standard deviation of a sample
                our_list.append(NormStandardDeviation)

            # --- Append KDM ---#
            KDMList = []
            for num in range(cg.electrode_count):
                our_list.append(cg.KDM_list[num][index])
                KDMList.append(cg.KDM_list[num][index])
            if self.electrode_count > 1:
                KDM_Average = sum(KDMList) / cg.electrode_count
                our_list.append(KDM_Average)
                KDM_STD_list = [(X - KDM_Average) ** 2 for X in KDMList]
                KDM_STD = sqrt(sum(KDM_STD_list) / (cg.electrode_count - 1))
                our_list.append(KDM_STD)

        # --- Write the data into the .txt file ---#
        with open(self.TextFileHandle, "a", encoding="utf-8", newline="") as our_input:
            writer = csv.writer(our_input, delimiter=" ")
            writer.writerow(our_list)
        with open(
            self.TextFileHandle, "r", encoding="utf-8", newline=""
        ) as filecontents:
            filedata = filecontents.read()
        filedata = filedata.replace("[", "")
        filedata = filedata.replace('"', "")
        filedata = filedata.replace("]", "")
        filedata = filedata.replace(",", "")
        filedata = filedata.replace("'", "")
        with open(self.TextFileHandle, "w", encoding="utf-8", newline="") as output:
            output.write(filedata)

    #################################################################
    # Write the data from the current file into the Export File ###
    #################################################################
    def FrequencyMapExport(self, file, frequency):

        our_list = []
        index = file - 1
        try:

            our_list.append(str(frequency))
            count = cg.frequency_dict[int(frequency)]

            # Peak Height / AUC
            for num in range(cg.electrode_count):
                our_list.append(cg.data_list[num][count][index])
                our_list.append(cg.data_list[num][count][index] / int(frequency))

            # Average Peak Height / AUC
            if self.electrode_count > 1:
                value = 0
                for num in range(cg.electrode_count):
                    value += cg.data_list[num][count][index]
                average = value / cg.electrode_count
                our_list.append(average)

                # Standard Deviation of a Sample across all electrodes
                # for Peak Height/AUC

                std_list = []
                for num in range(cg.electrode_count):
                    std_list.append(cg.data_list[num][count][index])

                std_list = [(value - average) ** 2 for value in std_list]

                standard_deviation = sqrt(sum(std_list) / (cg.electrode_count - 1))
                our_list.append(standard_deviation)

                # -- Average Charge --#
                avg_charge = average / int(frequency)
                our_list.append(avg_charge)

                # -- Charge STD --#
                std_list = []
                for num in range(cg.electrode_count):
                    std_list.append(cg.data_list[num][count][index])

                std_list = [x / int(frequency) for x in std_list]
                std_list = [(value - avg_charge) ** 2 for value in std_list]
                charge_standard_deviation = sqrt(
                    sum(std_list) / (cg.electrode_count - 1)
                )
                our_list.append(charge_standard_deviation)

            # --- Write the data into the .txt file ---#
            with open(
                self.TextFileHandle, "a", encoding="utf-8", newline=""
            ) as our_input:
                writer = csv.writer(our_input, delimiter=" ")
                writer.writerow(our_list)
            with open(
                self.TextFileHandle, "r", encoding="utf-8", newline=""
            ) as filecontents:
                filedata = filecontents.read()
            filedata = filedata.replace("[", "")
            filedata = filedata.replace('"', "")
            filedata = filedata.replace("]", "")
            filedata = filedata.replace(",", "")
            filedata = filedata.replace("'", "")
            with open(self.TextFileHandle, "w", encoding="utf-8", newline="") as output:
                output.write(filedata)

        except:
            print("\n\n", "ERROR IN FREQUENCY MAP TEXT FILE EXPORT", "\n\n")
            time.sleep(3)

    ###############################################
    # Normalize the data within the Text File ###
    ###############################################
    def TxtFileNormalization(self, electrodes=None, frequencies=None):
        TxtList = []

        try:
            # --- reinitialize the .txt file ---#
            self.__init__(
                electrodes=self.electrode_list, frequencies=self.frequency_list
            )

            # --- rewrite the data for the files that have already been analyzed
            # and normalize them to the new standard---#
            if cg.analysis_complete:
                analysis_range = len(cg.file_list)
            else:
                analysis_range = len(cg.file_list) - 1

            for index in range(analysis_range):
                _file_ = index + 1
                our_list = []
                AvgList = []
                our_list.append(str(_file_))
                our_list.append(str((_file_ * cg.SampleRate) / 3600))

                # --- peak height ---#
                for frequency in self.frequency_list:
                    count = cg.frequency_dict[frequency]
                    for electrode in self.electrode_list:
                        num = cg.electrode_dict[electrode]
                        our_list.append(cg.data_list[num][count][index])

                # --- Avg. Peak Height ---#
                if self.electrode_count > 1:
                    for frequency in self.frequency_list:
                        count = cg.frequency_dict[frequency]
                        average = 0
                        for electrode in self.electrode_list:
                            num = cg.electrode_dict[electrode]
                            average += cg.data_list[num][count][index]
                        average = average / self.electrode_count
                        our_list.append(average)

                # --- Data Normalization ---#
                for frequency in self.frequency_list:
                    count = cg.frequency_dict[frequency]
                    NormalizedFrequencyCurrents = []
                    for electrode in self.electrode_list:
                        num = cg.electrode_dict[electrode]

                        if frequency == cg.HighLowList["Low"]:
                            our_list.append(cg.offset_normalized_data_list[num][index])
                        else:
                            our_list.append(cg.normalized_data_list[num][count][index])

                # --- Average Data Normalization ---#
                if self.electrode_count > 1:
                    for frequency in self.frequency_list:
                        count = cg.frequency_dict[frequency]
                        NormalizedFrequencyCurrents = []
                        for electrode in self.electrode_list:
                            num = cg.electrode_dict[electrode]

                            if frequency == cg.HighLowList["Low"]:
                                NormalizedFrequencyCurrents.append(
                                    cg.offset_normalized_data_list[num][index]
                                )
                            else:
                                NormalizedFrequencyCurrents.append(
                                    cg.normalized_data_list[num][count][index]
                                )

                        AverageNorm = (
                            sum(NormalizedFrequencyCurrents) / self.electrode_count
                        )
                        our_list.append(AverageNorm)

                    # --- Standard Deviation between electrodes ---#
                    for frequency in self.frequency_list:
                        count = cg.frequency_dict[frequency]
                        NormalizedFrequencyCurrents = []
                        for electrode in self.electrode_list:
                            num = cg.electrode_dict[electrode]

                            if frequency == cg.HighLowList["Low"]:
                                NormalizedFrequencyCurrents.append(
                                    cg.offset_normalized_data_list[num][index]
                                )
                            else:
                                NormalizedFrequencyCurrents.append(
                                    cg.normalized_data_list[num][count][index]
                                )

                        AverageNorm = (
                            sum(NormalizedFrequencyCurrents) / self.electrode_count
                        )
                        STDList = [
                            (X - AverageNorm) ** 2 for X in NormalizedFrequencyCurrents
                        ]
                        StandardDeviation = sqrt(
                            sum(STDList) / (self.electrode_count - 1)
                        )
                        our_list.append(StandardDeviation)

                if len(self.frequency_list) > 1:

                    # --- Append Normalized Ratiometric Data ---#
                    NormList = []
                    for electrode in self.electrode_list:
                        num = cg.electrode_dict[electrode]

                        our_list.append(cg.normalized_ratiometric_data_list[num][index])
                        NormList.append(cg.normalized_ratiometric_data_list[num][index])

                    if self.electrode_count > 1:
                        NormAverage = sum(NormList) / self.electrode_count
                        our_list.append(NormAverage)

                        NormSTDlist = [(X - NormAverage) ** 2 for X in NormList]
                        NormStandardDeviation = sqrt(
                            sum(NormSTDlist) / (self.electrode_count - 1)
                        )  # standard deviation of a sample
                        our_list.append(NormStandardDeviation)

                    # --- Append KDM ---#
                    KDMList = []
                    for electrode in self.electrode_list:
                        num = cg.electrode_dict[electrode]

                        our_list.append(cg.KDM_list[num][index])
                        KDMList.append(cg.KDM_list[num][index])

                    if self.electrode_count > 1:
                        KDM_Average = sum(KDMList) / self.electrode_count
                        our_list.append(KDM_Average)

                        KDM_STD_list = [(X - KDM_Average) ** 2 for X in KDMList]
                        KDM_STD = sqrt(sum(KDM_STD_list) / (self.electrode_count - 1))
                        our_list.append(KDM_STD)

                # --- Write the data into the .txt file ---#
                with open(
                    self.TextFileHandle, "a", encoding="utf-8", newline=""
                ) as our_input:
                    writer = csv.writer(our_input, delimiter=" ")
                    writer.writerow(our_list)
                with open(
                    self.TextFileHandle, "r", encoding="utf-8", newline=""
                ) as filecontents:
                    filedata = filecontents.read()
                filedata = filedata.replace("[", "")
                filedata = filedata.replace('"', "")
                filedata = filedata.replace("]", "")
                filedata = filedata.replace(",", "")
                filedata = filedata.replace("'", "")
                with open(
                    self.TextFileHandle, "w", encoding="utf-8", newline=""
                ) as output:
                    output.write(filedata)

        except:
            print("\n", "ERROR IN TEXT FILE NORMALIZATION", "\n")
            time.sleep(0.1)


def _update_global_lists(file):

    if file not in cg.file_list:
        cg.file_list.append(file)

        sample = round(len(cg.file_list) * cg.SampleRate / 3600, 3)
        cg.sample_list.append(sample)
        cg.RealTimeSampleLabel["text"] = sample

        if file != cg.numFiles:
            cg.FileLabel["text"] = file + 1


# ------------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------------#


############################################
# Initialize GUI to start the program  ###
############################################

if __name__ == "__main__":

    root = tk.Tk()
    app = MainWindow(root)

    style = ttk.Style()
    style.configure(
        "On.TButton", foreground="blue", font=LARGE_FONT, relief="raised", border=100
    )
    style.configure(
        "Off.TButton", foreground="black", font=MEDIUM_FONT, relief="sunken", border=5
    )

    while True:
        # --- initiate the mainloop ---#
        try:
            root.mainloop()
        # --- escape scrolling error ---#
        except UnicodeDecodeError:
            pass

            # *########################################*#
            # *######## End of Program ############*#
            # *########################################*#
