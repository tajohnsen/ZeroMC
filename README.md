# ZeroMC
0MQ PUB/SUB system for displaying fullscreen images to subscribers.

This is a proof of concept and is far from complete.
The system was tested on Windows using Python 3.6.

## Dependencies
* pyzmq
* pygame

## Modules

### Subscriber
Subscribers are meant to run the Display module and will receive JPG images from the Publisher.
Images will display fullscreen and cycle every 20 seconds.
Since this is a PUB/SUB system the subscriber ensures that the file received doesn't already exist.

### Publisher
Publishers will run in the background and scan a specified directory for JPEG files.
Files will be published every 15 seconds though in production this should be much longer.
Future development should add a command to allow the publisher to instruct subscribers to erase all old images.

## How to try it
Download the repository and install it using

```
Linux:
python setup.py sdist
pip3 install --user dist/ZeroMC-0.1.tar.gz
```

```
Windows:
python.exe setup.py sdist
pip install dist/ZeroMC-0.1.tar.gz
```

First run the publisher:

```
Linux:
python3 -m zeromc.publisher
```

```
Windows:
python.exe -m zeromc.publisher
```

Next run the display (subscriber):

```
Linux:
python3 -m zeromc.display
```

```
Windows:
python.exe -m zeromc.display
```

It may take about 30 seconds but your screen will be overtaken by a test image which is giant letters: JPG.
* To change from fullscreen to a windowed display, press n.
* To change back to fullscreen, press f.
* To exit the display press ESCAPE.

You can add more JPG images to the `tests` directory to send to the display.
You do not need to restart either component to do so.

## Uninstall
To uninstall type:
```
Linux:
pip3 uninstall zeromc
```

```
Windows:
pip uninstall zeromc
```
