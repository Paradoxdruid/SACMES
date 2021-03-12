#!/usr/bin/env python3
import tkinter as tk
from config import cg
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import os
import numpy as np
from scipy.signal import savgol_filter
from scan_frames import FrequencyMapVisualizationFrame, ContinuousScanVisualizationFrame
from text_export import TextFileExport

# from main_window import ReadData, _get_listval, _retrieve_file

# cg = Config()


###############
# Styling ###
###############
HUGE_FONT = ("Verdana", 18)
LARGE_FONT = ("Verdana", 11)
MEDIUM_FONT = ("Verdnana", 10)
SMALL_FONT = ("Verdana", 8)


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
            cg.root.after(
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

            if int(frequency) > cg.cutoff_frequency:

                if not cg.HighAlreadyReset:
                    cg.high_xstart = max(potentials)
                    cg.high_xend = min(potentials)

                # -- set the local variables to the global ---#
                xend = cg.high_xend
                xstart = cg.high_xstart

            elif int(frequency) <= cg.cutoff_frequency:

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
            smooth_currents = savgol_filter(currents, 15, cg.sg_degree)
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
                adjusted_potentials, adjusted_currents, cg.polyfit_deg
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
            cg.root.after(1000, self.InitializeSubplots, ax, electrode)

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
            smooth_currents = savgol_filter(currents, 15, cg.sg_degree)
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
                adjusted_potentials, adjusted_currents, cg.polyfit_deg
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
