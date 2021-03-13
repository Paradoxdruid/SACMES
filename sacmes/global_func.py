#!/usr/bin/env python3

from config import cg

########################
# Global Functions ###
########################


##############################
# Retrieve the file name ###
##############################
def _retrieve_file(file, electrode, frequency):
    try:
        if cg.method == "Continuous Scan":

            if cg.e_var == "single":
                filename = "%s%dHz_%d%s" % (
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename2 = "%s%dHz__%d%s" % (
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename3 = "%s%dHz_#%d%s" % (
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename4 = "%s%dHz__#%d%s" % (
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )

            elif cg.e_var == "multiple":
                filename = "E%s_%s%sHz_%d%s" % (
                    electrode,
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename2 = "E%s_%s%sHz__%d%s" % (
                    electrode,
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename3 = "E%s_%s%sHz_#%d%s" % (
                    electrode,
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename4 = "E%s_%s%sHz__#%d%s" % (
                    electrode,
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )

            return filename, filename2, filename3, filename4

        if cg.method == "Frequency Map":

            if cg.e_var == "single":
                filename = "%s%dHz%s" % (cg.handle_variable, frequency, cg.extension)
                filename2 = "%s%dHz_%s" % (cg.handle_variable, frequency, cg.extension)
                filename3 = "%s%dHz_%d%s" % (
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename4 = "%s%dHz__%d%s" % (
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename5 = "%s%dHz_#%d%s" % (
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename6 = "%s%dHz__#%d%s" % (
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )

            elif cg.e_var == "multiple":
                filename = "E%s_%s%sHz%s" % (
                    electrode,
                    cg.handle_variable,
                    frequency,
                    cg.extension,
                )
                filename2 = "E%s_%s%sHz_%s" % (
                    electrode,
                    cg.handle_variable,
                    frequency,
                    cg.extension,
                )
                filename3 = "E%s_%s%sHz_%d%s" % (
                    electrode,
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename4 = "E%s_%s%sHz__%d%s" % (
                    electrode,
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename5 = "E%s_%s%sHz_#%d%s" % (
                    electrode,
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )
                filename6 = "E%s_%s%sHz__#%d%s" % (
                    electrode,
                    cg.handle_variable,
                    frequency,
                    file,
                    cg.extension,
                )

            return filename, filename2, filename3, filename4, filename5, filename6
    except Exception:
        print("\nError in retrieve_file\n")


def ReadData(myfile, electrode):

    try:
        ###############################################################
        # Get the index value of the data depending on if the     ###
        # electrodes are in the same .txt file or separate files  ###
        ###############################################################
        if cg.e_var == "single":
            cg.list_val = cg.current_column_index + (electrode - 1) * cg.spacing_index
        elif cg.e_var == "multiple":
            cg.list_val = cg.current_column_index

        #####################
        # Read the data ###
        #####################
        try:
            # ---Preallocate Potential and Current lists---#
            with open(myfile, "r", encoding="utf-16") as mydata:
                cg.encoding = "utf-16"

                variables = len(mydata.readlines())
                potentials = ["hold"] * variables
                # key: potential; value: current ##
                data_dict = {}

                currents = [0] * variables

        except Exception:
            # ---Preallocate Potential and Current lists---#
            with open(myfile, "r", encoding="utf-8") as mydata:
                cg.encoding = "utf-8"

                variables = len(mydata.readlines())
                potentials = ["hold"] * variables
                # key: potential; value: current ##
                data_dict = {}

                currents = [0] * variables

        # ---Extract data and dump into lists---#
        with open(myfile, "r", encoding=cg.encoding) as mydata:
            list_num = 0
            for line in mydata:
                check_split_list = line.split(cg.delimiter)
                # delete any spaces that may come before the first value #
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
                    # ---Currents---#
                    current_value = check_split_list[
                        cg.list_val
                    ]  # list_val is the index value of the given electrode
                    current_value = current_value.replace(",", "")
                    current_value = float(current_value)
                    current_value = current_value * 1000000
                    currents[list_num] = current_value

                    # ---Potentials---#
                    potential_value = line.split(cg.delimiter)[cg.voltage_column_index]
                    potential_value = potential_value.strip(",")
                    potential_value = float(potential_value)
                    potentials[list_num] = potential_value
                    data_dict.setdefault(potential_value, []).append(current_value)
                    list_num = list_num + 1

        # if there are 0's in the list (if the preallocation added to many)
        # then remove them
        cut_value = 0
        for value in potentials:
            if value == "hold":
                cut_value += 1

        if cut_value > 0:
            potentials = potentials[:-cut_value]
            currents = currents[:-cut_value]

        #######################
        # Return the data ###
        #######################
        return potentials, currents, data_dict
    except Exception:
        print("\nError in ReadData()\n")


#######################################
# Retrieve the column index value ###
#######################################
def _get_listval(electrode):
    try:
        if cg.e_var == "single":
            cg.list_val = cg.current_column_index + (electrode - 1) * cg.spacing_index

        elif cg.e_var == "multiple":
            cg.list_val = cg.current_column_index

            return cg.list_val
    except Exception:
        print("\nError in _get_listval\n")
