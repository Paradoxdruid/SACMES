#!/usr/bin/env python3

import tkinter as tk
from config import cg
import os
from post_analysis import PostAnalysis
from normalization import DataNormalization
from wait_time import Track, WaitTime
from initialization import InitializeContinuousCanvas, InitializeFrequencyMapCanvas
from scan_frames import ContinuousScanManipulationFrame, FrequencyMapManipulationFrame
from global_func import _retrieve_file


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

        _ = tk.Label(self.win, text="Searching for files...", font=cg.HUGE_FONT).grid(
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
                self.win, text="E%s" % electrode, font=cg.LARGE_FONT
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
                    frame, text="E%s" % electrode, font=cg.HUGE_FONT
                )
                electrode_label.grid(row=row_value, column=column_value, pady=5, padx=5)
                self.label_dict[electrode][cg.frequency_list[0]] = electrode_label
                self.already_verified[electrode][cg.frequency_list[0]] = False

                if column_value == 1:
                    column_value = 0
                    row_value += 1
                else:
                    column_value = 1

        self.stop_button = tk.Button(self.win, text="Stop", command=self.stop)
        self.stop_button.grid(row=row_value, column=0, columnspan=2, pady=5)
        self.StopSearch = False

        self.num = 0
        self.count = 0
        self.analysis_count = 0
        self.analysis_limit = cg.electrode_count * len(cg.frequency_list)
        self.electrode_limit = cg.electrode_count - 1
        self.frequency_limit = len(cg.frequency_list) - 1

        cg.root.after(50, self.verify)

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
                    except Exception:
                        try:
                            mydata_bytes = os.path.getsize(myfile2)
                            myfile = myfile2
                        except Exception:
                            try:
                                mydata_bytes = os.path.getsize(myfile3)
                                myfile = myfile3
                            except Exception:
                                try:
                                    mydata_bytes = os.path.getsize(myfile4)
                                    myfile = myfile4
                                except Exception:
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

                                cg.root.after(10, self.proceed)

                if self.num < self.electrode_limit:
                    self.num += 1

                else:
                    self.num = 0

                if self.analysis_count < self.analysis_limit:
                    if not self.StopSearch:
                        cg.root.after(100, self.verify)

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
                except Exception:
                    try:
                        mydata_bytes = os.path.getsize(myfile2)
                        myfile = myfile2
                    except Exception:
                        try:
                            mydata_bytes = os.path.getsize(myfile3)
                            myfile = myfile3
                        except Exception:
                            try:
                                mydata_bytes = os.path.getsize(myfile4)
                                myfile = myfile4
                            except Exception:
                                try:
                                    mydata_bytes = os.path.getsize(myfile5)
                                    myfile = myfile5
                                except Exception:
                                    try:
                                        mydata_bytes = os.path.getsize(myfile6)
                                        myfile = myfile6
                                    except Exception:
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

                            cg.root.after(10, self.proceed)

                if self.num < self.electrode_limit:
                    self.num += 1
                else:
                    self.num = 0

                if self.analysis_count < self.analysis_limit:
                    if not self.StopSearch:
                        cg.root.after(200, self.verify)

    def verify_multi(self, myfile):

        # changing the column index
        # ---Set the electrode index value---#
        check_ = False
        try:
            # ---Preallocate Potential and Current lists---#
            with open(myfile, "r", encoding="utf-8") as mydata:
                encoding = "utf-8"

        except Exception:

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
                except Exception:
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
    @staticmethod
    def show_plot(frame):
        frame.tkraise()

    @staticmethod
    def show_frame(cont):

        frame = cg.ShowFrames[cont]
        frame.tkraise()


# ------------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------------#
