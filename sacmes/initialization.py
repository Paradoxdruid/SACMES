#! /usr/bin/env python3
import tkinter as tk
from config import Config
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import os
import numpy as np
from scipy.signal import savgol_filter


cg = Config()


###############
# Styling ###
###############
HUGE_FONT = ("Verdana", 18)
LARGE_FONT = ("Verdana", 11)
MEDIUM_FONT = ("Verdnana", 10)
SMALL_FONT = ("Verdana", 8)


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
