from pdf2image import convert_from_path
from PIL import Image, ImageOps
from statistics import median
from io import BytesIO
import numpy as np
import cv2
import tempfile


def deskew_image(image):
    # Convert PIL image to numpy array
    image_array = np.array(image)

    # Convert to grayscale
    gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)

    # Apply edge detection
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Detect lines using Hough Line Transform
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    # Calculate the angle of skew based on the detected lines
    if lines is not None:
        angles = []
        for rho, theta in lines[:, 0]:
            angle = np.rad2deg(theta) - 90  # Adjust to correct orientation
            if -45 < angle < 45:  # Filter to keep near-horizontal lines only
                angles.append(angle)

        # Use median angle to reduce the effect of outliers
        if len(angles) > 0:
            skew_angle = median(angles)
        else:
            skew_angle = 0
    else:
        skew_angle = 0

    # Rotate the image to correct the skew
    (h, w) = image_array.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, skew_angle, 1.0)
    deskewed = cv2.warpAffine(image_array, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # Convert back to PIL image
    deskewed_image = Image.fromarray(deskewed)
    return deskewed_image





def deskew_pdf(input_pdf_bytes):
    # Step 1: Convert the in-memory PDF to a list of images
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(input_pdf_bytes)
        temp_pdf_path = temp_pdf.name

    images = convert_from_path(temp_pdf_path)

    # Step 2: Deskew each image
    deskewed_images = [deskew_image(image) for image in images]

    # Step 3: Convert deskewed images back to a PDF in memory
    output_pdf = BytesIO()
    deskewed_images[0].save(output_pdf, format='PDF', save_all=True, append_images=deskewed_images[1:])

    # Step 4: Return the in-memory PDF bytes
    return output_pdf.getvalue()


