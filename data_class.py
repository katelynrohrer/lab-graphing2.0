"""
File: data_class.py
Author: Katelyn Rohrer
Description: This file defines the classes needed to graph on making_graphs.py

"""

import csv, glob, math
from scipy.signal import find_peaks
import datetime, calendar
import making_graphs
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from dateutil import tz
import pytz


class MocaData:
    """
    So far there's only one instance of this object which is created
    in the main. Holds all data concerning moca.
    """
    def __init__(self, path, stamp, arm_len_meters):
        self._path = path
        self._file_name = self._path[self._path.rfind("/")+1:]
        self._movement = self._file_name[:self._file_name.find(".")]
        self._stamp = stamp.lower()
        self._arm_len_meters = arm_len_meters
        self._data = make_dict(self._path)
        #self._data["Seconds"] = [float(frame)/60 for frame in range(len(self._data["Frame #"]))]
        self._x, self._y = [], []  # Here, x and horiz are the same but x is raw data
        self.horiz, self.vert = [], []  # and horiz is modified. Same with y and vert
        #self.sec = self._data["Seconds"]
        self.epoch = self._data["Timestamp (microseconds)"]
        self._get_coords()
        self.adj_vert = [i-self.vert[0] for i in self.vert]
        self.adj_horiz = [i-self.horiz[0] for i in self.horiz]
        self.adj_epoch = self.epoch.copy()

        self._peaks_vert = []
        self._peaks_horiz = []
        self._find_peaks()

    def _find_peaks(self):
        if self._movement == "ChestAA" and "fast" in self._file_name.lower():
            self._peaks_vert, _ = find_peaks(self.adj_vert, height=0.75, distance=100)
            self._peaks_horiz, _ = find_peaks(self.adj_horiz, height=0.85, distance=100)
        # TODO ALL OTHER SCALES

    def _get_coords(self):
        """
        Parses through the dictionary and gets the relevant x and y coordinates
        Ps x and y are flipped because on a screen (0,0) is the top left corner
        """
        scale = self._scale()  # Scales px to m
        for key in self._data:
            if "x" in key.lower() and self._stamp in key.lower():
                self._x = [-float(x)*scale for x in self._data[key]]
                self.horiz = self._x.copy()
            elif "y" in key.lower() and self._stamp in key.lower():
                self._y = [-float(y)*scale for y in self._data[key]]
                self.vert = self._y.copy()

    def _scale(self):
        """
        Right now, this takes the moca marker points on the hand and shoulder,
        finds their distance in px, and uses the known arm measurement
        to scale the two together
        :return: meters per px float
        """
        if self._movement == "ChestAA":
            shoulder_x = self._data["Shoulder Green X"][0]
            shoulder_y = self._data["Shoulder Green Y"][0]

            hand_x = self._data["Hand Pink X"][0]
            hand_y = self._data["Hand Pink Y"][0]

            leg1 = hand_y - shoulder_y
            leg2 = hand_x - shoulder_x

            arm_len_px = math.sqrt((leg1 ** 2) + (leg2 ** 2))
            scale = self._arm_len_meters / arm_len_px

            return scale

        elif self._movement == "ShoulderFE":
            return 1  # TODO SCALE 2
        elif self._movement == "ShoulderAA":
            return 1  # TODO SCALE 3
        elif self._movement == "BicepC":
            return 1  # TODO SCALE 4
        elif self._movement == "FingerP":
            return 1  # TODO SCALE 5
        elif self._movement == "BodyLean":
            return 1  # TODO SCALE 6

    def smooth(self, amount=0.1):
        """
        Smoothes the data by checking for a large jump in data between frames
        and skipping those frames
        :param amount: The distance of the jump in meters
        """
        for i in range(len(self.adj_vert)-1):
            if abs(self.adj_vert[i] - self.adj_vert[i+1]) > amount:
                self.adj_vert[i+1] = self.adj_vert[i]

            if abs(self.adj_horiz[i] - self.adj_horiz[i+1]) > amount:
                self.adj_horiz[i+1] = self.adj_horiz[i]

    def man_vert_adj(self, amt):
        """
        Shifts vertical and horizontal data (both of these are y-axis, so
        shifting both together doesn't hurt anything for now - might later)
        :param amt: The amount to adjust in px
        """
        self.adj_vert = [x + amt for x in self.adj_vert]
        self.adj_horiz = [y + amt for y in self.adj_horiz]

    def man_horiz_adj(self, amt):
        """
        Shifts seconds by the amount given
        :param amt: The amount to adjust in px
        """
        self.adj_epoch = [y + amt for y in self.adj_epoch]

    def set_adj_epoch(self, first_epoch):
        self.adj_epoch = [(i - first_epoch) / 1000000 for i in self.epoch]

    def set_adj_vert(self, bio_peak_val, adj):
        moca_peak_val = self.adj_vert[self._peaks_vert[0]]
        change = -(moca_peak_val - bio_peak_val) - adj
        self.adj_vert = [i + change for i in self.adj_vert]

    def get_movement(self):
        return self._movement

    def get_dict(self):
        return self._data

    def get_stamp(self):
        return self._stamp

    def get_peaks_vert(self):
        return self._peaks_vert

    def get_peaks_horiz(self):
        return self._peaks_horiz


