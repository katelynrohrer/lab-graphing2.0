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
ARM_LEN_M = 0.8509  # METERS
WRIST_TO_HAND_LEN = 0.06  # About 2.5in
FOLDER = "ChestAA.CH2M.Run1.Fast copy"  # contains all the necessary files
MUSCLE = "Bicep"
STAMP = "Shoulder"

#AXIS = "horiz"

def main():
    # Gathering file names
    biostamp_file, moca_file = get_file_names()

    # Creating data objects from data_class file
    bio = dc.BiostampData(biostamp_file)
    moca = dc.MocaData(moca_file, STAMP, ARM_LEN_M)

    moca.smooth()  # Helps sometimes, hurts sometimes

    # Reset times to start at 0 seconds - based on first moca frame
    first_epoch = moca.epoch[0]
    moca.set_adj_epoch(first_epoch)
    bio.set_adj_epoch(first_epoch)
    #moca.set_adj_vert(bio.adj_vert[bio._peaks_vert[0]], WRIST_TO_HAND_LEN)

    # Manual adjustment for moca coordinates - trying to make this automatic
    moca.man_vert_adj(MANUAL_VERT_ADJ)
    moca.man_horiz_adj(MANUAL_HORIZ_ADJ)

    plot(bio, moca)


def plot(bio, moca):
    fig = plt.figure(figsize=(17, 10))
    fig.subplots_adjust(hspace=0.3)

    fig1 = plt.subplot(221)
    fig1.plot(moca.adj_epoch, moca.adj_vert, c='b', label='moca vert')
    fig1.plot(bio.adj_epoch, bio.adj_vert, c='r', label='bio vert')
    fig1.set_title('Vertical Axis')
    fig1.set_xlabel("time (s)")
    fig1.set_ylabel("position (m)")
    fig1.legend(loc="upper left")

    fig2 = plt.subplot(222)
    fig2.plot(moca.adj_epoch, moca.adj_horiz, c='b', label='moca horiz')
    fig2.plot(bio.adj_epoch, bio.adj_horiz, c='r', label='bio horiz')
    fig2.set_title('Horizontal Axis')
    fig2.set_xlabel("time (s)")
    fig2.set_ylabel("position (m)")
    fig2.legend(loc="upper left")

    fig3 = plt.subplot(223)
    fig3.plot(moca.adj_epoch, moca.adj_vert, c='b', label='moca vert')
    fig3.plot(bio.adj_epoch, bio.adj_vert, c='r', label='bio vert')
    fig3.set_xlim([30, 36])
    fig3.set_title('Vertical Axis - 3 Reps')
    fig3.set_xlabel("time (s)")
    fig3.set_ylabel("position (m)")
    fig3.legend(loc="upper left")

    fig4 = plt.subplot(224)
    fig4.plot(moca.adj_epoch, moca.adj_horiz, c='b', label='moca horiz')
    fig4.plot(bio.adj_epoch, bio.adj_horiz, c='r', label='bio horiz')
    fig4.set_xlim([30, 36])
    fig4.set_title('Horizontal Axis - 3 Reps')
    fig4.set_xlabel("time (s)")
    fig4.set_ylabel("position (m)")
    fig4.legend(loc="upper left")

    '''
    if AXIS == "vert":
        plt.plot(bio.adj_epoch, bio.adj_vert, c='r', label='bio vert')
        plt.plot(moca.adj_epoch, moca.adj_vert, c='b', label='moca vert')
    elif AXIS == "horiz":
        plt.plot(moca.adj_epoch, moca.adj_horiz, c='b', label='moca horiz')
        plt.plot(bio.adj_epoch, bio.adj_horiz, c='r', label='bio horiz')
    '''

    file_info = bio.get_file_info()
    title = file_info["Movement"] + " " + file_info["Subject"] + " " + MUSCLE\
                + "/" + STAMP + " " + file_info["Run"][:-1] + " "\
                + file_info["Run"][-1:] + " " + file_info["Speed"]

    fig.suptitle(title, size=25)
    fig.savefig(FOLDER + "/" + MUSCLE + '.png', bbox_inches='tight', pad_inches=0.5)
    plt.legend(loc="upper left")
    plt.show()


def find_all_files():
    # Finds all files in directory ending in accel.csv
    files = glob.glob(FOLDER + "/*", recursive=True)
    return files


def get_file_names():
    biostamp_file = ""
    moca_file = ""
    all_files = find_all_files()
    for file in all_files:
        if MUSCLE in file and "position" in file:
            biostamp_file = file
        if "accel" not in file and "gyro" not in file \
                and "position" not in file and "velocity" not in file:
            moca_file = file

    assert biostamp_file != "", "File Not Found"
    assert moca_file != "", "File Not Found"

    return biostamp_file, moca_file


if __name__ == "__main__":
    main()
