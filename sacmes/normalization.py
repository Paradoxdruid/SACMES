#!/usr/bin/env python3

from config import cg


##############################
# Normalization Function ###
##############################
class DataNormalization:
    def __init__(self):
        pass

    @staticmethod
    def Normalize(file, data, num, count, index):

        sample = len(cg.file_list) * cg.SampleRate / 3600
        #######################################################
        # Check the frequency and apply the baseline offset ##
        #######################################################
        frequency = cg.frequency_list[count]
        if frequency == cg.HighLowList["Low"]:
            if cg.XaxisOptions == "Experiment Time":
                Offset = (sample * cg.LowFrequencySlope) + cg.LowFrequencyOffset
            elif cg.XaxisOptions == "File Number":
                Offset = (file * cg.LowFrequencySlope) + cg.LowFrequencyOffset
        else:
            Offset = 0

        NormalizationIndex = int(cg.NormalizationPoint) - 1

        # --- If the file being used as the standard has been analyzed,
        # normalize the data to that point ---#
        if file >= cg.NormalizationPoint:

            if cg.NormalizationPoint not in cg.NormalizationVault:
                cg.NormalizationVault.append(cg.NormalizationPoint)

            # -- if the software has still been normalizing to the first file,
            # start normalizing to the normalization point --#
            if not cg.InitializedNormalization:
                cg.InitializedNormalization = True

            ###########################################################
            # If the rest of the data has already been normalized ###
            # to this point, continue to normalize the data for   ###
            # the current file to the normalization point         ###
            ###########################################################
            cg.normalized_data_list[num][count][index] = (
                data / cg.data_list[num][count][NormalizationIndex]
            )

            ###########################################################################
            # If this is a low frequency, apply the offset to the normalized data ###
            ###########################################################################
            if frequency == cg.HighLowList["Low"]:
                cg.offset_normalized_data_list[num][index] = (
                    cg.normalized_data_list[num][count][index] + Offset
                )

        #######################################################################
        # Elif the chosen normalization point is greater than the current ###
        # file, continue to normalize to the previous normalization point ###
        #######################################################################
        elif cg.InitializedNormalization:

            # Acquire the normalization point that was previously selected ###
            TempNormalizationPoint = cg.NormalizationVault[-1]
            TempNormalizationIndex = TempNormalizationPoint - 1

            cg.normalized_data_list[num][count][index] = (
                data / cg.data_list[num][count][TempNormalizationIndex]
            )

            ###########################################################################
            # If this is a low frequency, apply the offset to the normalized data ###
            ###########################################################################
            if cg.frequency_list[count] == cg.HighLowList["Low"]:
                cg.offset_normalized_data_list[num][index] = (
                    cg.normalized_data_list[num][count][index] + Offset
                )

        # --- Else, if the initial normalization point has not yet been reached,
        # normalize to the first file ---#
        elif not cg.InitializedNormalization:
            cg.normalized_data_list[num][count][index] = (
                data / cg.data_list[num][count][0]
            )

            ###########################################################################
            # If this is a low frequency, apply the offset to the normalized data ###
            ###########################################################################
            if cg.frequency_list[count] == cg.HighLowList["Low"]:
                cg.offset_normalized_data_list[num][index] = (
                    cg.normalized_data_list[num][count][index] + Offset
                )

    ################################################################
    # If the normalization point has been changed, renormalize ###
    # the data list to the new normalization point             ###
    ################################################################
    def RenormalizeData(self, file):
        ##############################################################
        # If the normalization point equals the current file,      ##
        # normalize all of the data to the new normalization point ##
        #############################################################
        if file == cg.NormalizationPoint:
            index = file - 1
            NormalizationIndex = cg.NormalizationPoint - 1
            for num in range(cg.electrode_count):
                for count in range(len(cg.frequency_list)):

                    cg.normalized_data_list[num][count][:index] = [
                        (idx / cg.data_list[num][count][NormalizationIndex])
                        for idx in cg.data_list[num][count][:index]
                    ]

                    ##################################################
                    # If the frequency is below cutoff_frequency, ###
                    # add the baseline Offset                     ###
                    ##################################################
                    if cg.frequency_list[count] == cg.HighLowList["Low"]:
                        for index in range(len(cg.file_list)):

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

            ################################################
            # Analyze KDM using new normalization data ###
            ################################################
            if len(cg.frequency_list) > 1:
                self.ResetRatiometricData()

            ###############################
            # GUI Normalization Label ###
            ###############################
            cg.NormWarning["fg"] = "green"
            cg.NormWarning["text"] = "Normalized to file %s" % str(
                cg.NormalizationPoint
            )

            ########################################################################
            # If .txt file export has been activated, update the exported data ###
            ########################################################################
            if cg.SaveVar:
                cg.text_file_export.TxtFileNormalization()

        #########################################################################
        # If the Normalization Point has been changed and the current file is ##
        # greater than the new point, renormalize the data to the new point   ##
        #########################################################################
        if cg.NormalizationWaiting:
            index = file - 1
            NormalizationIndex = cg.NormalizationPoint - 1
            for num in range(cg.electrode_count):
                for count in range(len(cg.frequency_list)):

                    ##########################
                    # Renormalize the data ##
                    ##########################
                    cg.normalized_data_list[num][count][:index] = [
                        idx / cg.data_list[num][count][NormalizationIndex]
                        for idx in cg.data_list[num][count][:index]
                    ]
                    ##################################################
                    # If the frequency is below cutoff_frequency,  ##
                    # add the baseline Offset                      ##
                    ##################################################
                    if cg.frequency_list[count] == cg.HighLowList["Low"]:
                        for index in range(len(cg.file_list)):

                            ##########################
                            # Calculate the offset ##
                            ##########################
                            sample = cg.sample_list[index]
                            file = index + 1

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

            ################################################
            # Using the newly normalized data, calculate ##
            # the Normalized Ratio and KDM               ##
            # for each file that has been analyzed       ##
            ################################################
            if len(cg.frequency_list) > 1:
                self.ResetRatiometricData()

            # --- Indicate that the data has been normalized to the
            # new NormalizationPoint ---#
            cg.NormWarning["fg"] = "green"
            cg.NormWarning["text"] = "Normalized to file %s" % str(
                cg.NormalizationPoint
            )
            cg.wait_time.NormalizationProceed()

            # -- if .txt file export has been activated, update the exported data ---#
            if cg.SaveVar:
                cg.text_file_export.TxtFileNormalization()

    #############################################################
    # Readjust the data to the new user-inputted parameters ###
    #############################################################
    @staticmethod
    def ResetRatiometricData():

        ############################################
        # Readjust Low Frequencies with Offset ###
        ############################################

        # -- Iterate through every frequency --#
        for frequency in cg.frequency_list:

            # -- Only apply the offset if the frequency is below cutoff_frequency --#
            if frequency == cg.HighLowList["Low"]:
                count = cg.frequency_dict[frequency]

                # -- Apply the offset to every file --#
                for index in range(len(cg.file_list)):

                    sample = cg.sample_list[index]
                    file = cg.file_list[index]

                    if cg.XaxisOptions == "Experiment Time":
                        Offset = (sample * cg.LowFrequencySlope) + cg.LowFrequencyOffset
                    elif cg.XaxisOptions == "File Number":
                        Offset = (file * cg.LowFrequencySlope) + cg.LowFrequencyOffset

                    for num in range(cg.electrode_count):
                        cg.offset_normalized_data_list[num][
                            index
                        ] = cg.normalized_data_list[num][count][index] + float(Offset)

        ####################################################
        # Readjust KDM with newly adjusted frequencies ###
        ####################################################
        for file in cg.file_list:
            index = file - 1
            for num in range(cg.electrode_count):

                # grab the index value for the current high and low frequencies
                # used for ratiometric analysis #
                HighCount = cg.frequency_dict[cg.HighFrequency]

                HighPoint = cg.normalized_data_list[num][HighCount][index]
                LowPoint = cg.offset_normalized_data_list[num][index]

                NormalizedDataRatio = HighPoint / LowPoint
                cg.normalized_ratiometric_data_list[num][index] = NormalizedDataRatio

                # -- KDM ---#
                KDM = (HighPoint - LowPoint) + 1
                cg.KDM_list[num][index] = KDM

        # -- if .txt file export has been activated, update the exported data ---#
        if cg.SaveVar:
            if not cg.analysis_complete:
                cg.text_file_export.TxtFileNormalization()
