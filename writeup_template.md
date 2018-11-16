## Project: Search and Sample Return


[image1]: ./test_dataset/IMG/robocam_2018_10_29_14_14_55_338.jpg
[image2]: ./test_dataset/IMG/robocam_2018_10_29_14_14_19_071.jpg


### Notebook Analysis

![image1] ![image2]

I decided to write a single thresholding function `color_thresh()` that accepts and tests both a lower and upper bound for each RGB channel. The functions `navigable_thresh()` and `sample_thresh()` each call `color_thresh()`,
passing appropriate threshold values for navigable terrain and samples, respectively. The limited environmental color pallette can complicate color thesholding, but the selected values in `navigable_thresh()` and
`sample_thresh()` work well enough to complete this project.

`process_image()` goes through a series of steps, numbered 1 - 7, which are described as follows:
1. Some basic constants about our camera are defined to facilite transforming the incoming image from the viewpoint of the robot to a top down world view.

2. The incoming image is transformed to a top down view. A mask is similarly constructed for use in step 3.

3. A thresholding (both high and low) is applied to the incoming image to identify pixels considered navigable. A similar thresholding is applied to the combination of the previously defined mask and the invserse of
navicable to identify obstacles. Finally, a separate theshold to applied to image to identify rock samples.

4. Since the rover is defined in the world with a particular convention, the top down, thresholded pixels need to be translated and rotated to match.

5. We have knowledge about the rover's position and orientation in the world from its onboard telemetry, accessed via the databucket. The output pixels from step 4 can be translated, rotated, and scaled such that they
allign with our world map.

6. Since the pixels are now alligned with the world, we can simply copy them to the world map, keeping each channel separate.

7. Finally, we build a series of images to pass information to the user.


### Autonomous Navigation and Mapping

To give some autonomy to the rover, two of the provided files (`perception.py` and `decision.py`) were updated to include and add on to what was generated in the Jupyter notebook. `perception.py` contains much of
what is described above, with two key differences:

- A stability check was added, such that the Rover's worldmap is only updated by stable camera images. During some maneuvers, the Rover can develop excessive pitch and roll angles. Since our perspective transform
doesn't account for these angles, we incorrectly transform our image pixels. While some instability is acceptable, too much ruins our map fidelity. A threshold is imposed on both axies before updating the worldmap.


- Since the Rover will now take actions in `decision.py`, some guidance is needed to make decisions. Navigable terrain and, if in view, rock sample pixels are vectorized and stored in Rover.

Out of the box, `decision.py` came equipped to handle basic navigation. If navigable terrain data was available, it would move towards the most open terrain in view (the average of all navigable vectors). It could detect
walls by thresholding the number of navigable pixels - when the number dropped too low, the Rover would initiate a stop sequence, and once stopped, turn until the numbner of navigable pixels rose above the threshold.

Since this procedure did a decent job of moving the Rover through the environment, much of the logic was left in tact. However, more logic was needed if rock samples were to be found and picked up. First, a check was made to
determine if any rock sample pixels were present in the frame. At first, if present, the Rover would drive towards them, similar to how it addressed navigable terrain. It was quickly determined, however, that more often
than not, the Rover's momentum would overcome its intention to face the sample, which would exit the frame and become lost.

To compensate, two new states were added: `face_sample` and `approach_sample`. The `face_sample` state occurs immediately after the included `forward` state, and exists to stop the Rover and turn it face the sample.
This decoupling of halting forward trajectory and facing the sample avoided the earlier stated momentum problem. Once the Rover is stopped and facing the sample, a transition to the `approach_sample` state. In this state,
the Rover slowly moves towards the sample, correcting direction as needed, and slowing to a stop just in front. Once there, the original included pickup code initiates pickup.

Though simple and clunky, this approach works surprisingly well. The most common modes of failure were getting stuck along the wall during the approach, and losing sight of the sample both while facing and approaching
the samples. To overcome, in each state, the sample's visibility is checked. If the vector list is empty but the state hasn't timed out, the Rover is lighly perturbed. Once the timeout has been reached, though, the
Rover's state is returned to `forward`.

Running the Rover in autonomous mode provides fairly good results. It usually maps over 70% of the world with > 70% fidelity, and, more often than not, picks up every sample it sees, though it only occasionally
picks up every sample on the map. There are of course many ways in
which it could be improved. To start, simply following the average navigable terrian vectors is sloppy. Often in wider areas, it will drive around in circles, and its tendency to swerve back and forth
causes unneccessary pitching and rolling, complicating the mapping process. Except for the rocks in the center, the Rover tends to
avoid getting stuck when driving around. However, because rock sample always lie against walls, it often becomes stuck when the approach angle is close to the wall angle. Finally, the map the Rover builds of the world
isn't used to help itself navigate or pickup samples.

Three significant upgrades are suggested. The first is to intelligently utilize the built map. Navigable terrain should be weighted by past exploration, or, in other words, the Rover should tend to move towards
unexplored terrain. The Rover should also utilize the map to determine optimal sample approaches to avoid getting stuck along the walls. The second upgrade would include a stuck state, such that if the Rover should
happen to get stuck, it can activate a plan to become unstuck. The third and final upgrade would be stabilize its motion, which could be done by choosing destination points and moving towards them.