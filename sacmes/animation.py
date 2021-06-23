#!/usr/bin/env python3

import tkinter as tk
from config import cg
import os
from scipy.signal import savgol_filter
import threading
from global_func import _retrieve_file, ReadData
import time
from lmfit.models import LorentzianModel, QuadraticModel


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
                cg.PoisonPill = self.PoisonPill  # global reference

                self.file = 1

                cg.root.after(10, self.start)  # initiate the run() method

            def run(self):

                while True:
                    try:
                        task = self.q.get(block=False)

                    except Exception:
                        break
                    else:
                        if not cg.PoisonPill:
                            cg.root.after(cg.Interval, task)

                if not cg.analysis_complete:
                    if not cg.PoisonPill:
                        cg.root.after(10, self.run)

        _ = _threaded_animation(Queue=cg.q)

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

    @staticmethod
    def _blit_clear(artists, bg_cache):
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
        _, ax = cg.figures[self.num]
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
                    ratio_fig, _ = cg.ratiometric_figures[self.num]
                    ratio_fig.canvas.draw()

        elif self._drawn_artists:

            self._blit_draw(self._drawn_artists, self._blit_cache)

    # The rest of the code in this class is to facilitate easy blitting
    @staticmethod
    def _blit_draw(artists, bg_cache):
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
            except Exception:
                try:
                    mydata_bytes = os.path.getsize(myfile2)
                    myfile = myfile2
                    filename = filename2
                except Exception:
                    try:
                        mydata_bytes = os.path.getsize(myfile3)
                        myfile = myfile3
                        filename = filename3
                    except Exception:
                        try:
                            mydata_bytes = os.path.getsize(myfile4)
                            myfile = myfile4
                            filename = filename4
                        except Exception:
                            try:
                                mydata_bytes = os.path.getsize(myfile5)
                                myfile = myfile5
                                filename = filename5
                            except Exception:
                                try:
                                    mydata_bytes = os.path.getsize(myfile6)
                                    myfile = myfile6
                                    filename = filename6
                                except Exception:
                                    mydata_bytes = 1

        if mydata_bytes > cg.byte_limit:
            print("%s%d: Queueing %s" % (self.spacer, self.electrode, filename))
            cg.q.put(lambda: self._run_analysis(myfile, frequency))

        else:
            if not cg.PoisonPill:
                cg.root.after(100, self._step)

    def _check_queue(self):

        while True:
            try:
                print("%sChecking Queue" % self.spacer)
                _ = cg.q.get(block=False)
            except Exception:
                print("%sQueue Empty" % self.spacer)
                break
            else:
                if not cg.PoisonPill:
                    cg.root.after(1, self.task)

        if not cg.analysis_complete:
            if not cg.PoisonPill:
                cg.root.after(5, self._check_queue)

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
                except Exception:
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
                cg.root.after(1, self._step)

        ##########################################################
        # Elif the function has not analyzed each frequency  ###
        # for this file, move onto the next frequency        ###
        ##########################################################
        elif self.count < self.frequency_limit:
            self.count += 1

            cg.root.after(1, self._step)

    @staticmethod
    def fit_lz_peaks(potentials, currents):
        min_y = float(min(currents))
        model = QuadraticModel(prefix="Background")
        params = model.make_params()  # a=0, b=0, c=0
        params.add("a", 0, min=0)
        params.add("b", 0)
        params.add("c", 0, min=min_y)

        peak = LorentzianModel(prefix="peak")
        pars = peak.make_params()
        pars.add("center", -0.3)
        pars.add("amplitude", 0.005, min=0)
        pars.add("sigma", 0.05, min=0)

        model = model + peak
        params.update(pars)

        # _ = model.eval(params, x=potentials)  # not needed
        result = model.fit(currents, params, x=potentials)
        comps = result.eval_components()

        return result.best_fit, float(max(comps["peak"]))

    def _raw_generator(self, myfile, frequency):

        ########################################
        # Polynomical Regression Range (V) ###
        ########################################
        # --- if the frequency is equal or below cutoff_frequency,
        # use the low freq parameters ---#
        if frequency <= cg.cutoff_frequency:
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
        if sg_range <= cg.sg_degree:
            sg_range = cg.sg_degree + 1

        # -- if the range is even, make it odd --#
        if sg_range % 2 == 0:
            sg_range = sg_range + 1

        # Apply the smoothing function and create a dictionary pairing
        # each potential with its corresponding current
        try:
            smooth_currents = savgol_filter(currents, sg_range, cg.sg_degree)
            data_dict = dict(zip(potentials, smooth_currents))
        except ValueError:
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
        # polynomial_coeffs = np.polyfit(
        #     adjusted_potentials, adjusted_currents, cg.polyfit_deg
        # )

        eval_regress, baseline = self.fit_lz_peaks(
            adjusted_potentials, adjusted_currents
        )

        # print(baseline)
        # TODO: use baseline for peak height calculation

        #############################
        # Polynomial Regression ###
        #############################
        # eval_regress = np.polyval(polynomial_coeffs, adjusted_potentials).tolist()
        # Implement better baseline subtraction here.
        # _ = dict(zip(eval_regress, adjusted_potentials))
        # dictionary with current: potential

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

            _ = (Peak_Height / frequency) * 100000
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
                _ = cg.frequency_list[self.count]

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
            _ = 1
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
                    _,
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

                _ = cg.data_list[self.num][self.count][
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
            _ = 1
            EmptyPlots = framedata
            time.sleep(0.1)
            print("\n Yielding Empty Plots in Animation \n")
            return EmptyPlots

    ############################
    # Ratiometric Analysis ###
    ############################
    def _ratiometric_generator(self):

        _ = self.file - 1

        HighFrequency = cg.HighLowList["High"]
        LowFrequency = cg.HighLowList["Low"]

        HighCount = cg.frequency_dict[HighFrequency]
        _ = cg.frequency_dict[LowFrequency]

        HighPoint = cg.normalized_data_list[self.num][HighCount][self.index]
        LowPoint = cg.offset_normalized_data_list[self.num][self.index]

        NormalizedRatio = HighPoint / LowPoint
        KDM = (HighPoint - LowPoint) + 1

        # -- save the data to global lists --#
        cg.normalized_ratiometric_data_list[self.num].append(NormalizedRatio)
        cg.KDM_list[self.num].append(KDM)

        return NormalizedRatio, KDM

    def _ratiometric_animation(self, framedata, *args):

        _, KDM = framedata

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
