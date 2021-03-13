#!/usr/bin/env python3
import tkinter as tk
import tkinter.ttk as ttk
from config import cg


def main():

    # cg = Config()
    # -- file handle variable --#
    # cg.handle_variable = ""  # default handle variable is nothing
    # cg.e_var = "single"  # default input file is 'Multichannel', or a single file
    # # containing all electrodes
    # PHE_method = "Abs"  # default PHE Extraction is difference between absolute max/min

    # # ------------------------------------------------------------#

    # cg.InputFrequencies = [
    #     30,
    #     80,
    #     240,
    # ]  # frequencies initially displayed in Frequency Listbox
    # cg.electrodes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]

    # # ------------------------------------------------------------------------------------#
    # # ------------------------------------------------------------------------------------#

    ########################
    # Global Variables ###
    ########################

    ########################################
    # Polynomial Regression Parameters ###
    ########################################
    # cg.sg_window = 5  # Savitzky-Golay window (in mV range),
    # # must be odd number (increase signal:noise)
    # cg.sg_degree = 1  # Savitzky-Golay polynomial degree
    # cg.polyfit_deg = 15  # degree of polynomial fit

    # cg.cutoff_frequency = 50  # frequency that separates 'low' and 'high'
    # # frequencies for regression analysis and
    # # smoothing manipulation

    # #############################
    # # Checkpoint Parameters ###
    # #############################
    # cg.key = 0  # SkeletonKey
    # search_lim = 15  # Search limit (sec)
    # cg.PoisonPill = False  # Stop Animation variable
    # cg.FoundFilePath = False  # If the user-inputted file is found
    # cg.ExistVar = False  # If Checkpoints are not met ExistVar = True
    # cg.AlreadyInitiated = False  # indicates if the user has already initiated analysis
    # cg.HighAlreadyReset = False  # If data for high frequencies has been reset
    # cg.LowAlreadyReset = False  # If data for low frequencies has been reset
    # cg.analysis_complete = False  # If analysis has completed, begin PostAnalysis

    # ##################################
    # # Data Extraction Parameters ###
    # ##################################
    # cg.delimiter = 1  # default delimiter is a space; 2 = tab
    # cg.extension = 1
    # cg.current_column = 4  # column index for list_val.
    # cg.current_column_index = 3
    # # list_val = column_index + 3
    # # defauly column is the second (so index = 1)
    # cg.voltage_column = 1
    # cg.voltage_column_index = 0
    # cg.spacing_index = 3

    # # -- set the initial limit in bytes to filter out preinitialized files < 3000b
    # cg.byte_limit = 3000
    # # - set the initial bite index to match the checkbutton
    # # - index in the toolbar menu MainWindow.byte_menu
    # cg.byte_index = 2

    # ######################################################
    # # Low frequency baseline manipulation Parameters ###
    # ######################################################
    # cg.LowFrequencyOffset = 0  # Vertical offset of normalized data for
    # # user specified 'Low Frequency'
    # cg.LowFrequencySlope = 0  # Slope manipulation of norm data for user
    # # specified 'Low Frequency'

    ###############
    # Styling ###
    ###############
    HUGE_FONT = ("Verdana", 18)
    LARGE_FONT = ("Verdana", 11)
    MEDIUM_FONT = ("Verdnana", 10)
    SMALL_FONT = ("Verdana", 8)

    cg.root = tk.Tk()
    from main_window import MainWindow

    _ = MainWindow(cg.root)

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
            cg.root.mainloop()
        # --- escape scrolling error ---#
        except UnicodeDecodeError:
            pass


if __name__ == "__main__":
    main()
