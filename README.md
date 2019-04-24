# Fish Tracker

Fish tracker is a set of Python scripts used to automatically annotate the position and orientation of one fish in pre-saved videos.

# Requirements

Although we only tested `Fish Tracker` in Linux (Ubuntu) these scripts should work on any system that provides the following requirements:

- Python 2.7
- Numpy and Matplotlib (`http://www.numpy.org/`)
- Open CV 2.4.7 for Python (`http://opencv.org/`)

# Quick Start

To quickly test the scripts download the `Fish Tracker` project from the GitHub web site (`https://github.com/joseaccruz/fishtracker/archive/master.zip`) to any directory in you computer. The `sample` directory contains a one minute video for demo purposes only that we'll use in this example:

1. Go to the sample directories:

~~~
$ cd <your directory structure>/fishtracker
~~~

2. Run the `ftget.py`, `getproc.py` and `ftplot.py` scripts:

~~~
$ python ftget.py sample/sample.mp4 sample/myproject 350x185:265x230 200
$ python ftproc.py sample/myproject
$ python ftplot.py sample/myproject
~~~

After running these three scripts you should find the following files in the `sample` directory:

~~~
myproject                    - Project file
myproject.raw                - Raw XY positions tracked from the original video.
myproject.dat                - Scaled XY positions and angles computed from raw data.
myproject.plt_heat.svg       - XY Position heat map based on the observed data.
myproject.plt_polar.svg      - Fish orientation polar histogram based on the observed data.
~~~

# Usage

Fish tracker consists of four Python scripts that can be used separately to automatically annotate the position and orientation of one fish in a pre-saved high background contrast video. Here we describe in detail the usage of each of these scripts.

## ftget.py

The `ftget.py`script analyzes a video of a fish in a high contrast setting and extracts the X,Y positions of the fish's head, tail and centroid.

To run the script go to the `Fish Tracker` directory and type:

~~~
$ python ftget.py sample/sample.mp4 sample/myproject 350x185:265x230 200
~~~

The first argument (`sample.mp4`) must be the name (or the full path) of the video file to track. It doesn't need to be in the same directory to work. Something like this is perfectly acceptable:

~~~
$ python ftget.py -s /home/jsilva/videos/sample.mp4 sample/myproject 350x185:265x230 200
~~~

The second argument (`sample/myproject`) must be the name (or the full path) of the project file. This file will be created by the script and will be used in the later scripts to prevent typing the same parameters again-and-again.

__WARNING__: Be careful to choose a unique name for your project file. `ftget.py` will overwrite any file with the same name as the project file!

The last two arguments `350x185:265x230` and `200` define respectively the _coordinates of the region of interest (ROI)_ for the tracking and the _luminosity threshold_.

### Show Video option

The `-s` option tells the script to show the video on your screen while processing. This option can be really useful to get an idea of how well the tracking is working and to help setting up the best parameters for the tracking.

When you run the `ftget.py` script with the `-s` option you should be able to see two windows:

- The `Tracking Video` window;
- The `Tracking Binary`window.

The `Tracking Video` window shows the video as it is processed. In the top left corner of the video a red counter displays the frame being analyzed. The big red square at the center video identifies the tracking ROI. Everything outside the ROI is ignored by the tracking. In the top left corner of the ROI you can see the XY coordinates, the width and the height of the ROI and the luminosity threshold (LUMTH) as defined in the command line. You can adjust these values using the following keys:

- `UP arrow` move the ROI up;
- `DOWN arrow` move the ROI down;
- `LEFT arrow` move the ROI left;
- `RIGHT arrow` move the ROI right;
- `W` increases the ROI width;
- `SHIFT-W` decreases the ROI width;
- `H` increases the ROI height;
- `SHIFT-H` decreases the ROI height;

The `Tracking Binary` window show the binary image obtained by applying the LUMTH (`200` in our example) to the original image (i.e. every pixel of the image with a luminosity value higher than the LUMTH is set to white, the pixels of the image with a luminosity value lower than the LUMTH are set to black).  You can adjust these LUMTH values using the following keys:

- `L` increase the LUMTH;
- `SHIFT-L` decrease LUMTH;

__IMPORTANT__: As you change the LUMTH the size of white blobs in the `Tracking Binary` window also changes. The goal, for a perfect tracking, is to adjust all both the ROI and the LUMTH in order to get only the fish in the `Tracking Binary` window.

Note that when the fish is not detected a green cross is shown in the ROI. on the other hand you should always see the head, tail and centroid of the fish correctly marked on the image.

When you're happy with the result press `Q` and check the console. The script will print the final parameter values:

~~~
Final parameters: 350x182:264x240 200
~~~

__IMPORTANT__: The `-s` option dramatically slows down the performance of the script. After choosing the best ROI and LUMTH values if you need to process a long video just run the script without this option.

### Delay Option

If you want to check the video frame by frame you can set the `-d` option to add a delay of a few `ms` between each frame:

~~~
$ python ftget.py -d 500 -s sample/sample.mp4 sample/myproject 350x185:265x230 200
~~~

When using the delay option you can press any key to speed up the video again.

### Output

The `ftget.py` script generates two files:

- Project file (`sample/myproject` in our example).
- Raw data file (`sample/myproject.raw` in our example).

Both files are saved in the same directory (`sample` in our example).

The raw data file is a tab separated file containing one line per frame as in this example:

~~~
0   1   498 306 471 290 436 269
1   1   504 308 477 294 441 273
2   1   512 302 482 296 448 275
3   1   519 300 489 299 454 289
4   1   526 302 496 300 457 294
5   1   526 302 496 300 457 294
6   1   533 304 502 301 462 297
7   1   539 306 510 302 469 299
8   1   545 306 515 302 474 299
9   1   550 306 520 303 481 299
~~~

