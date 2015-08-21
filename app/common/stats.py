__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.
import math

def mean(data):
    return sum(data) / float(len(data))


def median(data):
    data = sorted(data)
    data_len = len(data)
    x1 = data_len / 2
    if data_len % 2 == 0:
        data = [data[x1 - 1], data[x1]]
        return mean(data)
    return data[x1]


def st_dev(data):
    """Return standard sample deviation of input data

    :param data: 1D, list, tuple,...
    :return:
    """
    data_len = float(len(data))
    data_mean = mean(data)
    data1 = []
    for x in data:
        data1.append((x - data_mean)**2)
    return math.sqrt(sum(data1)/(data_len - 1))


def diff(data):
    previous, data = data[0], data[1:]
    out_data = []
    for x in data:
        out_data.append(x - previous)
        previous = x
    return out_data


def running_consumption(data, time_series):
    """Calculates running consumption E/day

    :param data:
    :param time_series:
    """

    data_d = diff(data)
    time_d = diff(time_series)
    out_data = []
    for d_d, t_d in zip(data_d, time_d):
        # print type(t_d)
        # print d_d, "|", t_d, "|", float(t_d.total_seconds())/60/60, (float(d_d)/float(t_d.total_seconds()))*60*60*24
        out_data.append((float(d_d)/float(t_d.total_seconds()))*60*60*24)
    return out_data, data_d, time_d


class SimpleMovingAverage(object):
    def __init__(self, navg, items):
        self.navg = navg
        self.items = items

    def calculate(self):
        av = []
        for i in range(len(self.items)):
            if i + 1 < self.navg:
                av.append(0)
            else:
                av.append(sum(self.items[i + 1 - self.navg:i + 1]) / self.navg)
        return av