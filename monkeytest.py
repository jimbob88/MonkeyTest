#!/usr/bin/env python
'''
MonkeyTest -- test your hard drive read-write speed in Python
A simplistic script to show that such system programming
tasks are possible and convenient to be solved in Python

The file is being created, then written with random data, randomly read
and deleted, so the script doesn't waste your drive

(!) Be sure, that the file you point to is not something
    you need, cause it'll be overwritten during test

Runs on both Python3 and 2, despite that I prefer 3
Has been tested on 3.5 and 2.7 under ArchLinux
Has been tested on 3.5.2 under Ubuntu Xenial
Has been tested on 3.6.7 under Ubuntu Bionic
'''
from __future__ import division, print_function  # for compatability with py2
try:
    import Tkinter as tk
    import ttk
    import tkFileDialog as filedialog
except ModuleNotFoundError:
    import tkinter as tk
    import tkinter.ttk as ttk
    from tkinter import filedialog

import os, sys
from random import shuffle
import argparse
import json
import matplotlib.pyplot as plt
import numpy as np
import colorama as col
#from threading import Thread

ASCIIART = r'''Brought to you by coding monkeys.
Eat bananas, drink coffee & enjoy!
                 _
               ,//)
               ) /
              / /
        _,^^,/ /
       (G,66<_/
       _/\_,_)    _
      / _    \  ,' )
     / /"\    \/  ,_\
  __(,/   >  e ) / (_\.oO
  \_ /   (   -,_/    \_/
    U     \_, _)
           (  /
            >/
           (.oO
''' # r''''''
# ASCII-art: used part of text-image @ http://www.ascii-art.de/ascii/mno/monkey.txt
# it seems that its original author is Mic Barendsz (mic aka miK)
# text-image is a bit old (1999) so I couldn't find a way to communicate with author
# if You're reading this and You're an author -- feel free to write me

try:  # if Python >= 3.3 use new high-res counter
    from time import perf_counter as time
except ImportError:  # else select highest available resolution counter
    if sys.platform[:3] == 'win':
        from time import clock as time
    else:
        from time import time


def get_args():
    parser = argparse.ArgumentParser(description='Arguments', formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--file',
                        required=False,
                        action='store',
                        default='/tmp/monkeytest',
                        help='The file to read/write to')
    parser.add_argument('-s', '--size',
                        required=False,
                        action='store',
                        default=128,
                        help='Total MB to write')
    parser.add_argument('-w', '--write-block-size',
                        required=False,
                        action='store',
                        default=1024,
                        help='The block size for writing in bytes')
    parser.add_argument('-r', '--read-block-size',
                        required=False,
                        action='store',
                        default=512,
                        help='The block size for reading in bytes')
    parser.add_argument('-j', '--json',
                        required=False,
                        action='store',
                        help='Output to json file')
    parser.add_argument('-m', '--mode',
                        required=False,
                        default='cli',
                        help='Choose either CLI or GUI')

    args = parser.parse_args()
    return args


