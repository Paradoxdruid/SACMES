#!/usr/bin/env python3

import tkinter as tk
import tkinter.ttk as ttk
from config import cg
from animation import ElectrochemicalAnimation
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# from input_frame import InputFrame  - circular import


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
        FileTitle = tk.Label(self, text="File Number", font=cg.MEDIUM_FONT,)
        FileTitle.grid(row=0, column=0, padx=5, pady=5)
        cg.FileLabel = ttk.Label(
            self, text="1", font=cg.LARGE_FONT, style="Fun.TButton"
        )
        cg.FileLabel.grid(row=1, column=0, padx=5, pady=5)

        # --- Display the experiment duration as a function of the user-inputted
        # Sample Rate ---#
        SampleTitle = tk.Label(self, text="Experiment Time (h)", font=cg.MEDIUM_FONT)
        SampleTitle.grid(row=0, column=1, padx=5, pady=5)
        cg.RealTimeSampleLabel = ttk.Label(self, text="0", style="Fun.TButton")
        cg.RealTimeSampleLabel.grid(row=1, column=1, padx=5, pady=5)

        # --- Real-time Normalization Variable ---#
        SetPointNormLabel = tk.Label(
            self, text="Set Normalization Point", font=cg.MEDIUM_FONT
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
        self.NormWarning = tk.Label(self, text="", fg="red", font=cg.MEDIUM_FONT)
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
        SetInjectionLabel = tk.Label(
            self, text="Set Injection Range", font=cg.MEDIUM_FONT
        )
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
                self.FrequencyFrame, text="Drift Correction", font=cg.LARGE_FONT
            )
            self.KDM_title.grid(row=0, column=0, columnspan=3, pady=1, padx=5)

            # --- High Frequency Selection for KDM and Ratiometric Analysis ---#
            self.HighFrequencyLabel = tk.Label(
                self.FrequencyFrame, text="High Frequency", font=cg.MEDIUM_FONT
            )
            self.HighFrequencyLabel.grid(row=1, column=1, pady=5, padx=5)

            cg.HighFrequencyEntry = tk.Entry(self.FrequencyFrame, width=7)
            cg.HighFrequencyEntry.insert(tk.END, cg.HighFrequency)
            cg.HighFrequencyEntry.grid(row=2, column=1, padx=5)

            # --- Low Frequency Selection for KDM and Ratiometric Analysis ---#
            self.LowFrequencyLabel = tk.Label(
                self.FrequencyFrame, text="Low Frequency", font=cg.MEDIUM_FONT
            )
            self.LowFrequencyLabel.grid(row=1, column=0, pady=5, padx=5)

            cg.LowFrequencyEntry = tk.Entry(self.FrequencyFrame, width=7)
            cg.LowFrequencyEntry.insert(tk.END, cg.LowFrequency)
            cg.LowFrequencyEntry.grid(row=2, column=0, padx=5)

            self.LowFrequencyOffsetLabel = tk.Label(
                self.FrequencyFrame, text="Low Frequency\n Offset", font=cg.MEDIUM_FONT
            ).grid(row=3, column=0, pady=2, padx=2)
            self.LowFrequencyOffset = tk.Entry(self.FrequencyFrame, width=7)
            self.LowFrequencyOffset.insert(tk.END, cg.LowFrequencyOffset)
            self.LowFrequencyOffset.grid(row=4, column=0, padx=2, pady=2)

            self.LowFrequencySlopeLabel = tk.Label(
                self.FrequencyFrame,
                text="Low Frequency\n Slope Manipulation",
                font=cg.MEDIUM_FONT,
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
            RegressionFrame, text="Real Time Analysis Manipulation", font=cg.LARGE_FONT
        )
        self.RegressionLabel.grid(row=0, column=0, columnspan=4, pady=5, padx=5)

        ###################################################################
        # Real Time Manipulation of Savitzky-Golay Smoothing Function ###
        ###################################################################
        self.SmoothingLabel = tk.Label(
            RegressionFrame, text="Savitzky-Golay Window (mV)", font=cg.LARGE_FONT
        )
        self.SmoothingLabel.grid(row=1, column=0, columnspan=4, pady=1)
        self.SmoothingEntry = tk.Entry(RegressionFrame, width=10)
        self.SmoothingEntry.grid(row=2, column=0, columnspan=4, pady=3)
        self.SmoothingEntry.insert(tk.END, cg.sg_window)

        # --- Check for the presence of high and low frequencies ---#
        if cg.frequency_list[-1] > cg.cutoff_frequency:
            self.High = True
        else:
            self.High = False

        if cg.frequency_list[0] <= cg.cutoff_frequency:
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
                LowParameterFrame, text="xstart (V)", font=cg.MEDIUM_FONT
            ).grid(row=0, column=0)
            self.low_xstart_entry = tk.Entry(LowParameterFrame, width=7)
            self.low_xstart_entry.insert(tk.END, str(cg.low_xstart))
            self.low_xstart_entry.grid(row=1, column=0)
            cg.low_xstart_entry = self.low_xstart_entry

            # --- points discarded at the beginning of the voltammogram, xend ---#
            self.low_xend_label = tk.Label(
                LowParameterFrame, text="xend (V)", font=cg.MEDIUM_FONT
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
                HighParameterFrame, text="xstart (V)", font=cg.MEDIUM_FONT
            ).grid(row=0, column=0)
            self.high_xstart_entry = tk.Entry(HighParameterFrame, width=7)
            self.high_xstart_entry.insert(tk.END, str(cg.high_xstart))
            self.high_xstart_entry.grid(row=1, column=0)
            cg.high_xstart_entry = self.high_xstart_entry

            # --- points discarded at the beginning of the voltammogram, xend ---#
            self.high_xend_label = tk.Label(
                HighParameterFrame, text="xend (V)", font=cg.MEDIUM_FONT
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
                    text="f <= %dHz" % cg.cutoff_frequency,
                    command=lambda: self.show_frame("LowParameterFrame"),
                )
                self.SelectLowParameters.grid(row=4, column=0, pady=5, padx=5)

                self.SelectHighParameters = ttk.Button(
                    RegressionFrame,
                    style="On.TButton",
                    text="f > %dHz" % cg.cutoff_frequency,
                    command=lambda: self.show_frame("HighParameterFrame"),
                )
                self.SelectHighParameters.grid(row=4, column=1, pady=5, padx=5)

        # --- Button to apply adjustments ---#
        self.AdjustParameterButton = tk.Button(
            RegressionFrame,
            text="Apply Adjustments",
            font=cg.LARGE_FONT,
            command=self.AdjustParameters,  # lambda
        )
        self.AdjustParameterButton.grid(row=5, column=0, columnspan=4, pady=10, padx=10)

        # ---Buttons to switch between electrode frames---#
        frame_value = 0
        column_value = 0
        for _ in cg.PlotValues:
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
        _ = file - 1

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
        self.show_frame(cg.input_frame)  # InputFrame)
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
    @staticmethod
    def show_plot(frame):
        frame.tkraise()

    #####################################
    # Destory the frames on Reset() ###
    #####################################
    @staticmethod
    def close_frame(cont):
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
            RegressionFrame, text="Real Time Analysis Manipulation", font=cg.LARGE_FONT
        )
        self.RegressionLabel.grid(row=0, column=0, columnspan=4, pady=5, padx=5)

        ###################################################################
        # Real Time Manipulation of Savitzky-Golay Smoothing Function ###
        ###################################################################
        self.SmoothingLabel = tk.Label(
            RegressionFrame, text="Savitzky-Golay Window (mV)", font=cg.LARGE_FONT
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
                LowParameterFrame, text="xstart (V)", font=cg.MEDIUM_FONT
            ).grid(row=0, column=0)
            self.low_xstart_entry = tk.Entry(LowParameterFrame, width=7)
            self.low_xstart_entry.insert(tk.END, str(cg.low_xstart))
            self.low_xstart_entry.grid(row=1, column=0)
            cg.low_xstart_entry = self.low_xstart_entry

            # --- points discarded at the beginning of the voltammogram, xend ---#
            self.low_xend_label = tk.Label(
                LowParameterFrame, text="xend (V)", font=cg.MEDIUM_FONT
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
                HighParameterFrame, text="xstart (V)", font=cg.MEDIUM_FONT
            ).grid(row=0, column=0)
            self.high_xstart_entry = tk.Entry(HighParameterFrame, width=7)
            self.high_xstart_entry.insert(tk.END, str(cg.high_xstart))
            self.high_xstart_entry.grid(row=1, column=0)
            cg.high_xstart_entry = self.high_xstart_entry

            # --- points discarded at the beginning of the voltammogram, xend ---#
            self.high_xend_label = tk.Label(
                HighParameterFrame, text="xend (V)", font=cg.MEDIUM_FONT
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
            font=cg.LARGE_FONT,
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
        self.show_frame(cg.input_frame)  # InputFrame)
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

        ElectrodeLabel = tk.Label(self, text="%s" % electrode, font=cg.HUGE_FONT)
        ElectrodeLabel.grid(row=0, column=0, pady=5, sticky="n")

        cg.FrameFileLabel = tk.Label(self, text="", font=cg.MEDIUM_FONT)
        cg.FrameFileLabel.grid(row=0, column=1, pady=3, sticky="ne")

        # --- Voltammogram, Raw Peak Height, and Normalized Figure and Artists ---#
        fig, _ = cg.figures[count]  # Call the figure and artists for the electrode
        canvas = FigureCanvasTkAgg(fig, self)  # and place the artists within the frame
        canvas.draw()  # initial draw call to create the artists that will be blitted
        canvas.get_tk_widget().grid(
            row=1, columnspan=2, pady=6, ipady=5, sticky="news"
        )  # does not affect size of figure within plot container

        if len(cg.frequency_list) > 1:
            # --- Ratiometric Figure and Artists ---#
            fig, _ = cg.ratiometric_figures[
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

        ElectrodeLabel = tk.Label(self, text="%s" % electrode, font=cg.HUGE_FONT)
        ElectrodeLabel.grid(row=0, column=0, pady=5, sticky="n")

        cg.FrameFileLabel = tk.Label(self, text="", font=cg.MEDIUM_FONT)
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
