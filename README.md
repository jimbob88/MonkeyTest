# MonkeyTest

MonkeyTest -- a disk benchmark to test your hard drive read-write speed in Python

A simplistic script to show that such system programming
tasks are possible and convenient to be solved in Python

~~I haven't done any command-line arguments parsing, so
you should configure it using the constants at top of the script.~~

The file is being created, then written with random data, randomly read
and deleted, so the script doesn't waste your drive

(!) Be sure, that the file you point to is not somthing
    you need, cause it'll be overwritten during test

Has been tested on 3.6.7 under Bionic, seems to fully support Python 2.7 (As of 03/03/19)


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
If you wish to use TUI on both Python2 and Python3 install picotui with:
```
pip install git+https://github.com/jimbob88/picotui-python2_3.git
```


If You want to contribute, be sure to see our TODO list first
  https://github.com/jimbob88/MonkeyTest/milestones

![monkeytest](https://cloud.githubusercontent.com/assets/16870636/12601547/7a3a4f14-c4aa-11e5-8b2e-48a20d7f7c17.png)

![monkeytest GUI](https://user-images.githubusercontent.com/9913366/53694502-b3fc4d00-3da7-11e9-8ea9-7bb7fbd17d9b.png)
![monkeytest Graph](https://user-images.githubusercontent.com/9913366/53694527-050c4100-3da8-11e9-89c6-a53aa6dfc859.png)

![monkeytest TUI](https://user-images.githubusercontent.com/9913366/53694508-c8d8e080-3da7-11e9-8018-e5bab1cb8137.png)