class BiostampData:
    def __init__(self, path):
        self._path = path
        self._data = make_dict(self._path)
        self._add_seconds()
        self._x = []
        self.horiz = []
        self._y = []
        self._z = []
        self.vert = []
        self.epoch = self._data["Timestamp (microseconds)"]
        self._get_coords()
        self._file_info = self.get_file_info()
        self.adj_vert = [i-self.vert[0] for i in self.vert]
        self.adj_horiz = [i-self.horiz[0] for i in self.horiz]
        self.adj_epoch = self.epoch.copy()
        self._peaks_vert = []
        self._peaks_horiz = []
        self._find_peaks()

    def _find_peaks(self):
        if self._file_info["Movement"].lower() == "chestaa" \
                and self._file_info["Speed"].lower() == "fast":
            self._peaks_vert, _ = find_peaks(self.adj_vert, height=0.4, distance=100)
            self._peaks_horiz, _ = find_peaks(self.adj_horiz, height=0.5, distance=100)

    def _add_seconds(self):
        self._data["Seconds"] = []
        for ms in range(len(self._data["Timestamp (microseconds)"])):
            self._data["Seconds"].append(
                (float(self._data["Timestamp (microseconds)"][ms]) / 1000000)
                - (float(self._data["Timestamp (microseconds)"][0]) / 1000000))

    def _get_coords(self):
        """
        Gets the vertical and horizontal coordinates from the data dict
        The z-axis was normalized to be vertical but x and y were not
        normalized beforehand so that's why we have self.horiz
        """
        for key in self._data:
            if "x" in key.lower():
                self._x = [float(x) for x in self._data[key]]
            elif "y" in key.lower():
                self._y = [-float(y) for y in self._data[key]]
            elif "z" in key.lower():
                self._z = [float(z) for z in self._data[key]]
                self.vert = self._z.copy()

        self.horiz = [math.sqrt((self._x[i]**2) + (self._z[i]**2)) for i in range(len(self._x))]

    def get_peaks_vert(self):
        return self._peaks_vert

    def get_peaks_horiz(self):
        return self._peaks_horiz

    def get_file_info(self):
        """
        Parses through file name to get info about the trial
        """
        line = self._path.split("/")[-1].split(".")
        self._file_info = {"Movement": line[0], "Muscle": line[1],
                           "Subject": line[2],  "Run": line[3],
                           "Speed": line[6]}
        return self._file_info

    def get_dict(self):
        return self._data

    def set_adj_epoch(self, first_epoch):
        self.adj_epoch = [(i-first_epoch)/1000000 for i in self.epoch]


def make_dict(path):
    """
    Makes a dictionary of the data from a csv file
    First row is key names and each column is a list within
    its respective key
    :param path: The str path to the file
    :return: Returns a dictionary of the data
    """
    data = {}
    csv_reader = csv.reader(open(path, 'r'))

    # Setup dictionary using first row
    for row in csv_reader:
        for item in row:
            data[item] = []
        break

    # Append data to the correct dictionary list
    for row in csv_reader:
        x = 0
        for key in data:
            if not row[x] == "":
                data[key].append(float(row[x]))
            else:
                data[key].append(float(data[key][-1]))
            x += 1

    return data


if __name__ == "__main__":
    making_graphs.main()

