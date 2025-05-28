import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, CheckButtons
from scipy.ndimage import zoom

# === PARAMETERS & STATE ===
params = {
    'num_bars':       16,
    'view_width':     384,
    'view_height':    384,
    'speed':          2,
    'pixel_size':     1.0,
    'blend':          0.0,    # 0 = animated, 1 = solid
    'color_strength': 0.0     # 0 = grayscale, 1 = full color
}
motion_enabled     = True
regen_enabled      = False
color_whites_enabled = False
active_slider      = None

# === STATIC NOISE GENERATOR ===
def generate_static(num, stripe_h, w, px):
    res = 1/px
    slides, gaps = [], []
    for _ in range(num):
        r1 = (np.random.rand(int(stripe_h*res), int(w*res)) > 0.5).astype(float)
        r2 = (np.random.rand(int(stripe_h*res), int(w*res)) > 0.5).astype(float)
        s = zoom(r1, (1/res,1/res), order=0)
        g = zoom(r2, (1/res,1/res), order=0)
        s = np.pad(s, [(0, stripe_h-s.shape[0]), (0, w-s.shape[1])], 'constant')[:stripe_h, :w]
        g = np.pad(g, [(0, stripe_h-g.shape[0]), (0, w-g.shape[1])], 'constant')[:stripe_h, :w]
        slides.append(s); gaps.append(g)
    return slides, gaps

sliding_bars, stationary_gaps = [], []

# === FIGURE & COMPOSITE AXES SETUP ===
fig = plt.figure(figsize=(8,8))
ax_img = fig.add_axes([0.0, 0.15, 1.0, 0.85])
ax_img.axis('off')
fig.patch.set_facecolor('black')

vh, vw = params['view_height'], params['view_width']
composite_blank = np.zeros((2*vh, 2*vw, 3))
im = ax_img.imshow(composite_blank, animated=True)

# === UPDATE FUNCTION ===
def update(frame):
    global sliding_bars, stationary_gaps

    nb = int(params['num_bars'])
    vw, vh = int(params['view_width']), int(params['view_height'])
    ph = vh // (2*nb)
    blend = params['blend']
    cstr  = params['color_strength']
    sp    = params['speed']

    # regen logic: if bar-count changed, regen both; elif regen enabled, regen sliding only
    if len(sliding_bars) != nb:
        sliding_bars, stationary_gaps = generate_static(nb, ph, vw, params['pixel_size'])
    elif regen_enabled:
        new_slides, _ = generate_static(nb, ph, vw, params['pixel_size'])
        sliding_bars = new_slides

    # prepare outputs and white‐pixel masks
    out_h = np.zeros((vh, vw, 3))
    out_v = np.zeros((vh, vw, 3))
    mask_h = np.zeros((vh, vw), dtype=bool)
    mask_v = np.zeros((vh, vw), dtype=bool)

    for i in range(nb):
        y0, x0 = i*2*ph, i*2*ph
        bar = sliding_bars[i]
        gap = stationary_gaps[i]

        # scroll or freeze
        if motion_enabled:
            off_h = (frame * sp) % vw
            off_v = (frame * sp) % vh
        else:
            off_h = off_v = 0

        # horizontal noise
        loop_h = np.hstack((bar[:, off_h:], bar[:, :off_h]))
        # vertical noise
        bv, gv = bar.T, gap.T
        loop_v = np.vstack((bv[off_v:], bv[:off_v]))

        # record white‐pixel mask
        mask_h[y0:y0+ph,   :] = loop_h > 0.5
        mask_h[y0+ph:y0+2*ph, :] = gap > 0.5
        mask_v[:, x0:x0+ph]     = loop_v > 0.5
        mask_v[:, x0+ph:x0+2*ph] = gv > 0.5

        # --- build horizontal panel ---
        bg = np.stack([loop_h]*3, axis=-1)
        gg = np.stack([gap]*3,   axis=-1)
        cg = np.zeros_like(gg); cg[:,:,0] = gap
        sbg = np.zeros_like(bg); sgg = np.ones_like(gg)
        scg = np.zeros_like(gg); scg[:,:,0] = 1

        mbg = (1-blend)*bg + blend*sbg
        mgg = (1-blend)*gg + blend*sgg
        mcg = (1-blend)*cg + blend*scg

        stripe_gray_h = np.vstack((mbg, mgg))
        stripe_col_h  = np.vstack((mbg, mcg))
        out_h[y0:y0+2*ph, :] += (1-cstr)*stripe_gray_h + cstr*stripe_col_h

        # --- build vertical panel ---
        bgv = np.stack([loop_v]*3, axis=-1)
        ggv = np.stack([gv]*3,   axis=-1)
        cgv = np.zeros_like(ggv); cgv[:,:,1] = gv
        sbgv = np.zeros_like(bgv); sggv = np.ones_like(ggv)
        scgv = np.zeros_like(ggv); scgv[:,:,1] = 1

        mbgv = (1-blend)*bgv + blend*sbgv
        mggv = (1-blend)*ggv + blend*sggv
        mcgv = (1-blend)*cgv + blend*scgv

        stripe_gray_v = np.hstack((mbgv, mggv))
        stripe_col_v  = np.hstack((mbgv, mcgv))
        out_v[:, x0:x0+2*ph] += (1-cstr)*stripe_gray_v + cstr*stripe_col_v

    # if color_whites enabled, override white pixels
    if color_whites_enabled:
        out_h[mask_h] = (1.0, 0.0, 0.0)  # red
        out_v[mask_v] = (0.0, 1.0, 0.0)  # green

    # assemble 2×2 composite
    comp = np.zeros((2*vh, 2*vw, 3))
    comp[0:vh,    0:vw   ] = out_h  # TL
    comp[0:vh,    vw:2*vw] = out_v  # TR
    comp[vh:2*vh, 0:vw   ] = out_v  # BL
    comp[vh:2*vh, vw:2*vw] = out_h  # BR

    im.set_array(comp)
    return (im,)

