## Project: Search and Sample Return


[image]: ./misc/rover_autonomous_screenshot.png


### Notebook Analysis

I decided to write a single thresholding function `color_thresh()` that accepts and tests both a lower and upper bound for each RGB channel. The functions `navigable_thresh()` and `sample_thresh()` each call `color_thresh()`, passing appropriate threshold values for navigable terrain and samples, respectively. The limited environmental color pallette can complicate color thesholding, but the selected values in `navigable_thresh()` and `sample_thresh()` work well enough to complete this project.

`process_image()` goes through a series of steps, numbered 1 - 7, which are described as follows:
1. Some basic constants about our camera are defined to facilitate transforming the incoming image from the viewpoint of the robot to a top down world view.

2. The incoming image is transformed to a top down view. A mask is similarly constructed for use in step 3.

3. A thresholding (both high and low) is applied to the incoming image to identify pixels considered navigable. A similar thresholding is applied to the combination of the previously defined mask and the invserse of
navigable to identify obstacles. Finally, a separate theshold to applied to image to identify rock samples.

4. Since the rover is defined in the world with a particular convention, the top down, thresholded pixels need to be translated and rotated to match.

5. We have knowledge about the rover's position and orientation in the world from its onboard telemetry, accessed via the databucket. The output pixels from step 4 can be translated, rotated, and scaled such that they
align with our world map.

6. Since the pixels are now aligned with the world, we can simply copy them to the world map, keeping each channel separate.

7. Finally, we build a series of images to pass information to the user.


### Autonomous Navigation and Mapping

To give some autonomy to the rover, two of the provided files (`perception.py` and `decision.py`) were updated to include and add on to what was generated in the Jupyter notebook. `perception.py` contains much of what is described above, with three key differences:

- A stability check was added, such that the Rover's worldmap is only updated by stable camera images. During some maneuvers, the Rover can develop excessive pitch and roll angles. Since our perspective transform doesn't account for these angles, we incorrectly map those image pixels. While some instability is acceptable, too much ruins our map fidelity. A threshold is imposed on both axies before updating the worldmap.

- The mask created in the notebook to ignore transformed pixels outside the camera's perspective was modified to also eliminate pixels that are far away, and this mask was applied to navigable terrain. Far away pixels were harder to determine, and by eliminating the sky, the navigable threshold could be slightly opened for a more accurate mapping.

- Since the Rover will now take actions in `decision.py`, some guidance is needed to make decisions Navigable terrain and, if in view, rock sample pixels are vectorized and stored in Rover.

Out of the box, `decision.py` came equipped to handle basic navigation. If navigable terrain data was available, it would move towards the most open terrain in view (the average of all navigable vectors). It could detect walls by thresholding the number of navigable pixels - when the number dropped too low, the Rover would initiate a stop and turn around sequence.

Since this procedure did a decent job of moving the Rover through the environment, much of the logic was left intact. However, since the Rover was only mapping stable images, the steering was dampened a bit, which dramatically reduced roll. This dampening was enforced by scaling the magnitude of the mean navigable vector by a factor proportional to speed. In other words, the faster the Rover drove, the wider it would steer, and vice versa. 

With basic motion in place, some logic was needed to find and pick up rock samples. First, a check was made to determine if any rock sample pixels were present in the frame. If present, the Rover would drive towards them, similar to how it addressed navigable terrain. It was quickly determined, however, that more often than not, the Rover's momentum would carry it past the sample. 

To compensate, two new states were added: `face_sample` and `approach_sample`. The `face_sample` state occurs immediately after the included `forward` state, and exists to quickly stop the Rover and turn it face the sample. This decoupling of halting forward trajectory and facing the sample avoided the earlier stated momentum problem. Once the Rover is stopped and facing the sample, a transition to the `approach_sample` state is made. In this state, the Rover slowly moves towards the sample, correcting direction as needed, and slowing to a stop just in front. Once there, the original included pickup code initiates pickup. Though simple and clunky, this approach works surprisingly well. The most common mode of failure was getting stuck along the wall during the approach.

Running the Rover in autonomous mode provides fairly good results. It typically maps over 80% of the world with > 80% fidelity in less than 1,000 seconds, and, more often than not, picks up every sample it sees, though it only occasionally picks up every sample on the map (see image below). There are of course many ways in which it could be improved. To start, simply following the average navigable terrain vectors is sloppy. Often in wider areas, it will drive around in circles, and its tendency to swerve back and forth causes unnecessary pitching and rolling, complicating the mapping process. Except for the rocks in the center, the Rover tends to avoid getting stuck when driving around. However, because rock sample always lie against walls, it often becomes stuck when the approach angle is close to the wall angle. Finally, the map the Rover builds of the world isn't used to help itself navigate or pickup samples.

Four significant upgrades are suggested. The first is to intelligently utilize the built map. Navigable terrain should be weighted by past exploration, or, in other words, the Rover should tend to move towards unexplored terrain. The Rover should also utilize the map to determine optimal sample approaches to avoid getting stuck along the walls. The second upgrade would include a stuck state, such that if the Rover should happen to get stuck, it can activate a plan to become unstuck. The third upgrade would be stabilize its motion, which could be done by choosing destination points and moving towards them in straight lines. The fourth and final upgrade, though more substantial than the others, would to introduce  a better method for identifying the different environmental components. Our simple color thresholding could be dramatically improved with even a basic convolutional neural network. 

![image]