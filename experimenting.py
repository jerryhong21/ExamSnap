import fitz  # PyMuPDF
import json
import re
import glob
from mc_detection import get_left_text
# import cairosvg
import numpy as np
import os
import cv2
from PyPDF2 import PdfReader
from io import BytesIO
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg
from pdf2image import convert_from_path
import threading


def code_to_run():
    global operation_done
    try:
        pix = page.get_pixmap()  # The potentially problematic line
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        operation_done = True



files = glob.glob("./exam_papers/*.pdf")


def add_circle(page, x, y, radius):
    circle_annot = page.add_circle_annot([x, y], radius)
    circle_annot.set_colors(fill=(1, 0, 0))  # Set the fill color to red


# Open a PDF document
pdf = './exam_papers/2019-hsc-physics.pdf'
# images = convert_from_path(pdf, dpi=300)
# images[24].save('output.png', 'PNG')

pdf_document = fitz.open(pdf)

# Select a page (e.g., page 0)
page = pdf_document[24]
# Set a timeout in seconds
timeout_in_seconds = 10  # Adjust this as needed

# Create a thread for the code
thread = threading.Thread(target=code_to_run)

# Start the thread
thread.start()

# Wait for the thread to complete or time out
thread.join(timeout=timeout_in_seconds)

# Check if the operation is done
if not operation_done:
    print("Operation timed out")
    # Handle the timeout (e.g., move on to the next task)
else:
    print("Operation completed successfully")
# pdf2 = PdfReader(pdf)
# page = pdf2.pages[24]
# print(page)
# Convert the PDF page to a pixmap (bitmap image)
# pixmap = renderPM.drawToPIL(page)
# pixmap_np = np.array(pixmap)

# print(page.get_text('dict'))
# svg_image = page.get_svg_image()
# drawing = svg2rlg(svg_image, scale=1.0)
# pdf_filename = 'temp.pdf'
# renderPM.drawToFile(drawing, pdf_filename, fmt='PDF')
# png_data = cairosvg.svg2png(bytestring=svg.data)
# png_array = np.frombuffer(png_data, dtype=np.uint8)
# h, w = 100, 100  # Replace with actual height and width
# reshaped_array = png_array.reshape((h, w, 4))
# cv2.imwrite('./thisisascrrenshot.png', pixmap_np)
print('SUCCESS')


# # left_text = get_left_text(page)
# filtered_left_text = [
#     element for element in left_text if re.search(r'\d', element)]
# print(filtered_left_text)

# x, y = 57.10624313354492, 70.39580535888672
# radius = 5
# # add_circle(page, x, y, radius)

# Get the text elements on the page as dictionaries
# data = json.loads(page.get_text("json"))
# data = page.get_text()
# print(data)


# for item in data:
#     print(item)
#     spans = item.get("spans", [])
#     for span in spans:
#         text = span.get("text", "")
#         print("Text:", text)


# print(text_elements[0])
# print(text_elements['width'])
# for block in data['blocks']:
#     for line in block['lines']:
#         for span in line['spans']:
#             print(span['text'])
#             print(span['origin'])
#             print(span['bbox'])

pattern = r"Question\s+\d+(?![\r\n]*continue)[\r\n\S]*"


def getHeight(pattern, page):
    data = page.get_text("dict")
    for block in data['blocks']:
        # print(block['number'])
        # print(line)
        # print(line['spans'])

        for line in block['lines']:
            for span in line['spans']:
                if re.match(pattern, span['text']) != None:
                    bbox = span['bbox']
                    return bbox[1]

    # returns height of element from top of page
    return bbox[1]


# getHeight('Question 24', page)
