import numpy as np
import cv2


# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def color_thresh(img, rgb_thresh_low=(150, 150, 150), rgb_thresh_high=(255, 255, 255)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:, :, 0])
    # Require that each pixel be within all three threshold values in RGB
    # defined by rgb_thresh_low and rgb_thresh_high
    # within_thresh will now contain a boolean array with "True"
    # where threshold was met
    within_thresh = (img[:, :, 0] >= rgb_thresh_low[0]) & (img[:, :, 0] <= rgb_thresh_high[0]) \
                    & (img[:, :, 1] >= rgb_thresh_low[1]) & (img[:, :, 1] <= rgb_thresh_high[1]) \
                    & (img[:, :, 2] >= rgb_thresh_low[2]) & (img[:, :, 2] <= rgb_thresh_high[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[within_thresh] = 1
    # Return the binary image
    return color_select


# Define a function to return thresholded navigable pixels
def navigable_thresh(img):
    # Call color_thresh using ground color thresholds
    return color_thresh(img, rgb_thresh_low=(130, 140, 150), rgb_thresh_high=(255, 255, 255))


# Define a function to return thresholded navigable pixels
def samples_thresh(img):
    # Call color_thresh using rock sample color thresholds
    return color_thresh(img, (120, 120, 0), (255, 255, 70))


# Define a function to convert from image coords to rover coords
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1] / 2).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel ** 2 + y_pixel ** 2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles


# Define a function to map rover space pixels to world space
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))

    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated


def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale):
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated


# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world


# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))  # keep same size as input image

    return warped


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # NOTE: camera image is coming to you in Rover.img

    # 1) Define source and destination points for perspective transform
    dst_size = 5
    bottom_offset = 6
    source = np.float32([[14, 140], [301, 140], [200, 96], [118, 96]])
    destination = np.float32([[Rover.img.shape[1] / 2 - dst_size, Rover.img.shape[0] - bottom_offset],
                              [Rover.img.shape[1] / 2 + dst_size, Rover.img.shape[0] - bottom_offset],
                              [Rover.img.shape[1] / 2 + dst_size, Rover.img.shape[0] - 2 * dst_size - bottom_offset],
                              [Rover.img.shape[1] / 2 - dst_size, Rover.img.shape[0] - 2 * dst_size - bottom_offset],
                              ])

    # 2) Apply perspective transform
    pre_mask = np.zeros_like(Rover.img[:, :, 0])
    pre_mask[82:, :] = 1
    mask = perspect_transform(pre_mask, source, destination)
    warped = perspect_transform(Rover.img, source, destination)

    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    pre_navigable = navigable_thresh(warped)
    navigable = pre_navigable * mask
    not_navigable = (navigable == 0)
    obstacles = not_navigable * mask
    samples = samples_thresh(warped)

    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
    Rover.vision_image[:, :, 0] = obstacles * 255
    Rover.vision_image[:, :, 1] = samples * 255
    Rover.vision_image[:, :, 2] = navigable * 255

    # 5) Convert map image pixel values to rover-centric coords
    navigable_x, navigable_y = rover_coords(navigable)
    obstacle_x, obstacle_y = rover_coords(obstacles)
    samples_x, samples_y = rover_coords(samples)

    # 6) Convert rover-centric pixel values to world coordinates
    xpos = Rover.pos[0]
    ypos = Rover.pos[1]
    yaw = Rover.yaw
    worldsize = Rover.worldmap.shape[0]
    scale = dst_size * 2
    navigable_x_world, navigable_y_world = pix_to_world(navigable_x, navigable_y, xpos, ypos, yaw, worldsize, scale)
    obstacle_x_world, obstacle_y_world = pix_to_world(obstacle_x, obstacle_y, xpos, ypos, yaw, worldsize, scale)
    samples_x_world, samples_y_world = pix_to_world(samples_x, samples_y, xpos, ypos, yaw, worldsize, scale)

    # 7) Check for instability (significant pitch and roll)
    stable = True
    if Rover.pitch > 0.25 or 360.0 - Rover.pitch < 0.25 \
       or Rover.roll > 0.5 or 360.0 - Rover.roll < 0.5:
        stable = False

    # 8) Update Rover worldmap if the Rover's camera is stable
    if stable:
        # Add navigable terrain to blue channel
        Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 10
        # Add obstacles to red channel
        Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        # Add samples to green channel
        Rover.worldmap[samples_y_world, samples_x_world, 1] += 1

    # 9) Convert rover-centric pixel positions to polar coordinates
    Rover.nav_dists, Rover.nav_angles = to_polar_coords(navigable_x, navigable_y)
    if samples_x.any():
        sample_dist, sample_angles = to_polar_coords(samples_x, samples_y)
        Rover.sample_dist, Rover.sample_angle = np.min(sample_dist), np.mean(sample_angles)
    else:
        Rover.sample_dist, Rover.sample_angle = None, None

    return Rover
