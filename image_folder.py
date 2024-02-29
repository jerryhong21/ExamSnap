from capture_screenshots import capture_screenshots
import os
import glob


exam_folder = input("Enter the name of folder you'd like to input: ")
exams_dir = glob.glob(f'exam_folders/{exam_folder}/*.pdf')
for exam_dir in exams_dir:
    exam_name = os.path.splitext(os.path.basename(exam_dir))[0]
    print('Starting to image', exam_name)
    capture_screenshots(exam_dir, exam_name)
    print(f'Screenshots captured for {exam_name}')

