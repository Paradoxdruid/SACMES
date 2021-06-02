#! /usr/bin/env python3

from config import cg
from text_export import _update_global_lists


###############################################################################
###############################################################################
# Classes and Functions for Real-Time Tracking and Text File Export ######
###############################################################################
###############################################################################


class WaitTime:
    def __init__(self):

        cg.NormalizationWaiting = False

    @staticmethod
    def NormalizationWaitTime():

        cg.NormalizationWaiting = True

    @staticmethod
    def NormalizationProceed():

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

                _ = cg.HighLowList["High"]
                _ = cg.HighLowList["Low"]

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
