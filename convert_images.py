from pdf2image import convert_from_path
import cv2
import numpy as np
# import pytesseract

pdf_file_path = "URS_02_A_Referene_Training_Curriculum.pdf"  # Replace with your PDF path

# Convert PDF to images
images = convert_from_path(pdf_file_path, dpi=300)

for i, img in enumerate(images):
    img.save(f"page_{i}.png", "PNG")

# Load Image
image = cv2.imread("page_0.png", cv2.IMREAD_GRAYSCALE)

# Threshold to detect tick marks
_, thresh = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY_INV)

# Find contours (tick marks)
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    if w < 15 and h < 15:  # Filtering small blobs
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

cv2.imshow("Detected Ticks", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
