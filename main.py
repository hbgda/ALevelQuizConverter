import os
import re
import json

from string import ascii_uppercase
from typing import Tuple

convert_path = "./convert"
output_path = "./output"
max_answers = 4

class Question:

    question: str
    answers: list[str]
    correct_answer: int

    def __init__(self, question, answers = [], correct_answer = 1):
        self.question = question
        self.answers = answers
        self.correct_answer = correct_answer


def save_to_json(questions: list[Question], filename):
    arr = []

    # Create json-like object for each question, so they can be saved to file.
    for question in questions:
        x = {
            "question": question.question,
            "answers": question.answers,
            "correct_answer": question.correct_answer
        }
        arr.append(x)

    # Save to file.
    with open(f"{output_path}/json/{filename}.json", "w") as handler:
        json.dump(arr, handler)
    
    

def save_to_csv(questions: list[Question], filename):
    csv_string = "Question,"

    # Dynamically create options string based on max_answers.
    options_string = ",".join([f"Option {x+1}" for x in range(max_answers)])
    csv_string += f"{options_string},Correct Answer\n"

    # Create a new string for each question that will be appended to csv_string.
    for question in questions:
        append_str = f"{question.question},{','.join(question.answers)},{question.correct_answer}\n"
        csv_string += append_str

    # Save to file.
    with open(f"{output_path}/csv/{filename}.csv", "w") as handler:
        handler.write(csv_string)


def format_data(questions, answers, error_check = 3) -> Tuple[list[str], list[str]]:
    answers = answers.replace("Answers\n", "").replace("Question Number\nAnswer", "").split()
    answers = [[int(x), y] for x,y in zip(answers[0::2], answers[1::2])]

    highest = 0

    corrected_questions = []
    for question in questions:
        x = question.split("\n")

        # Check for questions that don't match the format, this can be from questions using pictures or custom format options.
        if x[0][0].islower() or len(x[0].split(" ")) < error_check or len(x[1: ]) < 2:
            print(f"Skipping [{questions.index(question)}] due to potentially invalid format.\nData: [{', '.join(x)}]\n")
            continue
        
        # Check the highest recorded amount of answers, this is important due to Quizizz csv formatting.
        if len(x[1:]) > highest:
            highest = len(x[1:])
        
        corrected_questions.append(x)

    global max_answers
    max_answers = highest

    for index in range(len(corrected_questions)):
        q = corrected_questions[index]
        while len(q)-1 < highest:
            q.append("")
        corrected_questions[index] = q

    return (corrected_questions, answers)


def create_questions(questions, answers) -> list[Question]:
    converted_questions = []

    # Iterate through formatted questions and use the data to create objects.
    for index in range(len(questions)):
        q = questions[index]
        a = answers[index][1]

        q_converted = Question(q[0], q[1: ], ascii_uppercase.index(a) + 1)
        converted_questions.append(q_converted)

    return converted_questions
    

# Iterate through files within the specific convert_path and convert each.
for file in os.listdir(convert_path):

    print(f"Converting [{file}]")

    file_txt = open(f"{convert_path}/{file}", encoding="utf-8").read()
    # Create an array of strings containing question+answer data to later format.
    split = re.split("\\n\\n+", file_txt)
    
    # Answers are stored at the end of the file, this retrieves them from the end of the array.
    answers = split[-1]
    
    # Title and answer data is included with the question data, this is to remove that.
    questions = split[1 : -1]
    questions[0] = questions[0].replace("Quiz\n", "")

    # Format data.
    questions, answers = format_data(questions, answers)
    print(f"Formatted {len(questions)} questions.")
    print(f"Max answers: {max_answers}")
    
    # Create Question objects from data.
    converted_questions = create_questions(questions, answers)
    
    # Check for needed paths.
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    if not os.path.exists(f"{output_path}/json"):
        os.mkdir(f"{output_path}/json")

    if not os.path.exists(f"{output_path}/csv"):
        os.mkdir(f"{output_path}/csv")

    # Save questions to relevant formats.
    save_to_csv(converted_questions, file)
    save_to_json(converted_questions, file)

print("\n\n\n\nCONVERTED FILES ARE NOT GUARANTEED TO BE ACCURATE OR COMPLETE\nPLEASE REVIEW CONVERTED FILES BEFORE USE!\n\n\n\n")

    
