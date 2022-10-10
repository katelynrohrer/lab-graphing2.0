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
    def __init__(self, path, stamp, arm_len_meters, dist, hei):
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
        #self.real_time = []
        #self._start_time = self.find_start_time()

        # DO NOT TRUST THESE, THEY BREAK ALL THE TIME
        #self._peaks_vert, _ = find_peaks(self.vert, height=hei, distance=dist)
        #self._peaks_horiz, _ = find_peaks(self.horiz, height=hei, distance=dist)

    def _get_coords(self):
        """
        Parses through the dictionary and gets the relevant x and y coordinates
        Ps x and y are flipped because on a screen (0,0) is the top left corner
        """
        scale = self._scale()  # Scales px to m
        for key in self._data:
            if "x" in key.lower() and self._stamp in key.lower():
                # I HAVE NO IDEA WHY I HAVE TO ADD 1.2 HELP
                self._x = [-float(x)*scale+1.2 for x in self._data[key]]
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
        for i in range(len(self.vert)-1):
            if abs(self.vert[i] - self.vert[i+1]) > amount:
                self.vert[i+1] = self.vert[i]

            if abs(self.horiz[i] - self.horiz[i+1]) > amount:
                self.horiz[i+1] = self.horiz[i]

    def vert_adj(self, amt):
        """
        Shifts vertical and horizontal data (both of these are y-axis, so
        shifting both together doesn't hurt anything for now - might later)
        :param amt: The amount to adjust in px
        """
        self.vert = [x + amt for x in self.vert]
        self.horiz = [y + amt for y in self.horiz]

    def horiz_adj(self, amt):
        """
        Shifts seconds by the amount given
        :param amt: The amount to adjust in px
        """
        self.epoch = [y + amt for y in self.epoch]

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

    '''
    def find_start_time(self):
        video_path = "ChestAA.CH2M.Run1.Fast copy/ChestAA.Cam1.CH2M.Run1.MOCA.7:25:22.Fast.MOV"
        parser = createParser(video_path)
        metadata = extractMetadata(parser)
        # Get local timezone
        to_zone = tz.tzlocal()

        time_str = str(metadata.get("creation_date"))  #.astimezone(to_zone)
        year = int(time_str[:time_str.index("-")])
        month = int(time_str[time_str.index("-")+1:time_str.index("-")+3])
        day = int(time_str[time_str.index("-")+4:time_str.index(" ")])
        hour = int(time_str[time_str.index(" ")+1:time_str.index(":")])
        minute = int(time_str[time_str.index(":")+1:time_str.index(":")+3])
        second = int(time_str[time_str.rindex(":")+1:])
        t = datetime.datetime(year, month, day, hour, minute, second, tzinfo=to_zone)
        new = (calendar.timegm(t.timetuple())) * 1000000
        #print(calendar.timegm(t.timetuple()))
        self.real_time.append(new)

        #print(datetime.datetime.fromtimestamp(new))
        #print(self.real_time[0], "ear;oguaeopguhreaoguheo[")
        return new

    def find_real_time(self):
        #for i in range(len(self.sec)):
        #    self.real_time.append(self._start_time+i/60)
        self.real_time = [self._start_time+(i/60*1000000) for i in range(len(self.sec))]
    '''

class BiostampData:
    def __init__(self, path, dist, hei=0.5):
        self._path = path
        self._data = make_dict(self._path)
        self._add_seconds()
        self._x = []
        self.horiz = []
        self._y = []
        self._z = []
        self.vert = []
        self.epoch = self._data["Timestamp (microseconds)"]
        #self.sec = self._data["Seconds"]
        #self.real_time = []
        #self.real_time_from_midnight = []
        self._get_coords()
        self._file_info = self.get_file_info()
        self._peaks_vert, _ = find_peaks(self.vert, height=hei, distance=dist)
        self._peaks_horiz, _ = find_peaks(self.horiz, height=hei, distance=dist)

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

    '''
    def add_real_time(self):
        # given epoch time
        for epoch_time in self.ms:
            #epoch_time -= 57015838440
            date_time = datetime.datetime.fromtimestamp(epoch_time/1000000.0)
            ms_left = epoch_time % 1000000 / 1000

            datetime_str = date_time.strftime("%Y - %m - %d  %H : %M : %S")
            #print(datetime_str)
            datetime_str += " : " + str(ms_left)
            self.real_time.append(datetime_str)
            self.real_time_from_midnight.append(epoch_time)
    '''

'''
class adjMocaData:
    """
    This is what broke my soul today. I tried to adjust the data but it's not
    even close to working. Scrap the whole thing if you want idc
    It might help to make an adjMocaData class with 2 objects:
        1 for vert axis and 1 for horiz
    Cause that was my big issue with this
    """
    def __init__(self, mocaObj, bioObj):
        self._moca = mocaObj
        self._bio = bioObj

        # Trying to align the start and end points of the data through
        # first and last indexes
        self._FIRST_vert = len(self._bio.sec[0: self._bio.get_peaks_vert()[0]])
        self._FIRST_horiz = len(self._bio.sec[0: self._bio.get_peaks_horiz()[0]])
        self._LAST = self._moca.sec[0]
        self._get_last()

        self.sec_vert = self._moca.sec[self._moca.get_peaks_vert()[0]:]
        self.sec_horiz = self._moca.sec[self._moca.get_peaks_horiz()[0]:]

        self._peaks_vert = [x-self._moca.get_peaks_vert()[0] for x in self._moca.get_peaks_vert()]
        self._peaks_horiz = [x-self._moca.get_peaks_horiz()[0] for x in self._moca.get_peaks_horiz()]

        self.vert = self._moca.vert[self._moca.get_peaks_vert()[0]:]
        self.horiz = self._moca.horiz[self._moca.get_peaks_horiz()[0]:]


    def _get_last(self):
        """
        Gets the value of the last data point in biostamp and finds the last
        moca index using that
        """
        for x in range(len(self._moca.sec)):
            if self._moca.sec[x] >= self._bio.sec[-1]:
                self._LAST = x
                break


    def get_vert_align(self):
        """
        Right now it takes the first 10 data points and tries to vertically
        align the data through their average - it's inaccurate but okay for
        now as an estimate
        """
        DIFFS_VERT = []
        DIFFS_HORIZ = []
        for i in range(10):
            DIFFS_VERT.append(float(self._bio.vert[i]) - float(self._moca.vert[i]))
            DIFFS_HORIZ.append(float(self._bio.horiz[i]) - float(self._moca.horiz[i]))

        AVG_DIFF_VERT = sum(DIFFS_VERT) / 10
        AVG_DIFF_HORIZ = sum(DIFFS_HORIZ) / 10

        self.vert = [x+AVG_DIFF_VERT for x in self._moca.vert]
        self.horiz = [x+AVG_DIFF_HORIZ for x in self._moca.horiz]
'''

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

