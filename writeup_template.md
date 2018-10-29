## Project: Search and Sample Return


[image1]: ./test_dataset/IMG/robocam_2018_10_29_14_14_55_338.jpg
[image2]: ./test_dataset/IMG/robocam_2018_10_29_14_14_19_071.jpg


### Notebook Analysis
#### Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.
Rnning both the provided test images and a recording I made, it became apparent that each environmental feature
(navigable terrain, obstacles, sky, and samples) remained consistent in color, such that a basic color thresholding
system could be used to identify each. Several images (such as those shown below) were tested to determine a specific color range for each feature.

![image1] ![image2]

I decided to write a single thresholding function `color_thresh()` that accepts and tests both a lower and upper bound for each RGB channel. The functions `navigable_thresh()` and `sample_thresh()` call `color_thresh()`,
passing appropriate threshold values for navigable terrain and samples, respectively. The limited environmental ccolor pallette can comlicate color thesholding, the selected values in `navigable_thresh()` and
`sample_thresh()` work well enough to complete this project.

#### Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result.
`process_image()` goes theoug a series of steps, numbered 1 -


### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.


#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**

Here I'll talk about the approach I took, what techniques I used, what worked and why, where the pipeline might fail and how I might improve it if I were going to pursue this project further.  



![alt text][image3]



##Notebook Analysis
###Test