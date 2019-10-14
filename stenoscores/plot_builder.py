import csv
import os
import re
import sys

from dateutil import parser
import matplotlib
from matplotlib.ticker import MaxNLocator

import matplotlib.pyplot as plt
import numpy as np


class PlotBuilder:

    def __init__(self):
        self.drill_label_dict = {}
        self.reset_plot()

    def calc_log_stats(self, log_csv_path):
        log_stats = []

        with open(log_csv_path, 'r') as log_file:

            log_reader = csv.DictReader(log_file)
            for line in log_reader:
                date_and_time = line["utc_date_time"]
#                 time_to_complete = line["time_to_complete"]
#                 minutes, seconds = re.split(':', time_to_complete)
#                 seconds_to_complete = int(
#                     datetime.timedelta(
#                         minutes=int(minutes), seconds=int(seconds))
#                     .total_seconds())
                words_per_minute = line["wpm"]
                log_stats.append([date_and_time, words_per_minute])

        return log_stats

    def get_drill_name(self, file_name):
        drill_name = file_name.replace("-random", "").replace("-order", "")
        return drill_name

    def plot_runs(self, log_stats_array, runs_plot_file_path):

        numpy_array = np.array(log_stats_array)

        y = numpy_array[:, 1].astype(float)

        polynomials = 1
        if len(log_stats_array) > 10:
            polynomials = 3
        if len(log_stats_array) > 50:
            polynomials = 5

        x = np.arange(1, len(numpy_array) + 1)

        _, ax = plt.subplots(1, 1)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        polyfit = np.polyfit(x, y, polynomials)
        poly1d = np.poly1d(polyfit)

        linespace = np.linspace(x.min(), x.max())
        plt.plot(linespace, poly1d(linespace), '-r')

        self.set_plot_title(runs_plot_file_path)
        plt.xlabel('Runs')
        plt.ylabel('Words Per Minute')
        plt.plot(x, y, ".")
        plt.tight_layout()
        plt.savefig(runs_plot_file_path)

    def plot_dates(self, log_stats_array, dates_plot_file_path):

        numpy_array = np.array(log_stats_array)

        y = numpy_array[:, 1].astype(float)

        x = [parser.parse(d) for d in numpy_array[:, 0]]

        xs = matplotlib.dates.date2num(x)
        hfmt = matplotlib.dates.DateFormatter('%Y/%m/%d')

        _, ax = plt.subplots(1, 1)
        ax.xaxis.set_major_formatter(hfmt)

        plt.setp(ax.get_xticklabels(), rotation=20)

        polynomials = 1
        if len(log_stats_array) > 10:
            polynomials = 3
        if len(log_stats_array) > 50:
            polynomials = 5

        x_num = matplotlib.dates.date2num(x)

        # smooth polyfit from https://stackoverflow.com/a/17639070/2174538
        polyfit = np.polyfit(x_num, y, polynomials)
        poly1d = np.poly1d(polyfit)

        linespace = np.linspace(x_num.min(), x_num.max())
        num2dates = matplotlib.dates.num2date(linespace)
        self.set_plot_title(dates_plot_file_path)
        plt.xlabel('Dates')
        plt.ylabel('Words Per Minute')
        plt.plot(num2dates, poly1d(linespace), '-r')

        plt.plot(xs, y, ".")

        plt.tight_layout()
        plt.savefig(dates_plot_file_path)

    def set_plot_title(self, plot_file_path):
        file_name = os.path.splitext(os.path.basename(plot_file_path))[0]
        drill_label = self.get_drill_name(file_name)

        plot_title = drill_label
        if file_name.endswith("-random"):
            plot_title = "Randomized " + plot_title
        plot_title = plot_title.replace("-", " ")
        plot_title = plot_title.title()
        plt.title(plot_title)

    def reset_plot(self):
        self.fig = plt.figure()
        plt.clf()


if __name__ == '__main__':
    LOG_DIR = sys.argv[1]
    PLOT_DIR = sys.argv[2]
    RUNS_DIR = os.path.join(PLOT_DIR, "runs")
    if not os.path.exists(RUNS_DIR):
        os.makedirs(RUNS_DIR)
    DATES_DIR = os.path.join(PLOT_DIR, "dates")
    if not os.path.exists(DATES_DIR):
        os.makedirs(DATES_DIR)
    
    plot_builder = PlotBuilder()

    for log_csv_name in os.listdir(LOG_DIR):
        c_log_csv_path = os.path.join(LOG_DIR, log_csv_name)

        c_log_stats_array = plot_builder.calc_log_stats(c_log_csv_path)

        plot_builder.reset_plot()
        c_runs_plot_file_path = os.path.join(RUNS_DIR,
                                             re.sub(".csv$", ".svg",
                                                    log_csv_name))
        plot_builder.plot_runs(c_log_stats_array, c_runs_plot_file_path)

        plot_builder.reset_plot()
        c_dates_plot_file_path = os.path.join(DATES_DIR,
                                              re.sub(".csv$", ".svg",
                                                     log_csv_name))
        plot_builder.plot_dates(c_log_stats_array, c_dates_plot_file_path)