Each line contains 8 columns:

~~~
7   1   539 306 510 302 469 299
|   |   \-----/ \-----/ \-----/
|   |      |       |       |
|   |      |       |       +-----> tail XY coordinates
|   |      |       +-------------> centroid XY coordinates
|   |      +---------------------> head XY coordinates
|   +----------------------------> 1 if the fish was detected, 0 otherwise
+--------------------------------> frame number
~~~

All XY coordinates are measured in the reference of the video starting from the top left corner of the image.

## ftproc.py

The `ftproc.py` script performs the following of post-processing steps upon the raw data:
- Scale the XY coordinates.
- Shifts the coordinates to the top left corner of the ROI. This way, we can adjust the ROI to some physical reference point.
- Swaps the Y coordinates so the left bottom corner of the ROI will be point (0, 0).
- Shifts the coordinates for some amount of pixels.
- Computes the orientation angle of the fish.

__IMPORTANT__: Before running `ftproc.py` you need to create a project by running `ftget.py`.

To run the `ftproc.py` script go to the `Fish Tracker` directory and type:

~~~
$ python ftproc.py sample/myproject
~~~

The only mandatory parameter is the name (or the full path) of the project file.

### Scale and Shift options

The `ftproc.py` script accepts the following options:

- `-x`: X scale factor. The new X coordinates will be the product of this scale factor and the corresponding raw X coordinate.
- `-y`: Y scale factor. The new Y coordinates will be the product of this scale factor and the corresponding raw Y coordinate.
- `-H`: Horizontal shift factor. This value will be added to all X coordinates after scaling.
- `-V`: X scale factor. This value will be added to all Y coordinates after scaling.

### Output

The `ftproc.py` script generates one data file (`sample/myproject.dat` in our example), saved in the same directory as the previous files.

The data file is a tab separated file containing on line per frame as in this example:

~~~
0   1   148.00  116.00  121.00  132.00  86.00   153.00  -149.35
1   1   154.00  114.00  127.00  128.00  91.00   149.00  -152.59
2   1   162.00  120.00  132.00  126.00  98.00   147.00  -168.69
3   1   169.00  122.00  139.00  123.00  104.00  133.00  -178.09
4   1   176.00  120.00  146.00  122.00  107.00  128.00  -176.19
5   1   176.00  120.00  146.00  122.00  107.00  128.00  -176.19
6   1   183.00  118.00  152.00  121.00  112.00  125.00  -174.47
7   1   189.00  116.00  160.00  120.00  119.00  123.00  -172.15
8   1   195.00  116.00  165.00  120.00  124.00  123.00  -172.41
9   1   200.00  116.00  170.00  119.00  131.00  123.00  -174.29
10  1   205.00  116.00  176.00  119.00  137.00  122.00  -174.09
~~~

Each line contains 9 columns:

~~~
7 1 189.00  116.00 160.00  120.00  119.00  123.00 -172.15
| | \------------/ \------------/  \------------/    |
| |       |              |               |           +---> Orientation angle
| |       |              |               +---------------> tail XY coordinates
| |       |              +-------------------------------> centroid XY coords.
| |       +----------------------------------------------> head XY coordinates
| +------------------------------------------------------> 1 if detected
+--------------------------------------------------------> frame number
~~~

All XY coordinates are measured in the ROI reference frame starting from the bottom left corner of the ROI.

The angle is measured from `-180.0` to `180.0`. The `0` (zero) angle corresponds to the orientation of the fish heading left and increases as the fish rotates clockwise until reaching `180.0` == `-180.0` which corresponds to the orientation of the fish heading right.

## ftplot.py

The `ftplot.py` script generates some data visualization of the observed data.

__IMPORTANT__: Before running `ftplot.py` you need to run both `ftget.py` and `ftproc.py`.

To run the `ftplot.py` script go to the `Fish Tracker` directory and type:

~~~
$ python ftplot.py sample/myproject
~~~

The only mandatory parameter is the name (or the full path) of the project file.

### Show Images options

To display the images generated on the fly just add the `-s` option to the command line:

~~~
$ python ftplot.py -s sample/myproject
~~~

### Output

The `fplot.py` script generates to `SVG` files:

- `myproject.plt_heat.svg`  - XY Position heat map based on the observed data.
- `myproject.plt_polar.svg` - Fish orientation polar histogram based on the observed data.

The `SVG` format is a convenient vector based format which allow the file to be imported in all major vector editing image programs.


## ftview.py

Finally, the `ftview.py` script is a data visualizer that projects the data into the video for quality control and fun.

__IMPORTANT__: Before running `ftview.py` you need to run both `ftget.py` and `ftproc.py`.

To run the `ftview.py` script go to the `Fish Tracker` directory and type:

~~~
$ python ftview.py sample/myproject
~~~

The only mandatory parameter is the name (or the full path) of the project file.

### Display options

The `ftview.py` script accepts the following options:

- `-d`: Works as the _delay option_ of the `ftget.py` script.
- `-j`: Jumps to the specified frame.

For example if you want to check the data on the `myproject` project starting from frame 500 with a delay of 250 ms between frames just type:

~~~
$ python ftview.py -d 250 -j 500 sample/myproject 

~~~

## Image Enhance 
  This is a collection of matlab codes.Based on the fusion principles, the strategy derives the inputs and the weight measures only from the degraded version of an image. In order to better the results of fish recognition algorithms under medium to mediocre quality due to underwater limitations.
  
  
 FOR NOW ONLY COLOR BALANCE + WHITE BALANCE  CODES ARE AVAILABLE (can be useful on there own) UNDERDEVELOPMENT A CODE FOLLOWING THIS COURSE http://edu.epfl.ch/coursebook/en/image-and-video-processing-EE-550  
  
