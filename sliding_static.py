import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, CheckButtons
from scipy.ndimage import zoom

# Initial parameters
params = {
    'num_bars': 16,
    'view_width': 384,
    'view_height': 384,
    'speed': 2,
    'pixel_size': 1.0,
    'blend': 0.0  # Blend factor (0 = animated, 1 = solid)
}

# Global variables
sliding_bars = []
stationary_gaps = []
use_red = True

# Generate static noise bars (binary)
def generate_static(num_bars, stripe_height, view_width, pixel_size):
    resolution = 1.0 / pixel_size
    sliding = []
    stationary = []
    for _ in range(num_bars):
        raw_slide = (np.random.rand(int(stripe_height * resolution), int(view_width * resolution)) > 0.5).astype(float)
        raw_gap = (np.random.rand(int(stripe_height * resolution), int(view_width * resolution)) > 0.5).astype(float)

        slide = zoom(raw_slide, (1 / resolution, 1 / resolution), order=0)
        gap = zoom(raw_gap, (1 / resolution, 1 / resolution), order=0)

        slide = slide[:stripe_height, :view_width]
        gap = gap[:stripe_height, :view_width]

        sliding.append(slide)
        stationary.append(gap)

    return sliding, stationary

# Create plot with two viewports

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), gridspec_kw={'wspace': 0.0001})
plt.subplots_adjust(bottom=0.45)
ax1.axis('off')
ax2.axis('off')

frame_image1 = np.zeros((params['view_height'], params['view_width'], 3))
frame_image2 = np.zeros_like(frame_image1)

im1 = ax1.imshow(frame_image1, animated=True)
im2 = ax2.imshow(frame_image2, animated=True)

# Animation update function
def update(frame):
    global sliding_bars, stationary_gaps, use_red

    num_bars = int(params['num_bars'])
    view_width = int(params['view_width'])
    view_height = int(params['view_height'])
    stripe_height = view_height // (2 * num_bars)
    blend = params['blend']

    if len(sliding_bars) != num_bars:
        sliding_bars, stationary_gaps = generate_static(
            num_bars, stripe_height, view_width, params['pixel_size']
        )

    image1 = np.zeros((view_height, view_width, 3))
    image2 = np.zeros_like(image1)

    for i in range(num_bars):
        y = i * 2 * stripe_height
        offset = (frame * params['speed']) % view_width

        bar = sliding_bars[i]
        looped_bar = np.hstack((bar[:, offset:], bar[:, :offset]))
        gap = stationary_gaps[i]

        bar_end = y + stripe_height
        gap_end = bar_end + stripe_height
        if gap_end > view_height:
            gap_end = view_height
            bar_end = gap_end - stripe_height

        # === Horizontal View (Original) ===
        animated_bar = np.stack([looped_bar]*3, axis=-1)[:bar_end - y, :, :]
        animated_gap = np.zeros((gap_end - bar_end, view_width, 3))
        if use_red:
            animated_gap[:, :, 0] = gap[:gap_end - bar_end, :]
        else:
            animated_gap[:, :, :] = np.stack([gap]*3, axis=-1)[:gap_end - bar_end, :, :]

        solid_bar = np.zeros_like(animated_bar)
        solid_gap = np.ones_like(animated_gap) if not use_red else np.zeros_like(animated_gap)
        if use_red:
            solid_gap[:, :, 0] = 1  # Red

        blended_bar = (1 - blend) * animated_bar + blend * solid_bar
        blended_gap = (1 - blend) * animated_gap + blend * solid_gap
        image1[y:bar_end, :, :] = blended_bar
        image1[bar_end:gap_end, :, :] = blended_gap

        # === Vertical View (New) ===
        x = i * 2 * stripe_height
        offset_v = (frame * params['speed']) % view_height
        bar_v = bar.T
        looped_bar_v = np.vstack((bar_v[offset_v:], bar_v[:offset_v]))
        gap_v = gap.T

        bar_end_v = x + stripe_height
        gap_end_v = bar_end_v + stripe_height
        if gap_end_v > view_width:
            gap_end_v = view_width
            bar_end_v = gap_end_v - stripe_height

        animated_bar_v = np.stack([looped_bar_v]*3, axis=-1)[:, :bar_end_v - x, :]
        animated_gap_v = np.zeros((view_height, gap_end_v - bar_end_v, 3))
        if use_red:
            animated_gap_v[:, :, 1] = gap_v[:, :gap_end_v - bar_end_v]  # Green
        else:
            animated_gap_v[:, :, :] = np.stack([gap_v]*3, axis=-1)[:, :gap_end_v - bar_end_v, :]

        solid_bar_v = np.zeros_like(animated_bar_v)
        solid_gap_v = np.ones_like(animated_gap_v) if not use_red else np.zeros_like(animated_gap_v)
        if use_red:
            solid_gap_v[:, :, 1] = 1  # Green

        blended_bar_v = (1 - blend) * animated_bar_v + blend * solid_bar_v
        blended_gap_v = (1 - blend) * animated_gap_v + blend * solid_gap_v
        image2[:, x:bar_end_v, :] = blended_bar_v
        image2[:, bar_end_v:gap_end_v, :] = blended_gap_v

    im1.set_array(image1)
    im2.set_array(image2)
    return [im1, im2]

# Animation object
ani = animation.FuncAnimation(fig, update, frames=300, interval=30, blit=True)

# === Slider setup ===
slider_defs = {
    'num_bars':      (0.15, 0.35, 1, 32, params['num_bars']),
    'view_width':    (0.15, 0.31, 40, 400, params['view_width']),
    'view_height':   (0.15, 0.27, 40, 400, params['view_height']),
    'speed':         (0.15, 0.23, 1, 10, params['speed']),
    'pixel_size':    (0.15, 0.19, 0.5, 10.0, params['pixel_size']),
    'blend':         (0.15, 0.15, 0.0, 1.0, params['blend']),
}

sliders = {}
for name, (x, y, vmin, vmax, val) in slider_defs.items():
    ax_slider = plt.axes([x, y, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    slider = Slider(ax_slider, name, vmin, vmax, valinit=val, valstep=0.01 if isinstance(val, float) else 1)
    sliders[name] = slider

# On slider change
def on_slider_change(val):
    for key, slider in sliders.items():
        params[key] = float(slider.val) if key == 'blend' or isinstance(slider.val, float) else int(slider.val)

    stripe_height = params['view_height'] // (2 * params['num_bars'])

    global sliding_bars, stationary_gaps
    sliding_bars, stationary_gaps = generate_static(
        params['num_bars'], stripe_height, params['view_width'], params['pixel_size']
    )

    new_image = np.zeros((params['view_height'], params['view_width'], 3))
    im1.set_data(new_image)
    im2.set_data(new_image.copy())
    fig.canvas.draw_idle()

for slider in sliders.values():
    slider.on_changed(on_slider_change)

# === Checkbox for red toggle ===
ax_check = plt.axes([0.83, 0.09, 0.1, 0.1], facecolor='lightgoldenrodyellow')
check = CheckButtons(ax_check, ['Red Gaps'], [use_red])

def toggle_red(label):
    global use_red
    use_red = not use_red
    fig.canvas.draw_idle()

check.on_clicked(toggle_red)

# Initial static generation
stripe_height = params['view_height'] // (2 * params['num_bars'])
sliding_bars, stationary_gaps = generate_static(
    params['num_bars'], stripe_height, params['view_width'], params['pixel_size']
)

plt.show()
