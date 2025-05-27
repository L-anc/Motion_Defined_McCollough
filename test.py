import numpy as np
import cv2

def generate_static_frame(height, width):
    return np.random.randint(0, 256, (height, width), dtype=np.uint8)

def colorize(gray_img, color='red'):
    if color == 'red':
        return cv2.merge([gray_img // 3, gray_img // 3, gray_img])
    elif color == 'green':
        return cv2.merge([gray_img // 3, gray_img, gray_img // 3])
    else:
        return cv2.merge([gray_img, gray_img, gray_img])

def create_motion_defined_static(height, width, region_coords, static_region):
    """
    Creates a full-field flickering static frame with a stationary region.
    """
    dynamic_noise = generate_static_frame(height, width)
    combined = dynamic_noise.copy()
    x1, y1, x2, y2 = region_coords
    combined[y1:y2, x1:x2] = static_region[y1:y2, x1:x2]
    return combined

# Parameters
height, width = 400, 400
region_coords = (120, 120, 280, 280)  # x1, y1, x2, y2
frames = 120
color = 'red'  # Use 'green' for second orientation later

# Generate a fixed static region (motionless)
static_region = generate_static_frame(height, width)

for i in range(frames):
    frame = create_motion_defined_static(height, width, region_coords, static_region)
    colorized_frame = colorize(frame, color)

    # Optional: overlay an orientation mask (e.g., vertical grating)
    if color == 'red':  # Vertical stripes for red
        for x in range(region_coords[0], region_coords[2], 10):
            colorized_frame[:, x:x+5] = colorized_frame[:, x:x+5] * 0.8
    else:  # Horizontal stripes for green
        for y in range(region_coords[1], region_coords[3], 10):
            colorized_frame[y:y+5, :] = colorized_frame[y:y+5, :] * 0.8

    cv2.imshow("Motion-Defined Boundary Induction", colorized_frame)
    if cv2.waitKey(30) == 27:  # ESC to exit
        break

cv2.destroyAllWindows()