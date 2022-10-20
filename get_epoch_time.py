

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

    if hour < 0:
        hour = 24 - hour
        date = f"{video_raw_date.date-1:02d}"

        str_date = str(video_raw_date)
        metadata_given_time = str_date[:str_date.index(" ") - 2] + date + " " + hour + str_date[str_date.index(" ") + 3:]
    else:
        str_date = str(video_raw_date)
        metadata_given_time = str_date[:str_date.index(" ")+1] + hour + str_date[str_date.index(" ")+3:]

    # Get local timezone
    time_str_n = metadata.get("creation_date")
    epoch = (calendar.timegm(time_str_n.timetuple()))
    epoch_time_readable = datetime.datetime.fromtimestamp(epoch)

    assert str(metadata_given_time) == str(epoch_time_readable),\
        f"Error with converting. Times not equal\n" \
        f"                Given time from file: {metadata_given_time}\n" \
        f"                Epoch time converted: {epoch_time_readable}"

    return epoch
