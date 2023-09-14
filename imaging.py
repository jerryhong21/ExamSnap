import fitz  # PyMuPDF
import cv2
import numpy as np
import re


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
    return [0,0]


def is_bold(font):
    """
    Check if a font is likely to represent bold text.
    """
    font_flags = font.flags
    font_weight = font.font_weight

    # Check font flags and weight for common bold indicators
    return ("Bold" in font_flags) or (font_weight >= 700)


def extract_text_from_pdf(pdf_file):
    doc = fitz.open(pdf_file)
    text = []

    for page in doc:
        text.append(page.get_text())

    return text

# to deal with questions that extend pages, we can look for the regex question... continues...


class QuestionClass:
    def __init__(self, page_number, question_number, height):
        self.page_number = page_number
        self.question_number = question_number
        self.height = height


def detect_pattern_in_text(doc):

    # Regular expression to match "Question" followed by one or more spaces and one or more digits
    # pattern = r"Question\s+\d+(?:(?!continued).)*"
    # pattern = r"Question\s+\d+(?![\s\S]*continue)[\s\S]*"
    questions_mapped = []

    pattern = r"Question\s+\d+(?![\r\n]*continue)[\r\n\S]*"
    # Pattern below excludes
    # 'continue' following a question, this indicates a mere sentence saying question continues...
    # Any hyphens in expression - indicates a question range, not an actual question
    pattern = r"Question\s+\d+\s*(?![\r\n-]*continue)[\r\n\S]*"


    pages_with_pattern = []

    for page_number, page in enumerate(doc):
        # Page size in points (width, height)
        page_size = (page.rect.width, page.rect.height)
        
        page_text = page.get_text()

        # Use re.IGNORECASE to match "Question" case-insensitively
        matches = re.finditer(pattern, page_text, re.IGNORECASE)
        for match in matches:
            question = match.group(0)
            print(question)
            if question not in questions_mapped:
                # Setting pattern to look for specific to question number
                questionNumberPattern = r'\b' + \
                    re.escape(question) + r'\b(?![\w-]*-)'
                
                x0y0 = getHeight(questionNumberPattern, doc[page_number])
                y0 = x0y0[1]
                x0 = x0y0[0]
                
                questions_mapped.append(QuestionClass(
                    page_number, question, y0))
                pages_with_pattern.append(page_number)

        # in each page, store relevant question information into a question class

    # print(pages_with_pattern)
    # print(questions_mapped)
    # for question in questions_mapped:
    #     print(question.question_number)
    #     print(question.height)

    return pages_with_pattern


def capture_screenshots(pdf_file):
    text = extract_text_from_pdf(pdf_file)
    doc = fitz.open(pdf_file)
    # print(doc[11].get_text())
    pages_with_pattern = detect_pattern_in_text(doc)

    # Open PDF again to capture screenshots
    doc = fitz.open(pdf_file)
    for page_number in pages_with_pattern:
        page = doc[page_number]
        pix = page.get_pixmap()
        screenshot = np.frombuffer(
            pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        cv2.imwrite(f"page_{page_number}.png", screenshot)


if __name__ == "__main__":
    pdf_file = "2018_Final_Exam.pdf"  # Replace with the path to your PDF file
    capture_screenshots(pdf_file)

# TODO: modify the find patterns function to also return the index of these matches on each page.
# take screenshot - we can CROP question to fit the dimensions, we cna determine the dimensions by getting where the question starts, and where the next queston is (index).
# must consider cases: if question ends on the page
# if question continues to the next page
# Update pattern regex to exclude expressions with a hyphen between them
