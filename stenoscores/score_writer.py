'''
Created on 13.10.2019

@author: mkoerner
'''
from datetime import datetime
from os import path
import sys
from tkinter import Tk


class ScoreWriter(object):
    '''
    classdocs
    '''

    def __init__(self, stats_folder):
        '''
        Constructor
        '''
        self.stats_folder_path = stats_folder
        
    def write(self):
        clipboard_content = Tk().clipboard_get()
        clipboard_lines = clipboard_content.splitlines()
        if(len(clipboard_lines) < 4):
            print("clipboard does not contain stats")
            return
        # not always the first line
        file_name = None
        for line in clipboard_lines:
            if file_name is None:
                if line:
                    file_name = line.lower().replace(" ", "-")
                    print(file_name)
            if "with no uncorrected errors!" in line:
                print("stats: " + line)
                stats_split = line.split(" ")
                time = stats_split[1]
                wpm = stats_split[4]
                self.write_to_file(file_name, time, wpm)

    def write_to_file(self, file_name, time, wpm):
        file_name_with_suffix = file_name + '.csv'
        stats_file_path = path.join(self.stats_folder_path, file_name_with_suffix)
        write_header = False
        if not path.exists(stats_file_path):
            write_header = True

        with open(stats_file_path, 'a') as stats_file:  
            if write_header:
                stats_file.write('utc_date_time,time_to_complete,wpm\n')
            
            utc_date_time = datetime.now().replace(microsecond=0).isoformat()
            stats_file.write(utc_date_time + ',' + time + ',' + wpm + '\n')
            print()
    
    
if __name__ == '__main__':

    stats_folder = sys.argv[1]
    
    score_writer = ScoreWriter(stats_folder)

    score_writer.write()
