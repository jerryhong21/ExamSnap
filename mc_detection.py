import fitz  # PyMuPDF
import json
import re
from question_class import QuestionClass

# Function to check is the string is a multiple choice option
def is_an_option(str):
    # Regular expression pattern to match the specified conditions
    pattern = r'^[a-dA-D]|^[a-dA-D]\)|[a-dA-D]\)'

    # Check if the string matches the pattern
    return bool(re.match(pattern, str))


def old_extract_number_from_string(input_string):
    # Use regular expression to find all numbers in the string
    numbers = re.findall(r'\d+', input_string)

    # If there are numbers, return the first one (assuming it's in the middle)
    if numbers:
        # Assuming the number is in the middle
        return int(numbers[len(numbers) // 2])
    else:
        return None  # Return None if no numbers were found
    
def extract_number_from_string(input_string):
    # Use regular expression to find the first number in the string
    match = re.search(r'\b(\d+)\b', input_string)
    
    if match:
        return int(match.group(1))
    else:
        return None  # Return None if no number was found


def get_left_text(page):
    text_array = []
    data = page.get_text("dict")
    # print(data['blocks'])
    counter = 0
    for block in data['blocks']:
        counter = counter + 1
        if 'lines' not in block:
            continue
        for line in block['lines']:
            if 'spans' not in line:
                continue
            for span in line['spans']:
                if 'text' not in span:
                    continue
                bbox = span['bbox']
                left_margin = 97
                if bbox[0] <= left_margin:
                    text_array.append(span['text'])

    return text_array

# notes:
# multiple choice questions are NOT always in bold
# print out all the elements on left 100 margin?


# pdf_file = "2020-hsc-biology.pdf"
# pdf_file = "2019_Exam_Choice.pdf"
# pdf_file = "James Ruse 2020 Physics Prelim Yearly & Solutions.pdf"
# doc = fitz.open(pdf_file)

# page = doc[5]
# left_text = get_left_text(page)
# filtered_left_text = [
#     element for element in left_text if re.search(r'\d', element)]
# print(filtered_left_text)
# for str in filtered_left_text:
#     number = extract_number_from_string(str)
#     if number == question_number_to_search
    # if number is what we are looking for, then set its question class

# print(page.get_text())
# print(page.get_text("dict"))


# def extract_question_int(str):


# class QuestionClass:
#     def __init__(self, page_number, question_number, x0, y0, x1, y1):
#         self.page_number = page_number
#         self.question_number = question_number
#         self.x0 = x0
#         self.y0 = y0
#         self.x1 = x1
#         self.y1 = y1


def get_mc_x0y0(str, page):
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
                if span['text'] == str:
                    bbox = span['bbox']
                    # returns x and y position of element from top of page
                    if bbox[0] <= 97:
                        return [bbox[0], bbox[1]]

    # if the return bbox = [0,0] then the pattern has not been detected and should therefore be rejected
    return [0, 0]

# everytime, access questions_mapped and look for the questionNumberToSearch


def find_mc_questions(doc, questions_mapped):
    question_number_to_search = 1

    for page_number, page in enumerate(doc):
        page_text = page.get_text()
        # if (page_number == 1):
        #     print(page_text)
        default_width = page.rect.width
        default_height = page.rect.height
        # get all the text on the left side of prefered margin and store

        left_text = get_left_text(page)
        filtered_left_text = [
            element for element in left_text if re.search(r'\d', element)]
        # print(left_text)
        for str in filtered_left_text:
            if question_number_to_search == 21:
                return questions_mapped
            if (is_an_option(str)):
                continue
            number = extract_number_from_string(str)
            if number != question_number_to_search:
                continue

            # get dimensions for question
            bbox = get_mc_x0y0(str, page)
            if (bbox == [0, 0]):
                print(f"Nothing found for string: '{str}'")
                continue
            # create multiple choice question class
            new_question = QuestionClass(
                page_number, number, bbox[0], bbox[1], default_width, default_height)
            questions_mapped.append(new_question)
            question_number_to_search += 1

    # INSERT FUNCTION TO FILTER OUT EVERY THAT ISN'T MULTIPLE CHOICE (in the case that there are less than 20 MCs in the paper)

    return questions_mapped