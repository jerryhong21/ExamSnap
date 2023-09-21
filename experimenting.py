import fitz  # PyMuPDF
import json
import re
import glob

files = glob.glob("./exam_papers/*.pdf")
for file in files:
    print(file)
    


def add_circle(page, x, y, radius):
    circle_annot = page.add_circle_annot([x, y], radius)
    circle_annot.set_colors(fill=(1, 0, 0))  # Set the fill color to red


# Open a PDF document
pdf = '2018_Final_Exam.pdf'
pdf_document = fitz.open(pdf)

# Select a page (e.g., page 0)
page_number = 11
page = pdf_document[page_number]

x, y = 57.10624313354492, 70.39580535888672
radius = 5
# add_circle(page, x, y, radius)

# Get the text elements on the page as dictionaries
# data = json.loads(page.get_text("json"))
data = page.get_text("dict")
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


getHeight('Question 24', page)
