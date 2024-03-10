import fitz  # PyMuPDF
import cv2
import numpy as np
import re
import os
import glob
from question_detection import find_all_questions


def capture_screenshots(pdf_file, exam_name):
    doc = fitz.open(pdf_file)
    # print(pdf_file)

    questions_mapped = find_all_questions(doc)
    # print('Finsiehd finding q')
    # for question in questions_mapped:
    #     print(question.question_number)
    # perhaps we need to first SORT questions into order, in case the algorithm has detected a question before another
    # search for sorting algoritms in python
    set_lower_bounds(questions_mapped)
    # print('Finsiehd setting lower bounds')

    # loop through all questions in question array and capture screenshots
    for question in questions_mapped:
        print("Mapping", question.question_number)
        if question.x0 == 0 and question.y0 == 0:
            continue
        page_number = question.page_number
        page = doc[page_number]

        # PROGRAM IS CONSTANTLY STUCK ON THIS LINE
        pix = page.get_pixmap()

        # print('accessed3')

        # capture screenshot in a pix array
        screenshot = np.frombuffer(
            pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        # PNG file that goes to a folder named after exam
        folder_name = 'output_images'
        exam_dir = f"./{folder_name}/{exam_name}"
        if not os.path.exists(exam_dir):
            os.makedirs(exam_dir)
        png_file = f"./{folder_name}/{exam_name}/{exam_name}_Q{int_question_number(question.question_number)}_P{question.page_number}.png"
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
def int_question_number(question_num_str):
    if isinstance(question_num_str, int):
        return question_num_str
    elif 'Question' in question_num_str or 'question' in question_num_str or 'QUESTION':
        parts = question_num_str.split()
        clean_question_num_str = extract_first_number(parts[-1])
        if clean_question_num_str != None:
            return int(clean_question_num_str)

    # if 0 is returned then error as occured
    print(f"An error occured while converting '{question_num_str}' to integer")
    return 0


# This function assumes the questions array passed in is in order
def set_lower_bounds(questions):
    for i in range(len(questions) - 2):
        curr = questions[i]
        next = questions[i + 1]
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


def extract_first_number(s):

    # Find all instances of one or more digits in the string
    numbers = re.findall(r'\d+', s)

    # If there's at least one match, return the first. Otherwise, return None.
    return numbers[0] if numbers else None


def clean_questions(questions):
    # Iterate in reverse
    for i in range(len(questions) - 1, -1, -1):
        width = questions[i].x1 - questions[i].x0
        width_threshold = 100
        if (width < width_threshold):
            questions.pop(i)
            
    return questions

# TODO: MULTIPLE CHOICE SECTION DETECTION - RECOGNISE NUMBERS ON LEFT HAND SIDE? RECOGNISE BOLD FONTS?