class Benchmark:

    def __init__(self, file,write_mb, write_block_kb, read_block_b):
        self.file = file
        self.write_mb = write_mb
        self.write_block_kb = write_block_kb
        self.read_block_b = read_block_b

    def run(self, show_progress=True, update_pb=False):
        wr_blocks = int(self.write_mb * 1024 / self.write_block_kb)
        rd_blocks = int(self.write_mb * 1024 * 1024 / self.read_block_b)
        self.write_results = self.write_test( 1024 * self.write_block_kb, wr_blocks, show_progress, update_pb)
        self.read_results = self.read_test(self.read_block_b, rd_blocks, show_progress, update_pb)

    def write_test(self, block_size, blocks_count, show_progress=True, update_pb=False):
        '''
        Tests write speed by writing random blocks, at total quantity
        of blocks_count, each at size of block_size bytes to disk.
        Function returns a list of write times in sec of each block.
        '''
        f = os.open(self.file, os.O_CREAT | os.O_WRONLY, 0o777)  # low-level I/O

        self.write_took = []
        self.wperc_took = []
        prev_perc = 0
        for i in range(blocks_count):
            if show_progress:
                # dirty trick to actually print progress on each iteration
                sys.stdout.write('\rWriting: {:.2f} %'.format(
                    (i + 1) * 100 / blocks_count))
                sys.stdout.flush()
            if update_pb is not False:
                update_pb["value"] = ((i + 1) * 100 / blocks_count)
                update_pb.update()
                prev_perc = ((i + 1) * 100 / blocks_count)

            buff = os.urandom(block_size)
            start = time()
            os.write(f, buff)
            os.fsync(f)  # force write to disk
            t = time() - start
            self.write_took.append(t)
            self.wperc_took.append(((i + 1) * 100 / blocks_count))

        os.close(f)
        if update_pb is not False:
            update_pb["value"] = 100
        return self.write_took

    def read_test(self, block_size, blocks_count, show_progress=True, update_pb=False):
        '''
        Performs read speed test by reading random offset blocks from
        file, at maximum of blocks_count, each at size of block_size
        bytes until the End Of File reached.
        Returns a list of read times in sec of each block.
        '''
        f = os.open(self.file, os.O_RDONLY, 0o777)  # low-level I/O
        # generate random read positions
        offsets = list(range(0, blocks_count * block_size, block_size))
        shuffle(offsets)

        self.read_took = []
        self.rperc_took = []
        prev_perc = 0
        for i, offset in enumerate(offsets, 1):
            if show_progress and i % int(self.write_block_kb * 1024 / self.read_block_b) == 0:
                # read is faster than write, so try to equalize print period
                sys.stdout.write('\rReading: {:.2f} %'.format(
                    (i + 1) * 100 / blocks_count))
                sys.stdout.flush()
            if update_pb is not False and ((i + 1) * 100 / blocks_count)-1 > prev_perc:
                update_pb["value"] = ((i + 1) * 100 / blocks_count)
                update_pb.update()
                prev_perc = ((i + 1) * 100 / blocks_count)

            start = time()
            os.lseek(f, offset, os.SEEK_SET)  # set position
            buff = os.read(f, block_size)  # read from position
            t = time() - start
            if not buff: break  # if EOF reached
            self.read_took.append(t)
            self.rperc_took.append(((i + 1) * 100 / blocks_count))

        os.close(f)
        if update_pb is not False:
            update_pb["value"] = 100
        return self.read_took

    def print_result(self):
        result = ('\n\nWritten {} MB in {:.4f} s\nWrite speed is  {:.2f} MB/s'
                  '\n  max: {max:.2f}, min: {min:.2f}\n'.format(
            self.write_mb, sum(self.write_results), self.write_mb / sum(self.write_results),
            max=self.write_block_kb / (1024 * min(self.write_results)),
            min=self.write_block_kb / (1024 * max(self.write_results))))
        result += ('\nRead {} x {} B blocks in {:.4f} s\nRead speed is  {:.2f} MB/s'
                   '\n  max: {max:.2f}, min: {min:.2f}\n'.format(
            len(self.read_results), self.read_block_b,
            sum(self.read_results), self.write_mb / sum(self.read_results),
            max=self.read_block_b / (1024 * 1024 * min(self.read_results)),
            min=self.read_block_b / (1024 * 1024 * max(self.read_results))))
        print(result)
        print(ASCIIART)

    def return_result(self):
        result = ('\n\nWritten {} MB in {:.4f} s\nWrite speed is  {:.2f} MB/s'
                  '\n  max: {max:.2f}, min: {min:.2f}\n'.format(
            self.write_mb, sum(self.write_results), self.write_mb / sum(self.write_results),
            max=self.write_block_kb / (1024 * min(self.write_results)),
            min=self.write_block_kb / (1024 * max(self.write_results))))
        result += ('\nRead {} x {} B blocks in {:.4f} s\nRead speed is  {:.2f} MB/s'
                   '\n  max: {max:.2f}, min: {min:.2f}\n'.format(
            len(self.read_results), self.read_block_b,
            sum(self.read_results), self.write_mb / sum(self.read_results),
            max=self.read_block_b / (1024 * 1024 * min(self.read_results)),
            min=self.read_block_b / (1024 * 1024 * max(self.read_results))))

        return result


    def get_json_result(self,output_file):
        results_json = {}
        results_json["Written MB"] = self.write_mb
        results_json["Write time (sec)"] = round(sum(self.write_results),2)
        results_json["Write speed in MB/s"] = round(self.write_mb / sum(self.write_results),2)
        results_json["Read blocks"] = len(self.read_results)
        results_json["Read time (sec)"] = round(sum(self.read_results),2)
        results_json["Read speed in MB/s"] = round(self.write_mb / sum(self.read_results),2)
        with open(output_file,'w') as f:
            json.dump(results_json,f)

