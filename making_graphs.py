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
MANUAL_HORIZ_ADJ = 0
ARM_LEN_M = 0.69  # METERS (ESTIMATE FOR NOW)

def main():
    # This takes a folder that contains both files to be graphed in it.
    folder = "ChestAA.CH2M.Run1.Fast copy/"

    # This is used to find the correct file name for muscle and the correct
    # columns for stamp
    muscle = "Brachio"
    stamp = "Hand"

    # Gathering file names
    biostamp_file, moca_file = get_file_names(folder, muscle)

    # Creating data objects from data_class file
    bio = dc.BiostampData(biostamp_file, dist=100, hei=0.5)
    moca = dc.MocaData(moca_file, stamp, ARM_LEN_M, dist=200, hei=-0.7)

    moca.smooth()  # Helps sometimes, hurts sometimes

    # Manual adjustment for moca coordinates - trying to make this automatic
    moca.vert_adj(MANUAL_VERT_ADJ)
    moca.horiz_adj(MANUAL_HORIZ_ADJ)

    # Prints out the peaks coordinates - helps for debugging peaks
    #plt.plot(moca.sec, moca.vert, c='r')
    #for peak in peaks:
    #    plt.plot(moca.sec[peak], moca.vert[peak], c='b', marker="o")


    # DOES NOT ADJUST CORRECTLY - HELP
    #adj_moca = dc.adjMocaData(moca, bio)

    #plt.plot(bio.sec, bio.horiz, c='r', label='bio horiz')
    #plt.plot(moca.sec, moca.horiz, c='y', label='moca horiz')
    plt.plot(bio.epoch, bio.vert, c='r', label='bio horiz')
    plt.plot(moca.epoch, moca.vert, c='b', label='moca horiz')

    file_info = bio.get_file_info()
    title = file_info["Movement"] + " " + muscle + "/" + stamp \
                + " " + file_info["Run"][:-1] + " " + file_info["Run"][-1:] \
                + " " + file_info["Speed"]
    print(title)
    #plt.plot(adj_moca.sec_horiz, adj_moca.horiz, c='b', label='adj moca horiz')
    plt.title(title)
    plt.legend(loc="upper left")
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
