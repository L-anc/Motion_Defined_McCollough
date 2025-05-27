import numpy as np
import cv2

def generate_static_noise(height, width):
    """Generates a grayscale static noise frame."""
    return np.random.randint(0, 256, (height, width), dtype=np.uint8)

def colorize_noise(gray_img, color):
    """Apply a color tint to a grayscale image."""
    if color == 'red':
        return cv2.merge([gray_img // 3, gray_img // 3, gray_img])  # Red tint
    elif color == 'green':
        return cv2.merge([gray_img // 3, gray_img, gray_img // 3])  # Green tint
    else:
        return cv2.merge([gray_img, gray_img, gray_img])  # Gray

# Configuration
width, height = 400, 400
frames = 60
color = 'red'



while True:
    for i in range(frames):
        # Shift noise to simulate motion
        static = generate_static_noise(height, width)

        # Colorize based on orientation
        colorized = colorize_noise(static, color=color)

        # Show the frame
        cv2.imshow("Motion-defined McCollough Induction", colorized)

    # if color == 'red':
    #     color = 'green'
    # else:
    #     color = 'red'

    if cv2.waitKey(50) == 27:  # ESC to break
            break
    

cv2.destroyAllWindows()
