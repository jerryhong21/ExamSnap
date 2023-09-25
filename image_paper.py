from capture_screenshots import capture_screenshots
import os
import glob

exam_folder = "exam_papers"
exam_name = input("Enter the name of exam file you'd like to image: ")
pdf_file = f"{exam_folder}/{exam_name}.pdf"
capture_screenshots(pdf_file, exam_name)
print("Screenshots captured for", exam_name)