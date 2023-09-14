import fitz  # PyMuPDF
import json

# Open a PDF file
pdf = '2018_Final_Exam.pdf'
pdf_document = fitz.open(pdf)

# Select a page (e.g., page 0)
page = pdf_document[11]

# Define the circle annotation parameters
# (x1, y1, x2, y2) coordinates of the circle bounding box
circle_annot_rect1 = fitz.Rect(
    200, 440, 536.6965942382812, 166.99578857421875)
page.add_rect_annot(circle_annot_rect1)

# circle_annot_rect2 = fitz.Rect(
#     56.63999938964844, 427.0662536621094, 316.5990905761719, 495.5558166503906)
# page.add_rect_annot(circle_annot_rect2)


# Save the modified PDF
pdf_document.save('output.pdf')
pdf_document.close()
