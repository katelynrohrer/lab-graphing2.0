
import csv, os
import get_epoch_time as epoch

CSV_PATH = "ChestAA.CH2M.Run1.Slow copy/ChestAA.Cam1.CH2M.Run1.MOCA.7:25:22.Slow.csv"

# !! EITHER VIDEO_PATH OR START_EPOCH MUST BE EMPTY !!
VIDEO_PATH = ""

# ChestAA.CH2M.Run1.Fast Start Epoch - 1658789494
# ChestAA.CH2M.Run1.Slow Start Epoch - 1658789401
START_EPOCH = int("1658789494")  # IMPORTANT - THIS IS A 10-DIGIT NUMBER

def make_dict():
    """
    Makes a dictionary of the data from a csv file
    First row is key names and each column is a list within
    its respective key
    :param path: The str path to the file
    :return: Returns a dictionary of the data
    """
    data = {}
    csv_reader = csv.reader(open(CSV_PATH, 'r'))

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


def add_col_using_video():
    start_epoch = epoch.get_epoch_time(VIDEO_PATH)
    data = make_dict()
    data["Timestamp (microseconds)"] = []
    for i in range(len(data["Frame #"])):
        data["Timestamp (microseconds)"].append((start_epoch + i/60) * 1000000)
    export(data)


def add_col_using_start_epoch():
    data = make_dict()
    data["Timestamp (microseconds)"] = []
    for i in range(len(data["Frame #"])):
        data["Timestamp (microseconds)"].append((START_EPOCH + i/60) * 1000000)
    export(data)


def export(data):
    folder = CSV_PATH[:CSV_PATH.rindex("/") + 1]
    file_name = CSV_PATH[CSV_PATH.rindex("/")+1:-4]
    raw_row = list(data.keys())

    current_dir = os.path.abspath('')
    file_path = os.path.join(current_dir, folder, file_name + ".Epoch22.csv")

    # Labels
    with open(file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(raw_row)

    #  Data values
    with open(file_path, 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        for i in range(len(data[raw_row[0]])):
            current_row = []
            for item in raw_row:
                current_row.append(data[item][i])
            csv_writer.writerow(current_row)


def main():
    assert not VIDEO_PATH or not START_EPOCH, "Cannot have both filled in"
    if VIDEO_PATH:
        add_col_using_video()
    elif START_EPOCH:
        add_col_using_start_epoch()
    else:
        print("ERROR: Not completed")


if __name__ == "__main__":
    main()
