# PinMX Number CAPTCHA Solver

## The Problem
PinMX uses a simple image CAPTCHA containing 6 digits with a line drawn through them and some noise dots.
Because we cannot use external OCR APIs (like Tesseract.js via NPM) or paid services (like 2Captcha), we must build an in-house native solver.

## The Solution (In-House JS Native OCR)
We will use the `browser` tool's `evaluate` action to run a pure JavaScript image processing function directly inside the webpage.

### Steps:
1. Grab the canvas or image element containing the CAPTCHA (`.captcha-img` or similar).
2. Extract the pixel data using `canvas.getContext('2d').getImageData()`.
3. Apply a native image thresholding algorithm (convert to pure black and white, remove the thin line/noise).
4. Extract the bounding boxes of the 6 digits.
5. Use a simple, hardcoded matrix comparison (template matching) against a pre-defined set of 0-9 digits (since PinMX uses a standard font).
6. Auto-fill the input box.

## Next Action for Developer Army
1. Capture the raw base64 of the PinMX CAPTCHA image.
2. Build the pure JS thresholding script.
3. Map the 10 digits.
