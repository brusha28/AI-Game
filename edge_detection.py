import os
import cv2
import numpy as np
from rembg import remove

def extract_shape(image_path):
    # Load the image
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Remove the background
    result = remove(image_rgb)

    # Ensure the result has 3 channels
    if result.shape[2] == 4:  # If the result has an alpha channel, remove it
        result = cv2.cvtColor(result, cv2.COLOR_BGRA2BGR)
    elif result.shape[2] == 1:  # If the result is grayscale, convert it to RGB
        result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)

    # Convert the result to uint8
    result = result.astype(np.uint8)

    # Binarize the result image
    _, result = cv2.threshold(result, 1, 255, cv2.THRESH_BINARY)

    # Fill in gaps in the white blobs
    kernel = np.ones((25, 25), np.uint8)
    result = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel)

    # Ensure the result is in grayscale
    if len(result.shape) == 3 and result.shape[2] == 3:
        result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

    # Binarize again to ensure only black and white pixels
    _, result = cv2.threshold(result, 1, 255, cv2.THRESH_BINARY)

    # Find contours of the white object
    contours, _ = cv2.findContours(result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        # Get the bounding box of the largest contour
        x, y, w, h = cv2.boundingRect(contours[0])

        # Create a square bounding box
        size = max(w, h)
        square_result = np.zeros((size, size), dtype=np.uint8)

        # Calculate padding to center the object in the square
        x_pad = (size - w) // 2
        y_pad = (size - h) // 2

        # Place the object in the center of the square
        square_result[y_pad:y_pad+h, x_pad:x_pad+w] = result[y:y+h, x:x+w]

        result = square_result

    result = cv2.bitwise_not(result)

    return result