#!/usr/bin/env python3

import tkinter as tk
from config import cg
import tkinter.ttk as ttk
import matplotlib.pyplot as plt
from text_export import TextFileExport

# from input_frame import InputFrame -- circular import


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
        if cg.frequency_list[-1] > cg.cutoff_frequency:
            self.High = True
        else:
            self.High = False

        if cg.frequency_list[0] <= cg.cutoff_frequency:
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

        self.Title = tk.Label(self, text="Post Analysis", font=cg.HUGE_FONT).grid(
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
            NormalizationFrame, text="Set Normalization Point", font=cg.MEDIUM_FONT
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
            NormalizationFrame, text="", fg="red", font=cg.MEDIUM_FONT
        )
        cg.NormWarning = self.NormWarning

        if len(cg.frequency_list) > 1:

            self.FrequencyFrame = tk.Frame(DataAdjustmentFrame, relief="groove", bd=3)
            self.FrequencyFrame.grid(row=2, column=0, pady=10, padx=3, ipady=2)

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

            self.HighFrequencyEntry = tk.Entry(self.FrequencyFrame, width=7)
            self.HighFrequencyEntry.insert(tk.END, cg.HighFrequency)
            self.HighFrequencyEntry.grid(row=2, column=1, padx=5)

            # --- Low Frequency Selection for KDM and Ratiometric Analysis ---#
            self.LowFrequencyLabel = tk.Label(
                self.FrequencyFrame, text="Low Frequency", font=cg.MEDIUM_FONT
            )
            self.LowFrequencyLabel.grid(row=1, column=0, pady=5, padx=5)

            self.LowFrequencyEntry = tk.Entry(self.FrequencyFrame, width=7)
            self.LowFrequencyEntry.insert(tk.END, cg.LowFrequency)
            self.LowFrequencyEntry.grid(row=2, column=0, padx=5)

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

    @staticmethod
    def _draw():

        for num in range(cg.electrode_count):

            # get the figure for the electrode ##
            fig, ax = cg.figures[num]

            subplot_count = 0
            for count in range(len(cg.frequency_list)):

                _ = cg.frequency_list[count]

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
                _ = cg.plot_list[num][count]  # 'count' is the frequency index value

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
            self.win, text="No File Path Selected", font=cg.MEDIUM_FONT, fg="red"
        )
        self.PathWarningExists = False  # tracks the existence of a warning label

        # --- File Handle Input ---#
        HandleLabel = tk.Label(
            self.win, text="Exported File Handle:", font=cg.LARGE_FONT
        )
        HandleLabel.grid(row=4, column=0, columnspan=2)
        self.filehandle = ttk.Entry(self.win)
        self.filehandle.insert(tk.END, cg.FileHandle)
        self.filehandle.grid(row=5, column=0, columnspan=2, pady=5)

        self.ElectrodeLabel = tk.Label(
            self.win, text="Select Electrodes:", font=cg.LARGE_FONT
        )
        self.ElectrodeLabel.grid(row=10, column=0, sticky="nswe")
        self.ElectrodeCount = tk.Listbox(
            self.win,
            relief="groove",
            exportselection=0,
            width=10,
            font=cg.LARGE_FONT,
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
            self.win, text="Select Frequencies", font=cg.LARGE_FONT
        )
        self.FrequencyLabel.grid(row=10, column=1, padx=10)
        self.FrequencyList = tk.Listbox(
            self.win,
            relief="groove",
            exportselection=0,
            width=5,
            font=cg.LARGE_FONT,
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
            cg.FilePath = tk.filedialog.askdirectory(parent=parent)
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

        except Exception:
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
        self.show_frame(self.parent)  # InputFrame)
        self.close_frame(PostAnalysis)

        # Take resize weight away from the Visualization Canvas
        cg.container.columnconfigure(1, weight=0)

    # --- Function to switch between visualization frames ---#
    @staticmethod
    def show_plot(frame):
        frame.tkraise()

    @staticmethod
    def show_frame(cont):

        frame = cg.ShowFrames[cont]
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


# ------------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------------#
