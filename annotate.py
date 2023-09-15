import fitz  # PyMuPDF
import json

# Open a PDF file
pdf = './exam_papers/2020-hsc-biology.pdf'
pdf_document = fitz.open(pdf)

# Select a page (e.g., page 0)
page = pdf_document[16]

# Define the circle annotation parameters
# (x1, y1, x2, y2) coordinates of the circle bounding box
circle_annot_rect1 = fitz.Rect(
    (70.72830200195312, 66.694580078125, 187.97552490234375, 80.08657836914062))
page.add_rect_annot(circle_annot_rect1)

# circle_annot_rect2 = fitz.Rect(
#     56.63999938964844, 427.0662536621094, 316.5990905761719, 495.5558166503906)
# page.add_rect_annot(circle_annot_rect2)


# Save the modified PDF
pdf_document.save('output.pdf')
pdf_document.close()
