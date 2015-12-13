from app import db
from app.models import AppSettings
import datetime
from StringIO import StringIO
import csv
import os

__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.


class SettingReturn(object):
    def __init__(self, value, default):
        self.value = value
        self.default = default


def get_setting(setting_name, ret_type):
    value = ret_type(db.session.query(AppSettings.value).filter(AppSettings.name == setting_name).first()[0])
    default = ret_type(db.session.query(AppSettings.default_value).filter(AppSettings.name == setting_name).first()[0])
    out = SettingReturn(value=value, default=default)
    return out


def time_since_epoch(t):
    return (t - datetime.datetime(1970, 1, 1)).total_seconds()


def read_temp_log(files, back_period):
    out = []
    for csv_file_path in files:
        with open(csv_file_path, "rb") as csv_file:
            try:
                hm = tail(csv_file, back_period)
                csv_file = StringIO(hm)
                data = csv.reader(csv_file, delimiter=",")
                for row in data:
                    row = [remove_non_ascii(c) for c in row]
                    wanted = map(int, "0 1 2 3 4 9 14 19 24".split())
                    out_row = []
                    error = False
                    for i in wanted:
                        try:
                            out_row.append(row[i])
                        except IndexError:
                            error = True
                            break
                    if not error:
                        out.append(out_row)
            except ValueError:
                out = []
    out = list(reversed(out))
    out.insert(0, get_setting("SERVER_TEMP_TABLE_HEADER", str).value.split("|"))
    return out


def _tail(f, window=20):
    BUFSIZ = 1024
    f.seek(0, 2)  # move to the end of the file
    bites = f.tell()  # where in the file -> end of file -> file size [bytes]
    size = window
    block = -1
    data = []
    while size > 0 and bites > 0:
        if bites - BUFSIZ > 0:
            # Seek back one whole BUFSIZ
            f.seek(block * BUFSIZ, 2)
            # read BUFFER
            data.append(f.read(BUFSIZ))
        else:
            # file too small, start from beginning
            f.seek(0, 0)
            # only read what was not read
            data.append(f.read(bites))
        lines_found = data[-1].count('\n')
        size -= lines_found
        bites -= BUFSIZ
        block -= 1
    data.reverse()
    return '\n'.join(''.join(data).splitlines()[-window:])


def tail(f, window=20):
    t = _tail(f, window + 1)
    n, t = t.split("\n", 1)
    return t


def remove_non_ascii(mystring):
    out = ""
    for s in mystring:
        try:
            s.decode('ascii')
            out += s
        except UnicodeDecodeError:
            out += " "
    return out


def get_files():
    csv_folder = get_setting("SERVER_TEMP_CSV_FOLDER", str)
    csv_files = []
    files = os.listdir(unicode(csv_folder.value))
    for csv_file in files:
        name, ext = os.path.splitext(csv_file)
        if ext == ".csv":
            csv_files.append(os.path.join(csv_folder.value, csv_file))
    return csv_files


def update_setting(setting_name, new_value, ret_type):
    to_update = db.session.query(AppSettings).filter(AppSettings.name == setting_name).first()
    to_update.value = ret_type(new_value)
    db.session.commit()
