"""
File: making-graphs.py
Author: Katelyn Rohrer
Description: This file graphs the MOCA and Biostamp data on the same graph

"""


import data_class as dc
import glob, csv, math
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import datetime

MANUAL_VERT_ADJ = 0
MANUAL_HORIZ_ADJ = 0.999
ARM_LEN_M = 0.65  # METERS (ESTIMATE FOR NOW)
AXIS = "vert"

def main():
    # This takes a folder that contains both files to be graphed in it.
    folder = "ChestAA.CH2M.Run1.Fast copy"

    # This is used to find the correct file name for muscle and the correct
    # columns for stamp
    muscle = "Brachio"
    stamp = "Hand"

    # Gathering file names
    biostamp_file, moca_file = get_file_names(folder, muscle)

    # Creating data objects from data_class file
    bio = dc.BiostampData(biostamp_file)
    moca = dc.MocaData(moca_file, stamp, ARM_LEN_M)

    moca.smooth()  # Helps sometimes, hurts sometimes

    # Reset times to start at 0 seconds - based on first moca frame
    first_epoch = moca.epoch[0]
    moca.set_adj_epoch(first_epoch)
    bio.set_adj_epoch(first_epoch)
    moca.set_adj_vert(bio.adj_vert[bio._peaks_vert[0]])

    # Manual adjustment for moca coordinates - trying to make this automatic
    moca.man_vert_adj(MANUAL_VERT_ADJ)
    moca.man_horiz_adj(MANUAL_HORIZ_ADJ)

    if AXIS == "vert":
        plt.plot(bio.adj_epoch, bio.adj_vert, c='r', label='bio vert')
        plt.plot(moca.adj_epoch, moca.adj_vert, c='b', label='moca vert')
    elif AXIS == "horiz":
        plt.plot(bio.adj_epoch, bio.adj_horiz, c='r', label='bio horiz')
        plt.plot(moca.adj_epoch, moca.adj_horiz, c='b', label='moca horiz')

    plt.xlim([30, 40]) # can use for 3 reps, , ylim=(ymin, ymax)

    file_info = bio.get_file_info()
    title = file_info["Movement"] + " " + file_info["Subject"] + " " + muscle\
                + "/" + stamp + " " + file_info["Run"][:-1] + " "\
                + file_info["Run"][-1:] + " " + file_info["Speed"] + " at 999 ms"

    plt.title(title)
    plt.legend(loc="upper left")
    plt.xlabel("time (s)")
    plt.ylabel("position (m)")
    plt.show()


def find_all_files(folder):
    # Finds all files in directory ending in accel.csv
    files = glob.glob(folder + "/*", recursive=True)
    return files


def get_file_names(folder, muscle):
    biostamp_file = ""
    moca_file = ""
    all_files = find_all_files(folder)
    for file in all_files:
        if muscle in file and "position" in file:
            biostamp_file = file
        if "accel" not in file and "gyro" not in file \
                and "position" not in file and "velocity" not in file:
            moca_file = file

    assert biostamp_file != "", "File Not Found"
    assert moca_file != "", "File Not Found"

    return biostamp_file, moca_file

if __name__ == "__main__":
    main()
