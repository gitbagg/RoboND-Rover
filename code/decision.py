import numpy as np
import time


# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function
def decision_step(Rover):
    # Check if we have vision data to make decisions with
    # First check if we're close to an already found sample
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
        if Rover.mode == 'forward':
            if Rover.sample_angle is not None:
                # Switch to approach_sample mode
                Rover.mode = 'face_sample'
            # Check the extent of navigable terrain
            elif len(Rover.nav_angles) >= Rover.stop_forward:
                # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle 
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                # Set steering to average angle clipped to the range +/- 15
                Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                    # Set mode to "stop" and hit the brakes!
                    Rover.throttle = 0
                    # Set brake to stored brake value
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = -15 # Could be more clever here about which way to turn
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.mode = 'forward'

        elif Rover.mode == 'face_sample':
            # Hit the brakes if we're still moving
            if Rover.vel > 0.2:
                Rover.brake = Rover.brake_set
            # Else, turn to face the sample
            else:
                Rover.brake = 0
                if Rover.sample_angle is not None:
                    # While we're not facing the sample directly, turn towards it
                    if np.abs(Rover.sample_angle * 180 / np.pi) > 10:
                        Rover.steer = np.clip(Rover.sample_angle * 180 / np.pi, -15, 15)
                    # Else we're facing it and should start the approach and restart the timer
                    else:
                        Rover.mode = 'approach_sample'
                        Rover.sample_timer = time.time()

        elif Rover.mode == 'approach_sample':
            # Make sure we can still see the sample
            if Rover.sample_dist is None:
                # Check if we've timed out
                if time.time() - Rover.sample_timer > Rover.sample_timeout:
                    Rover.mode = 'forward'
                # Otherwise perturb the rover to find the sample
                else:
                    Rover.throttle = 0.05
                    Rover.steer /= 2
            else:
                # Keep steering towards the sample as we move forward
                Rover.steer = np.clip(Rover.sample_angle * 180 / np.pi, -15, 15)
                # If the sample is too far away, move towards it, otherwise initiate stopping
                if Rover.sample_dist > 10:
                    if time.time() - Rover.sample_timer > Rover.sample_timeout:
                        Rover.steer += np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15) * 0.5
                        Rover.sample_timer = time.time()
                    if Rover.vel > 0.2:
                        Rover.throttle = 0
                    else:
                        Rover.throttle = 0.1
                    Rover.brake = 0
                else:
                    Rover.throttle = 0
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
        else:
            print('bad mode')
    # If in a state where want to pickup a rock send pickup command
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        Rover.send_pickup = True
    
    return Rover

