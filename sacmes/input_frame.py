#!/usr/bin/env python3
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog

from config import cg
from queue import Queue
import datetime
from checkpoint import CheckPoint


# cg = Config()


###############
# Styling ###
###############
# HUGE_FONT = ("Verdana", 18)
# cg.LARGE_FONT = ("Verdana", 11)
# cg.MEDIUM_FONT = ("Verdnana", 10)
# SMALL_FONT = ("Verdana", 8)


class InputFrame(
    tk.Frame
):  # first frame that is displayed when the program is initialized
    def __init__(self, parent, controller):

        # global cg

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
            self, text="No File Path Selected", font=cg.MEDIUM_FONT, fg="red"
        )
        self.PathWarningExists = False  # tracks the existence of a warning label

        ImportFileLabel = tk.Label(
            self, text="Import File Label", font=cg.LARGE_FONT
        ).grid(row=row_value, column=0, columnspan=2)
        self.ImportFileEntry = tk.Entry(self)
        self.ImportFileEntry.grid(row=row_value + 1, column=0, columnspan=2, pady=5)
        self.ImportFileEntry.insert(tk.END, cg.handle_variable)

        # --- File Handle Input ---#
        HandleLabel = tk.Label(self, text="Exported File Handle:", font=cg.LARGE_FONT)
        HandleLabel.grid(row=row_value, column=2, columnspan=2)
        self.filehandle = ttk.Entry(self)
        now = datetime.datetime.now()
        day = str(now.day)
        month = str(now.month)
        year = str(now.year)
        self.filehandle.insert(tk.END, "DataExport_%s_%s_%s.txt" % (year, month, day))
        self.filehandle.grid(row=row_value + 1, column=2, columnspan=2, pady=5)

        row_value += 2

        EmptyLabel = tk.Label(self, text="", font=cg.LARGE_FONT).grid(
            row=row_value, rowspan=2, column=0, columnspan=10
        )
        row_value += 1

        # ---File Limit Input---#
        numFileLabel = tk.Label(self, text="Number of Files:", font=cg.LARGE_FONT)
        numFileLabel.grid(row=row_value, column=0, columnspan=2, pady=4)
        self.numfiles = ttk.Entry(self, width=7)
        self.numfiles.insert(tk.END, "50")
        self.numfiles.grid(row=row_value + 1, column=0, columnspan=2, pady=6)

        # --- Analysis interval for event callback in ElectrochemicalAnimation ---#
        IntervalLabel = tk.Label(
            self, text="Analysis Interval (ms):", font=cg.LARGE_FONT
        )
        IntervalLabel.grid(row=row_value, column=2, columnspan=2, pady=4)
        self.Interval = ttk.Entry(self, width=7)
        self.Interval.insert(tk.END, "10")
        self.Interval.grid(row=row_value + 1, column=2, columnspan=2, pady=6)

        row_value += 2

        # ---Sample Rate Variable---#
        SampleLabel = tk.Label(self, text="Sampling Rate (s):", font=cg.LARGE_FONT)
        SampleLabel.grid(row=row_value, column=0, columnspan=2)
        self.sample_rate = ttk.Entry(self, width=7)
        self.sample_rate.insert(tk.END, "20")
        self.sample_rate.grid(row=row_value + 1, column=0, columnspan=2)

        self.resize_label = tk.Label(self, text="Resize Interval", font=cg.LARGE_FONT)
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
            self.ElectrodeListboxFrame, text="Select Electrodes:", font=cg.LARGE_FONT
        )
        self.ElectrodeLabel.grid(row=0, column=0, columnspan=2, sticky="nswe")
        self.ElectrodeCount = tk.Listbox(
            self.ElectrodeListboxFrame,
            relief="groove",
            exportselection=0,
            width=10,
            font=cg.LARGE_FONT,
            height=6,
            selectmode="multiple",
            bd=3,
        )
        self.ElectrodeCount.bind("<<ListboxSelect>>", self.ElectrodeCurSelect)
        self.ElectrodeCount.grid(row=1, column=0, columnspan=2, sticky="nswe")
        for electrode in cg.electrodes:
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
            self.ListboxFrame, text="Select Frequencies", font=cg.LARGE_FONT
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
            font=cg.LARGE_FONT,
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
            font=cg.MEDIUM_FONT,
            command=lambda: cg.ManipulateFrequenciesFrame.tkraise(),  # noqa
        ).grid(row=2, column=0, columnspan=4)

        ###########################################################
        # Frame for adding/deleting frequencies from the list ###
        ###########################################################

        cg.ManipulateFrequenciesFrame = tk.Frame(self, width=10, bd=3, relief="groove")
        cg.ManipulateFrequenciesFrame.grid(
            row=row_value, column=2, columnspan=2, padx=10, pady=10, sticky="nsew"
        )

        ManipulateFrequencyLabel = tk.Label(
            cg.ManipulateFrequenciesFrame,
            text="Enter Frequency(s)",
            font=cg.MEDIUM_FONT,
        )
        ManipulateFrequencyLabel.grid(row=0, column=0, columnspan=4)

        self.FrequencyEntry = tk.Entry(cg.ManipulateFrequenciesFrame, width=8)
        self.FrequencyEntry.grid(row=1, column=0, columnspan=4)

        AddFrequencyButton = tk.Button(
            cg.ManipulateFrequenciesFrame,
            text="Add",
            font=cg.MEDIUM_FONT,
            command=self.AddFrequency,  # was lambda
        ).grid(row=2, column=0)
        DeleteFrequencyButton = tk.Button(
            cg.ManipulateFrequenciesFrame,
            text="Delete",
            font=cg.MEDIUM_FONT,
            command=self.DeleteFrequency,  # was lambda
        ).grid(row=2, column=1)
        ClearFrequencyButton = tk.Button(
            cg.ManipulateFrequenciesFrame,
            text="Clear",
            font=cg.MEDIUM_FONT,
            command=self.Clear,  # was lambda
        ).grid(row=3, column=0, columnspan=2)

        ReturnButton = tk.Button(
            cg.ManipulateFrequenciesFrame,
            text="Return",
            font=cg.MEDIUM_FONT,
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
        MethodsLabel = tk.Label(self, text="Select Analysis Method", font=cg.LARGE_FONT)
        self.MethodsBox = tk.Listbox(
            self,
            relief="groove",
            exportselection=0,
            font=cg.LARGE_FONT,
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
        OptionsLabel = tk.Label(
            self, text="Select Data to be Plotted", font=cg.LARGE_FONT
        )
        self.PlotOptions = tk.Listbox(
            self,
            relief="groove",
            exportselection=0,
            font=cg.LARGE_FONT,
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
            self, text="Select a Data Analysis Method", font=cg.MEDIUM_FONT, fg="red"
        )  # will only be added to the grid (row 16) if they dont select an option
        self.NoSelection = False

        # --- Select units of the X-axis ---#
        PlotOptions = ["Experiment Time", "File Number"]
        PlotLabel = tk.Label(self, text="Select X-axis units", font=cg.LARGE_FONT)
        self.XaxisOptions = tk.Listbox(
            self,
            relief="groove",
            exportselection=0,
            font=cg.LARGE_FONT,
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
            AdjustmentFrame, text="Select Y Limit Parameters", font=cg.LARGE_FONT
        )
        self.y_limit_parameter_label.grid(row=0, column=0, columnspan=4, pady=5, padx=5)

        # --- Raw Data Minimum Parameter Adjustment ---#
        self.raw_data_min_parameter_label = tk.Label(
            AdjustmentFrame, text="Raw Min. Factor", font=cg.MEDIUM_FONT
        )
        self.raw_data_min_parameter_label.grid(row=1, column=0)
        self.raw_data_min = tk.Entry(AdjustmentFrame, width=5)
        self.raw_data_min.insert(
            tk.END, "2"
        )  # initial minimum is set to 0.5*minimum current (baseline) of file 1
        self.raw_data_min.grid(row=2, column=0, padx=5, pady=2, ipadx=2)

        # --- Raw Data Maximum Parameter Adjustment ---#
        self.raw_data_max_parameter_label = tk.Label(
            AdjustmentFrame, text="Raw Max. Factor", font=cg.MEDIUM_FONT
        )
        self.raw_data_max_parameter_label.grid(row=3, column=0)
        self.raw_data_max = tk.Entry(AdjustmentFrame, width=5)
        self.raw_data_max.insert(
            tk.END, "2"
        )  # initial adjustment is set to 2x the max current (Peak Height) of file 1
        self.raw_data_max.grid(row=4, column=0, padx=5, pady=2, ipadx=2)

        # --- Raw Data Minimum Parameter Adjustment ---#
        self.data_min_parameter_label = tk.Label(
            AdjustmentFrame, text="Data Min. Factor", font=cg.MEDIUM_FONT
        )
        self.data_min_parameter_label.grid(row=1, column=1)
        self.data_min = tk.Entry(AdjustmentFrame, width=5)
        self.data_min.insert(
            tk.END, "2"
        )  # initial minimum is set to 0.5*minimum current (baseline) of file 1
        self.data_min.grid(row=2, column=1, padx=5, pady=2, ipadx=2)

        # --- Raw Data Maximum Parameter Adjustment ---#
        self.data_max_parameter_label = tk.Label(
            AdjustmentFrame, text="Data Max. Factor", font=cg.MEDIUM_FONT
        )
        self.data_max_parameter_label.grid(row=3, column=1)
        self.data_max = tk.Entry(AdjustmentFrame, width=5)
        self.data_max.insert(
            tk.END, "2"
        )  # initial adjustment is set to 2x the max current (Peak Height) of file 1
        self.data_max.grid(row=4, column=1, padx=5, pady=2, ipadx=2)

        # --- Normalized Data Minimum Parameter Adjustment ---#
        self.norm_data_min_parameter_label = tk.Label(
            AdjustmentFrame, text="Norm. Min.", font=cg.MEDIUM_FONT
        )
        self.norm_data_min_parameter_label.grid(row=1, column=2)
        self.norm_data_min = tk.Entry(AdjustmentFrame, width=5)
        self.norm_data_min.insert(tk.END, "0")  # initial minimum is set to 0
        self.norm_data_min.grid(row=2, column=2, padx=5, pady=2, ipadx=2)

        # --- Normalized Data Maximum Parameter Adjustment ---#
        self.norm_data_max_parameter_label = tk.Label(
            AdjustmentFrame, text="Norm. Max.", font=cg.MEDIUM_FONT
        )
        self.norm_data_max_parameter_label.grid(row=3, column=2)
        self.norm_data_max = tk.Entry(AdjustmentFrame, width=5)
        self.norm_data_max.insert(tk.END, "2")  # initial maximum is set to 2
        self.norm_data_max.grid(row=4, column=2, padx=5, pady=2, ipadx=2)

        # --- Raw Data Minimum Parameter Adjustment ---#
        self.KDM_min_label = tk.Label(
            AdjustmentFrame, text="KDM Min.", font=cg.MEDIUM_FONT
        )
        self.KDM_min_label.grid(row=1, column=3)
        self.KDM_min = tk.Entry(AdjustmentFrame, width=5)
        self.KDM_min.insert(
            tk.END, "0"
        )  # initial minimum is set to 0.5*minimum current (baseline) of file 1
        self.KDM_min.grid(row=2, column=3, padx=5, pady=2, ipadx=2)

        # --- Raw Data Maximum Parameter Adjustment ---#
        self.KDM_Max_label = tk.Label(
            AdjustmentFrame, text="KDM Max. ", font=cg.MEDIUM_FONT
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
            cg.FilePath = tkinter.filedialog.askdirectory()  # (parent=parent)
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

        except Exception:
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
        except Exception:
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

        except Exception:
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
