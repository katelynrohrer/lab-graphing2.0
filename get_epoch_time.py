

from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from dateutil import tz
import datetime, calendar

def get_epoch_time(video_path):
    # Finds video and gets metadata
    parser = createParser(video_path)
    metadata = extractMetadata(parser)
    video_raw_date = metadata.get("creation_date")

    # Converts metadata time to MST
    hour = f"{video_raw_date.hour-7:02d}"
    str_date = str(video_raw_date)
    metadata_given_time = str_date[:str_date.index(" ")+1] + hour + str_date[str_date.index(" ")+3:]
    #print(metadata_given_time, "Given time from file")

    # Get local timezone
    time_str_n = metadata.get("creation_date")
    epoch = (calendar.timegm(time_str_n.timetuple()))
    #print(epoch, "   Found epoch time")
    epoch_time_readable = datetime.datetime.fromtimestamp(epoch)
    #print(epoch_time_readable, "Epoch time readable")

    assert str(metadata_given_time) == str(epoch_time_readable),\
        f"Error with converting. Times not equal\n" \
        f"                Given time from file: {metadata_given_time}\n" \
        f"                Epoch time converted: {epoch_time_readable}"

    return epoch

#epoch = get_epoch_time("ChestAA.CH2M.Run1.Fast copy/ChestAA.Cam1.CH2M.Run1.MOCA.7:25:22.Fast.MOV")
#print("Epoch time:", epoch)