ani = animation.FuncAnimation(fig, update, frames=300, interval=30, blit=True)

# === SLIDER CALLBACK & ARROW-KEY CONTROL ===
def on_slider_change(slider, val):
    global active_slider
    active_slider = slider
    key = slider.name
    if key in ('blend','color_strength','pixel_size'):
        params[key] = float(val)
    else:
        params[key] = int(val)
    # regenerate on geometry change
    ph = params['view_height'] // (2*params['num_bars'])
    global sliding_bars, stationary_gaps
    sliding_bars, stationary_gaps = generate_static(
        params['num_bars'], ph, params['view_width'], params['pixel_size']
    )
    # clear composite
    vh, vw = params['view_height'], params['view_width']
    im.set_data(np.zeros((2*vh, 2*vw, 3)))
    fig.canvas.draw_idle()

def on_key(event):
    global active_slider
    if active_slider is None: return
    step = active_slider.valstep
    if event.key=='left':
        new = active_slider.val - step
    elif event.key=='right':
        new = active_slider.val + step
    else:
        return
    new = max(active_slider.valmin, min(active_slider.valmax, new))
    active_slider.set_val(new)

fig.canvas.mpl_connect('key_press_event', on_key)

# === TOGGLES: Motion, Random Static, Color Whites ===
ax_check = fig.add_axes([0.01, 0.12, 0.20, 0.08], facecolor='lightgoldenrodyellow')
check = CheckButtons(
    ax_check,
    ['Motion', 'Random Static (Sliding if off)', 'Color Whites'],
    [motion_enabled, regen_enabled, color_whites_enabled]
)
def on_toggle(label):
    global motion_enabled, regen_enabled, color_whites_enabled
    if label == 'Motion':
        motion_enabled = not motion_enabled
    elif label.startswith('Random Static'):
        regen_enabled = not regen_enabled
    else:  # Color Whites
        color_whites_enabled = not color_whites_enabled
check.on_clicked(on_toggle)

# === SLIDER SETUP (0.005 steps for floats) ===
slider_defs = {
    'num_bars':       (0.10, 0.08, 1,   32,   params['num_bars'],       1),
    'view_width':     (0.10, 0.06, 40, 400,   params['view_width'],     1),
    'view_height':    (0.10, 0.04, 40, 400,   params['view_height'],    1),
    'speed':          (0.60, 0.08, 1,   10,   params['speed'],          1),
    'pixel_size':     (0.60, 0.06, 0.5, 10.0, params['pixel_size'],     0.005),
    'blend':          (0.60, 0.04, 0.0, 1.0,  params['blend'],          0.005),
    'color_strength': (0.60, 0.02, 0.0, 1.0,  params['color_strength'], 0.005),
}

sliders = {}
for name,(x,y,vmin,vmax,val,step) in slider_defs.items():
    ax = fig.add_axes([x, y, 0.35, 0.02], facecolor='dimgray')
    s = Slider(ax, name, vmin, vmax, valinit=val, valstep=step)
    s.name = name; s.valstep = step
    s.label.set_color('white'); s.valtext.set_color('white')
    s.on_changed(lambda v, s=s: on_slider_change(s, v))
    sliders[name] = s

# === INITIAL NOISE ===
ph0 = params['view_height'] // (2*params['num_bars'])
sliding_bars, stationary_gaps = generate_static(
    params['num_bars'], ph0, params['view_width'], params['pixel_size']
)

plt.show()
