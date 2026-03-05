# Rubick-Vision-Solver
Algorithm to solve 3x3 cube with Image Processing and OpenCV

# Introduction

| Right Face (U) | Canny Visualization (C) |
| :---: | :---: |
| ![Upper Example](assets/Left.jpeg) | ![Front Example](assets/LeftCanny.jpeg) |

The input are 6 photos, so it's pratical for the user, instead of coloring the cube each square. The algorithm processes these images to identify the cube's state and provides a step-by-step solution using the Kociemba algorithm.

# Technical Challenges & Solutions

To solve a cube from photos, I dealt with three main problems:

 ## 1. Square & Face Detection (The Vision Pipeline)

Detecting stickers in varying light is difficult. I implemented an Adaptive Edge Detection system using   OpenCV's Canny and filters.

  Adaptive Canny: The code analyzes the image's average brightness to adjust Canny thresholds, since each photo can have different quality and light, ensuring detection works on both black and white cube frames.

  Filters: cv2.dilate to bridge small gaps in detected edges, helping the algorithm close contours that might be broken by reflections, also two more filters.

  Plan B (Grid Inference): If the algorithm fails to find 9 individual stickers (it can happen with a background too bright or dark or low-contrast colors, like white stickers on a white frame), it identifies the face's overall contour to then mathematically infers the 9 stickers.

## 2. Color Classification (HSV ROI Sampling)

Instead of relying on RGB values, that were tested, I converted images to the HSV (Hue, Saturation, Value) color space.

  ROI Area: For each detected square, the program defines a Region of Interest (ROI) in the center to calculate the average color, that garantes a more correct detection even if the square is a little wrong.

  Mapping: My logic maps colors to face notations (U, R, F, D, L, B) based on the center stickers. Even if you have a custom-colored cube, the program identifies which color represents which face by looking at the sticker in index 4, but is more relaible on a standard 3x3 cube.

## 3. Spatial Sorting

The algorithm detects the squares in a random order. I developeda a sort_centers function that organizes the 9 detected stickers into a logical sequence (top-left to bottom-right). This ensures the resulting 54-character string matches the physical structure required by the Kociemba library.

## 4.Explainig Solution

Since most of the people don't know the language used by Kociemba library, I created a function explaining each of the moves so the person doesn't understand how to resolve the cube.

The normal output of Kociemba: U F' L2 R'.

With my function:

1. Up: Turn clockwise;

2. Front: Turn counterclockwise;

3. Left: Turn 180 degrees;

4. Right: Turn counterclockwise;

## User Experience (UX) & Validation

To ensure that my program was successful and the cube will have a solution, there is a verification loop in the terminal, also the photos have to be taken according to the instructions:

  The user follows specific rotation instructions (e.g., "Keep Top pointing UP, rotate cube 90° LEFT").

  After each photo, a window displays the detected stickers and their classified colors.

  The user confirms if the detection is correct. If not, they can retry that specific face without restarting the entire process.

 ## How to Run

  Clone the repository.

  Install dependencies: pip install opencv-python numpy kociemba.

  Run the main script: python3 main.py.

  Follow the on-screen instructions to capture all 6 faces.

## Requirements

  Python 3.12+;

  OpenCV (cv2);

  Numpy;

  Kociemba (Solving library);
