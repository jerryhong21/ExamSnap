import fitz  # PyMuPDF
import cv2
import numpy as np
import re
import os


# navigating through the dictionary structure of page to obtain x0, y0 of text
def getHeight(pattern, page):
    data = page.get_text("dict")
    for block in data['blocks']:
        for line in block['lines']:
            for span in line['spans']:
                if re.match(pattern, span['text']) != None:
                    bbox = span['bbox']
                    # returns x and y position of element from top of page
                    return [bbox[0], bbox[1]]

    # this return statmenet case is not accounted for - since the pages put in are assumed to contain question...
    return [0, 0]


def extract_text_from_pdf(pdf_file):
    doc = fitz.open(pdf_file)
    text = []

    for page in doc:
        text.append(page.get_text())

    return text

# to deal with questions that extend pages, we can look for the regex question... continues...


class QuestionClass:
    def __init__(self, page_number, question_number, x0, y0, x1, y1):
        self.page_number = page_number
        self.question_number = question_number
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1


def question_exists(question_arr, new_question):
    for question in question_arr:
        if question.page_number == new_question.page_number and question.question_number == new_question.question_number:
            return True

    return False


def detect_pattern_in_text(doc):

    # Regular expression to match "Question" followed by one or more spaces and one or more digits
    # pattern = r"Question\s+\d+(?:(?!continued).)*"
    # pattern = r"Question\s+\d+(?![\s\S]*continue)[\s\S]*"

    # Pattern below excludes:
    # 'continue' following a question, this indicates a mere sentence saying question continues...
    # Any hyphens in expression - indicates a question range, not an actual question
    # [NOT WORKING RIGHT NOW - IMPLEMENT LATER]
    # pattern = r"Question\s+\d+\s*(?![\r\n-]*continue)[\r\n\S]*"

    pattern = r"Question\s+\d+(?![\r\n]*continue)[\r\n\S]*"

    pages_with_pattern = []
    questions_mapped = []

    for page_number, page in enumerate(doc):
        # Page size in points (width, height)
        page_text = page.get_text()
        default_width = page.rect.width
        default_height = page.rect.height

        # Use re.IGNORECASE to match "Question" case-insensitively
        matches = re.finditer(pattern, page_text, re.IGNORECASE)
        for match in matches:
            question = match.group(0)
            # Setting pattern to look for specific to question number
            questionNumberPattern = r'\b' + \
                re.escape(question) + r'\b(?![\w-]*-)'
            x0y0 = getHeight(questionNumberPattern, doc[page_number])
            # set threshold of x where after x, any "question" detected is seen as invalid
            x_threshold = 200
            if (x0y0[0] > x_threshold):
                continue
            new_question = QuestionClass(
                page_number, question, x0y0[0], x0y0[1], default_width, default_height)
            if not question_exists(questions_mapped, new_question):
                questions_mapped.append(new_question)

    return questions_mapped


def capture_screenshots(pdf_file, exam_name):
    text = extract_text_from_pdf(pdf_file)
    doc = fitz.open(pdf_file)
    # print(doc[11].get_text())
    questions_mapped = detect_pattern_in_text(doc)
    set_lower_bounds(questions_mapped)

    # Open PDF again to capture screenshots
    doc = fitz.open(pdf_file)

    for question in questions_mapped:
        page_number = question.page_number
        page = doc[page_number]
        pix = page.get_pixmap()
        screenshot = np.frombuffer(
            pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        png_file = f"{exam_name}_{question.question_number}_Page{question.page_number}.png"
        cv2.imwrite(png_file, screenshot)  # saving file

        # cropping file to contain singular question
        image = cv2.imread(png_file)
        cropped_image = crop_image(page, question, image)
        cv2.imwrite(png_file, cropped_image)


def int_question_number(question_number):

    parts = question_number.split()
    return int(parts[-1])


# This function assumes the questions array passed in is in order
def set_lower_bounds(questions):
    for i in range(len(questions) - 1):
        curr = questions[i]
        next = questions[i + 1]
        # if curr and next exist on same page
        if int_question_number(curr.question_number) - int_question_number(next.question_number) == -1 and curr.page_number == next.page_number:
            curr.y1 = next.y0


def crop_image(page, question, image):
    page_width = page.rect.width
    page_height = page.rect.height

    x1, y1 = int(question.x0), int(question.y0)  # Top-left corner
    x2, y2 = int(question.x1), int(question.y1)  # Bottom-right corner
    cropped_image = image[y1:y2, x1:x2]

    return cropped_image


if __name__ == "__main__":
    # pdf_file = "2018_Final_Exam.pdf"  # Replace with the path to your PDF file
    # Replace with the path to your PDF file
    # exam_name = "Sydney Boys 2020 Physics Prelim Yearly & Solutions"
    exam_name = "2018_Final_Exam"
    pdf_file = f"{exam_name}.pdf"
    capture_screenshots(pdf_file, exam_name)


# TODO: FIGURE OUT HOW TO DETECT PAGES OF QUESTION CONTINUATION
# EXCLUDE QUESTIONS 1-4 RANGES IN DETECTION
# MULTIPLE CHOICE SECTION DETECTION - RECOGNISE NUMBERS ON LEFT HAND SIDE? RECOGNISE BOLD FONTS?