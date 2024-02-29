
# ExamSnap: A PDF Exam Imaging Tool

ExamSnap is a powerful tool designed to streamline the process of converting individual questions from exam papers in PDF format into screenshots. This process is essential for creating a database of past exam questions, which can be mapped to relevant syllabus points, allowing for thorough analysis of question trends. Although optimized for HSC exams, ExamSnap maintains around 90% effectiveness with other exam papers.

## Getting Started

### Installation

1. Clone the repository to your preferred folder using the following command:
    ```bash
    git clone <repository-url>
    ```

### Usage

ExamSnap offers two modes for processing exam papers:

#### Mode 1: Individual Exam Papers

This mode is designed for screenshotting individual exam papers.

- Drag the exam paper into the `exam_papers` folder.
- Run the script with the command:
    ```bash
    python3 image_paper.py
    ```
- Follow the prompts and enter the exact file name of your exam paper (including the file extension, e.g., `.pdf`).
- Screenshots will be saved in the `output_images` folder.

#### Mode 2: Bulk Exam Papers

For processing multiple exam papers in bulk:

- Drag the folder containing your exam papers into the `exam_folders` folder.
- Run the script with the command:
    ```bash
    python3 image_folder.py
    ```
- Follow the prompts and enter the exact name of your exam folder.
- Screenshots will be captured and saved in the `output_images` folder.

### Note

For the best results, ensure your PDF files are named accurately and are of good quality. The effectiveness of the tool may vary based on the format and layout of the exam papers.

---

*ExamSnap is an evolving tool, and we welcome feedback and contributions to improve its accuracy and usability.*
