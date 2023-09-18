import fitz  # PyMuPDF
import cv2
import numpy as np
import re
import os

# navigating through the dictionary structure of page to obtain x0, y0 of text
# TODO: ADD ERROR CHECKS UNDER EVERY FOR LOOP, if a particular piece of text does not have a certain attribute, CONTINUE!


def getHeight(pattern, page):
    breaks = False
    data = page.get_text("dict")
    for block in data['blocks']:
        if 'lines' not in block:
            continue
        for line in block['lines']:
            if 'spans' not in line:
                continue
            for span in line['spans']:
                if 'text' not in span:
                    continue
                if re.match(pattern, span['text']) != None:
                    bbox = span['bbox']
                    # returns x and y position of element from top of page
                    return [bbox[0], bbox[1]]

    # if the return bbox = [0,0] then the pattern has not been detected and should therefore be rejected
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


def find_mc_questions(doc, questions_mapped):
    # set regex pattern to detect multiple choice questions
    # can set a binary pattern? detect 1, 2, 3 within x margin
    # OR detect Question 1, Question 2... within x + c margin
    # set margin from sample spaces
    return questions_mapped


def find_written_questions(doc, questions_mapped):

    # Regular expression to match "Question" followed by one or more spaces and one or more digits
    # Pattern below excludes:
    # 'continue' following a question, this indicates a mere sentence saying question continues...
    # Any hyphens in expression - indicates a question range, not an actual question
    # [NOT WORKING RIGHT NOW - IMPLEMENT LATER]
    # pattern = r"Question\s+\d+\s*(?![\r\n-]*continue)[\r\n\S]*"
    pattern = r"Question\s+\d+(?![\r\n]*continue)[\r\n\S]*"

    for page_number, page in enumerate(doc):
        # Page size in points (width, height)
        page_text = page.get_text()
        default_width = page.rect.width
        default_height = page.rect.height

        # Use re.IGNORECASE to match "Question" case-insensitively
        matches = re.finditer(pattern, page_text, re.IGNORECASE)
        for match in matches:
            question = match.group(0)
            print(question)
            # Setting pattern to look for specific to question number
            question_number_pattern = r'\b' + \
                re.escape(question) + r'\b(?![\w-]*-)'
            x0y0 = getHeight(question_number_pattern, doc[page_number])
            # set threshold of x where after x, any "question" detected is seen as invalid
            x_threshold = 200
            # if detected pattern is to the right of accepted margin OR not in the question_number_pattern
            if x0y0[0] > x_threshold or x0y0 == [0, 0]:
                continue
            new_question = QuestionClass(
                page_number, question, x0y0[0], x0y0[1], default_width, default_height)
            if not question_exists(questions_mapped, new_question):
                questions_mapped.append(new_question)

    # go through questions_mapped and look for gaps in page numbers, if the gap is 1-3, then insert question to array
    questions_mapped = find_question_cont(questions_mapped, doc)

    return questions_mapped

# Function to find question continuation - this occurs in papers where continuations of questions on the next page is not explicitly labled
# e.g. instead of the hsc format: Question 26 (continued), some papers do not label and carry straight on from the previous page

# TODO: Check if we are accounting for continuation of the last question


def find_question_cont(questions, doc):

    # gaps = True
    # REMOVE THE WHILE LOOP TO TEMPORARILY FIX CODE
    # while gaps:
    breaks = 0
    question_append = []
    for i in range(len(questions) - 2):
        breaks = 0
        curr = questions[i]
        # print(curr.question_number)
        next = questions[i + 1]
        # print(next.question_number)
        if (next.page_number - curr.page_number <= 4 and next.page_number - curr.page_number > 1):
            print(curr.question_number + ': continuation detected')
            page = doc[curr.page_number]
            default_width = page.rect.width
            default_height = page.rect.height
            new_question = QuestionClass(
                curr.page_number + 1, curr.question_number, 0, 0, default_width, default_height)
            question_append.append(new_question)

    for question_to_append in question_append:
        qn = question_to_append.question_number
        # print(len(questions))
        for question in questions:
            # print(question)
            if question.question_number == qn:
                index = questions.index(question)
                questions.insert(index, question_to_append)
                breaks = breaks + 1
                break

    if (breaks == 0):
        print('No question gaps were found')
        # for question in question_append:
        #     print(question.question_number)
        #     print(question.page_number)

    return questions


