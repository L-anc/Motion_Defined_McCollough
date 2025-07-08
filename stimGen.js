const PANEL = 384;
let params = { numBars:16, staticRate:1, pixelSize:1, blend:0, colorStr:0, speed:1 };
let motionEnabled = true, regenEnabled = false, colorWhitesEnabled = false, lastRegen = 0;
let hStripe = [], hGap = [], vStripe = [], vGap = [];

function setup() {
    pixelDensity(1);
    noSmooth();
    createCanvas(PANEL*2, PANEL*2);
    frameRate(30);
    wireControls();
    regenAll();
}

function draw() {
    background(0);
    const nb = params.numBars,
        ph = floor(PANEL/(2*nb)),
        f  = frameCount,
        rf = max(1, round(params.staticRate));

    if (hGap.length !== nb) {
    regenAll(); lastRegen = f;
    } else if (regenEnabled && f - lastRegen >= rf) {
    regenStripes(); lastRegen = f;
    }

    const offH = regenEnabled ? 0 : (motionEnabled ? floor(f * params.speed) % PANEL : 0);
    const offV = regenEnabled ? 0 : (motionEnabled ? floor(f * params.speed) % PANEL : 0);

    // ── TOP-LEFT (Horizontal stripes)
    push(); drawingContext.beginPath(); drawingContext.rect(0,0,PANEL,PANEL); drawingContext.clip();
    for (let i = 0; i < nb; i++) {
    const y0 = i*2*ph;
    // noise versions
    image(hStripe[i], -offH,       y0);
    image(hStripe[i], PANEL-offH,  y0);
    image(hGap[i],    0,           y0+ph);

    // blend overlay (white for stripe / black for gap)
    if (params.blend > 0) {
        noStroke();
        fill(255, 255 * params.blend); //black stripe
        rect(0, y0, PANEL, ph);
        fill(0, 255 * params.blend);//white stripe
        rect(0, y0+ph, PANEL, ph);
    }

    // colorStr overlay
    if (params.colorStr > 0) {
        noStroke();
        fill(255, 0, 0, 255 * params.colorStr);
        rect(0, y0, PANEL, ph);
    }
    }
    pop();

    // ── TOP-RIGHT (Vertical stripes)
    push(); drawingContext.beginPath(); drawingContext.rect(PANEL,0,PANEL,PANEL); drawingContext.clip();
    for (let i = 0; i < nb; i++) {
    const x0 = i*2*ph;
    image(vStripe[i], PANEL+x0,      -offV);
    image(vStripe[i], PANEL+x0,      PANEL-offV);
    image(vGap[i],    PANEL+x0+ph,   0);

    if (params.blend > 0) {
        noStroke();
        fill(255, 255 * params.blend);
        rect(PANEL+x0, 0, ph, PANEL);
        fill(0,   255 * params.blend);
        rect(PANEL+x0+ph, 0, ph, PANEL);
    }

    if (params.colorStr > 0) {
        noStroke();
        fill(0,255,0, 255 * params.colorStr);
        rect(PANEL+x0, 0, ph, PANEL);
    }
    }
    pop();

    // ── BOTTOM-LEFT (Vertical stripes)
    push(); drawingContext.beginPath(); drawingContext.rect(0,PANEL,PANEL,PANEL); drawingContext.clip();
    for (let i = 0; i < nb; i++) {
    const x0 = i*2*ph;
    image(vStripe[i], x0,     PANEL-offV);
    image(vStripe[i], x0,     2*PANEL-offV);
    image(vGap[i],    x0+ph,  PANEL);

    if (params.blend > 0) {
        noStroke();
        fill(255, 255 * params.blend);
        rect(x0, PANEL, ph, PANEL);
        fill(0,   255 * params.blend);
        rect(x0+ph, PANEL, ph, PANEL);
    }

    if (params.colorStr > 0) {
        noStroke();
        fill(0,255,0, 255 * params.colorStr);
        rect(x0, PANEL, ph, PANEL);
    }
    }
    pop();

    // ── BOTTOM-RIGHT (Horizontal stripes)
    push(); drawingContext.beginPath(); drawingContext.rect(PANEL,PANEL,PANEL,PANEL); drawingContext.clip();
    for (let i = 0; i < nb; i++) {
    const y0 = i*2*ph;
    image(hStripe[i], PANEL-offH,       PANEL+y0);
    image(hStripe[i], 2*PANEL-offH,     PANEL+y0);
    image(hGap[i],    PANEL,           PANEL+y0+ph);

    if (params.blend > 0) {
        noStroke();
        fill(255, 255 * params.blend);
        rect(PANEL, PANEL+y0, PANEL, ph);
        fill(0,   255 * params.blend);
        rect(PANEL, PANEL+y0+ph, PANEL, ph);
    }

    if (params.colorStr > 0) {
        noStroke();
        fill(255,0,0, 255 * params.colorStr);
        rect(PANEL, PANEL+y0, PANEL, ph);
    }
    }
    pop();

    // ── TRAINING-MOTION DEFINED: swap any remaining pure-white pixels
    if (colorWhitesEnabled) {
    loadPixels();
    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
        const idx = 4 * (y * width + x);
        if (
            pixels[idx]   === 255 &&
            pixels[idx+1] === 255 &&
            pixels[idx+2] === 255
        ) {
            // determine quadrant:
            if (x < PANEL && y < PANEL) {
            // top-left → red
            pixels[idx] = 255; pixels[idx+1] = 0;   pixels[idx+2] = 0;
            } else if (x >= PANEL && y < PANEL) {
            // top-right → green
            pixels[idx] = 0;   pixels[idx+1] = 255; pixels[idx+2] = 0;
            } else if (x < PANEL && y >= PANEL) {
            // bottom-left → green
            pixels[idx] = 0;   pixels[idx+1] = 255; pixels[idx+2] = 0;
            } else {
            // bottom-right → red
            pixels[idx] = 255; pixels[idx+1] = 0;   pixels[idx+2] = 0;
            }
        }
        }
    }
    updatePixels();
    }
}

