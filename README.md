# MonkeyTest

MonkeyTest -- a disk benchmark to test your hard drive read-write speed in Python

A simplistic script to show that such system programming
tasks are possible and convenient to be solved in Python

~~I haven't done any command-line arguments parsing, so
you should configure it using the constants at top of the script.~~

The file is being created, then written with random data, randomly read
and deleted, so the script doesn't waste your drive

(!) Be sure, that the file you point to is not smthng
    you need, cause it'll be overwritten during test

Has been tested on 3.6.7 under Bionic
May support python2 but this hasn't been extensively tested

Installation:
```
sudo apt install python3-dev python3-tk
sudo -H pip3 install matplotlib
sudo -H pip3 install numpy
sudo -H pip3 install colorama
```
Usage for gui:
```
python3 monkeytest.py --mode gui
```

If You want to contribute, be sure to see our TODO list first
  https://github.com/jimbob88/MonkeyTest/milestones

![monkeytest](https://cloud.githubusercontent.com/assets/16870636/12601547/7a3a4f14-c4aa-11e5-8b2e-48a20d7f7c17.png)