# Finds all questions on the pdf doc returns array containing all questions
def find_all_questions(doc):
    questions_mapped = []
    # questions_mapped = find_mc_questions(doc, questions_mapped)
    questions_mapped = find_written_questions(doc, questions_mapped)

    return questions_mapped


def capture_screenshots(pdf_file, exam_name):
    doc = fitz.open(pdf_file)
    print(pdf_file)

    questions_mapped = find_all_questions(doc)
    print(questions_mapped)
    # perhaps we need to first SORT questions into order, in case the algorithm has detected a question before another
    # search for sorting algoritms in python
    set_lower_bounds(questions_mapped)

    # loop through all questions in question array and capture screenshots
    for question in questions_mapped:
        page_number = question.page_number
        page = doc[page_number]
        pix = page.get_pixmap()

        # capture screenshot in a pix array
        screenshot = np.frombuffer(
            pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        # PNG file that goes to a folder named after exam
        folder_name = 'exam_images'
        png_file = f"./{folder_name}/{exam_name}_{question.question_number}_Page{question.page_number}.png"
        # print(png_file)
        # png_file = f"{exam_name}_{question.question_number}_Page{question.page_number}.png"

        # saving screenshot file
        cv2.imwrite(png_file, screenshot)

        # cropping file to contain singular question
        image = cv2.imread(png_file)
        cropped_image = crop_image(page, question, image)
        cv2.imwrite(png_file, cropped_image)
        # print(f'File written to directory: {png_file}')


# extracts question number integer (e.g. int_question_number('Question 24') = 24)
def int_question_number(question_number):
    if 'Question' in question_number or 'question' in question_number:
        parts = question_number.split()
        return int(parts[-1])

    # if 0 is returned then error as occured
    print(f"An error occured while converting {question_number} to integer")
    return 0


# This function assumes the questions array passed in is in order
def set_lower_bounds(questions):
    for i in range(len(questions) - 2):
        curr = questions[i]
        next = questions[i + 1]
        # if curr and next exist on same page)
        # print(curr.question_number)
        # print(next.question_number)
        if int_question_number(curr.question_number) - int_question_number(next.question_number) == -1 and curr.page_number == next.page_number:
            curr.y1 = next.y0


# sets crops all question images to end at lower bounds
def crop_image(page, question, image):
    page_width = page.rect.width
    page_height = page.rect.height

    x1, y1 = int(question.x0) - 5, int(question.y0)  # Top-left corner
    x2, y2 = int(question.x1), int(question.y1)  # Bottom-right corner
    cropped_image = image[y1:y2, x1:x2]

    return cropped_image


# main function
if __name__ == "__main__":
    # Replace with the name of exam pdf
    exam_name = "2018 Project Academy"
    exam_names = [
        "Carlingford Preliminary Physics (2019) Yearly Examination",
        "2018 Project Academy",
        "2019_TEC"]
    exam_folder = './exam_papers'
    pdf_file = f"{exam_folder}/{exam_name}.pdf"
    capture_screenshots(pdf_file, exam_name)

    # for exam in exam_names:
    #     pdf_file = f"{exam_folder}/{exam}.pdf"
    #     # print(pdf_file)
    #     capture_screenshots(pdf_file, exam)
    #     # print(f'Screenshots captured for {exam}')

# TODO: MULTIPLE CHOICE SECTION DETECTION - RECOGNISE NUMBERS ON LEFT HAND SIDE? RECOGNISE BOLD FONTS?