function regenAll() {
    hStripe = []; hGap = []; vStripe = []; vGap = [];
    const nb = params.numBars,
        ph = floor(PANEL/(2*nb)),
        scaleLow = 1/params.pixelSize,
        lowH = max(1, floor(ph * scaleLow)),
        lowW = max(1, floor(PANEL * scaleLow));

    for (let i = 0; i < nb; i++) {
    const A = Array.from({length: lowH}, () => Array.from({length: lowW}, () => random()>0.5?1:0));
    const B = Array.from({length: lowH}, () => Array.from({length: lowW}, () => random()>0.5?1:0));
    let S = createImage(PANEL, ph), G = createImage(PANEL, ph);
    S.loadPixels(); G.loadPixels();
    for (let y = 0; y < ph; y++) {
        const ly = floor(y*scaleLow);
        for (let x = 0; x < PANEL; x++) {
        const lx = floor(x*scaleLow),
                idx = 4*(y*PANEL + x),
                v1  = A[ly][lx]*255,
                v2  = B[ly][lx]*255;
        S.pixels[idx]   = v1; S.pixels[idx+1] = v1; S.pixels[idx+2] = v1; S.pixels[idx+3] = 255;
        G.pixels[idx]   = v2; G.pixels[idx+1] = v2; G.pixels[idx+2] = v2; G.pixels[idx+3] = 255;
        }
    }
    S.updatePixels(); G.updatePixels();
    hStripe.push(S); hGap.push(G);

    const vs = createGraphics(ph, PANEL),
            vg = createGraphics(ph, PANEL);
    vs.noSmooth(); vg.noSmooth();
    vs.push(); vs.translate(0,PANEL); vs.rotate(-HALF_PI); vs.image(S,0,0); vs.pop();
    vg.push(); vg.translate(0,PANEL); vg.rotate(-HALF_PI); vg.image(G,0,0); vs.pop();
    vStripe.push(vs); vGap.push(vg);
    }
}

function regenStripes() {
    hStripe = []; vStripe = [];
    const nb = params.numBars,
        ph = floor(PANEL/(2*nb)),
        scaleLow = 1/params.pixelSize,
        lowH = max(1, floor(ph*scaleLow)),
        lowW = max(1, floor(PANEL*scaleLow));
    for (let i = 0; i < nb; i++) {
    const A = Array.from({length: lowH}, () => Array.from({length: lowW}, () => random()>0.5?1:0));
    let S = createImage(PANEL, ph);
    S.loadPixels();
    for (let y = 0; y < ph; y++) {
        const ly = floor(y*scaleLow);
        for (let x = 0; x < PANEL; x++) {
        const lx = floor(x*scaleLow),
                idx = 4*(y*PANEL + x),
                v1  = A[ly][lx]*255;
        S.pixels[idx]   = v1; S.pixels[idx+1] = v1; S.pixels[idx+2] = v1; S.pixels[idx+3] = 255;
        }
    }
    S.updatePixels();
    hStripe.push(S);
    const vs = createGraphics(ph, PANEL);
    vs.noSmooth();
    vs.push(); vs.translate(0,PANEL); vs.rotate(-HALF_PI); vs.image(S,0,0); vs.pop();
    vStripe.push(vs);
    }
}

function wireControls() {
    function hook(id, key, fmt) {
    const s = document.getElementById(id),
            v = document.getElementById(id+'Val');
    s.oninput = () => {
        params[key] = parseFloat(s.value);
        v.textContent = fmt(params[key]);
        if (key==='numBars') regenAll();
    };
    s.oninput();
    }
    hook('numBars','numBars', v=>v.toFixed(0));
    hook('staticRate','staticRate', v=>v.toFixed(1));
    hook('pixelSize','pixelSize', v=>v.toFixed(1));
    hook('blend','blend', v=>v.toFixed(2));
    hook('colorStr','colorStr', v=>v.toFixed(2));
    hook('speed','speed', v=>v.toFixed(1));
    document.getElementById('motion').onchange   = e => motionEnabled      = e.target.checked;
    document.getElementById('randStat').onchange = e => regenEnabled       = e.target.checked;
    document.getElementById('colWhite').onchange = e => colorWhitesEnabled = e.target.checked;
}