#!/usr/bin/env python3

import csv
from config import cg
from numpy import sqrt
import time


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

            with open(
                self.TextFileHandle, "w+", encoding="utf-8", newline=""
            ) as our_input:
                writer = csv.writer(our_input, delimiter=" ")
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

        except Exception:
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

        except Exception:
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