class benchmark_gui:
    def __init__(self, master, file, write_mb, write_block_kb, read_block_b):
        self.master = master
        self.master.title('Monkey Test')
        self.master.resizable(0, 0)

        self.main_frame = ttk.Frame(self.master)
        self.main_frame.pack()

        self.current_file = tk.StringVar()
        self.current_file.set(file)

        self.write_mb = tk.IntVar()
        self.write_mb.set(write_mb)

        self.write_block_kb = tk.IntVar()
        self.write_block_kb.set(write_block_kb)

        self.read_block_b = tk.IntVar()
        self.read_block_b.set(read_block_b)

        self.show_progress = tk.IntVar()
        self.show_progress.set(1)

        self.initialize()

    def initialize(self):
        ttk.Label(self.main_frame, textvariable=self.current_file, relief='groove').grid(row=1, column=1, padx=5,pady=5)
        ttk.Button(self.main_frame, text='Open', command=lambda: self.current_file.set(filedialog.asksaveasfilename(initialdir = "~",title = "Save As" ))).grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(self.main_frame, text='Write MB').grid(row=2, column=1, padx=5, pady=5)
        self.write_mb_spinbox = tk.Spinbox(self.main_frame, justify='center', textvariable=self.write_mb, width=8)
        self.write_mb_spinbox.grid(row=2, column=2, padx=5, pady=5)

        ttk.Label(self.main_frame, text='Write Block KB').grid(row=3, column=1, padx=5, pady=5)
        self.write_block_kb_spinbox = tk.Spinbox(self.main_frame, justify='center', textvariable=self.write_block_kb, width=8)
        self.write_block_kb_spinbox.grid(row=3, column=2, padx=5, pady=5)

        ttk.Label(self.main_frame, text='Read Block B').grid(row=4, column=1, padx=5, pady=5)
        self.read_block_b_spinbox = tk.Spinbox(self.main_frame, justify='center', textvariable=self.read_block_b, width=8)
        self.read_block_b_spinbox.grid(row=4, column=2, padx=5, pady=5)

        tk.Checkbutton(self.main_frame, text='Show Progress', variable=self.show_progress).grid(row=5, column=1, columnspan=2)
        ttk.Button(self.main_frame, text='Run Monkey Test', command=self.run).grid(row=6, column=1, columnspan=2, padx=5, pady=5)

        #file,write_mb, write_block_kb, read_block_b

    def run(self):
        if self.write_mb.get() <= 0: self.write_mb.set(1)
        if self.write_block_kb.get() <= 0: self.write_mb.set(1)
        if self.read_block_b.get() <= 0: self.write_mb.set(1)
        if self.current_file.get() == '': self.current_file.set('/tmp/monkeytest')

        file = self.current_file.get()
        write_mb = self.write_mb.get()
        write_block_kb = self.write_block_kb.get()
        read_block_b = self.read_block_b.get()

        for widget in self.main_frame.winfo_children():
            widget.destroy()

        perc_comp_pb = ttk.Progressbar(self.main_frame, orient="horizontal", length=200, mode="determinate")
        perc_comp_pb["maximum"] = 100
        perc_comp_pb.grid(row=1, column=0, padx=5, pady=5)


        benchmark = Benchmark(file,write_mb, write_block_kb, read_block_b)
        run_lb = tk.Label(self.main_frame, text='Running...')
        run_lb.grid(row=0, column=0, padx=5, pady=5)
        if self.show_progress.get():
            benchmark.run(update_pb=perc_comp_pb, show_progress=False)
        if not self.show_progress.get():
            benchmark.run(show_progress=False)

        perc_comp_pb.destroy()
        run_lb.destroy()

        show_results = tk.Message(self.main_frame, text=benchmark.return_result(), justify='center')
        show_results.grid(columnspan=2, row=0, column=0)

        tk.Button(self.main_frame, text='Read Graph', command=lambda: self.plot('Read', benchmark)).grid(row=1, column=0)
        tk.Button(self.main_frame, text='Write Graph', command=lambda: self.plot('Write', benchmark)).grid(row=1, column=1)
        benchmark.print_result()

    def plot(self, rw, benchmark):
        if rw == 'Read':
            plt.plot(np.cumsum(benchmark.read_took), benchmark.rperc_took)
            plt.ylabel('Percent Complete (y)')
            plt.xlabel('Time taken (x)')
            plt.show()
        elif rw == 'Write':
            plt.plot(np.cumsum(benchmark.write_took), benchmark.wperc_took)
            plt.ylabel('Percent Complete (y)')
            plt.xlabel('Time taken (x)')
            plt.show()


def main():

    args = get_args()
    if args.mode.lower() == 'cli':
        if os.path.isfile(args.file):
            if input('Are you sure you wish to continue? Selected file will be deleted. (Y/N) ') == 'Y'.casefold():
                os.remove(args.file)
            else:
                print('Terminated')
                exit()
        if int(args.size) <= 0:
            print('{yellow}Total MB to write is smaller than or equal to 0, assuming default value of{end} {red}(128){end}'.format(
                yellow=col.Fore.YELLOW, end=col.Style.RESET_ALL, red=col.Fore.RED))
            args.size = 128
        if int(args.write_block_size) <= 0:
            print('{yellow}The block size for writing in bytes is smaller than or equal to 0, assuming default value of{end} {red}(1024){end}'.format(
                yellow=col.Fore.YELLOW, end=col.Style.RESET_ALL, red=col.Fore.RED))
            args.write_block_size = 1024
        if int(args.read_block_size) <= 0:
            print('{yellow}The block size for reading in bytes is smaller than or equal to 0, assuming default value of{end} {red}(512){end}'.format(
                yellow=col.Fore.YELLOW, end=col.Style.RESET_ALL, red=col.Fore.RED))
            args.read_block_size = 512

        benchmark = Benchmark(args.file, args.size, args.write_block_size, args.read_block_size)
        benchmark.run()
        if args.json is not None:
            benchmark.get_json_result(args.json)
        else:
            benchmark.print_result()
        os.remove(args.file)
    elif args.mode.lower() == 'gui':
        root = tk.Tk()
        benchmark_gui_var = benchmark_gui(root, args.file, args.size, args.write_block_size, args.read_block_size)
        root.mainloop()

if __name__ == "__main__":
    main()
