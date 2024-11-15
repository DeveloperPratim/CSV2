import csv
import requests
import re


def download_file(url, local_filename):
    # Send a GET request to the URL
    with requests.get(url, stream=True) as response:
        # Raise an exception if the request was unsuccessful
        response.raise_for_status()
        
        # Open the local file in write-binary mode
        with open(local_filename, 'wb') as f:
            # Download the file in chunks and write to the local file
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
    print(f"File downloaded and saved as {local_filename}")

# Example usage:
url = 'https://sses.freewebhostmost.com/records.csv'  # Replace with the file URL
local_filename = 'records.csv'  # The path where you want to save the file

download_file(url, local_filename)



# Constants
API_KEY = 'AIzaSyC2wd6WisuKrJsWqto4dHuyKRmY7X5eTVc'  # Replace with your actual API key
URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent'

def create_prompt(id, chapter, subtopic, question, answer):
    return f"""
    {{
      "id": "{id}",
      "Chapter": "{chapter}",
      "Subtopic": "{subtopic}",
      "Question": "{question}",
      "Answer": "{answer}",

      "Evaluation": {{
        "Corrected Question": "<Corrected Question Text>",
        "Corrected Answer": "<Corrected Answer Text>",
        "Detailed Answer": "<Full, Corrected Answer Text>",

        "Feedback": {{
          "Strengths": "<Positive Aspects of the Answer>",
          "Areas for Improvement": "<Things to Improve in the Answer>",
          "Issues": "<Identified Problems>"
        }},

        "Overall Comment": "<Comment on the Overall Answer>",
        "Errors": ["<Error 1>", "<Error 2>", "<Error 3>"],
        "Relevance to Question": "<Relevance Percentage>",
        "Answer Length": {{
          "Word Count": "<Word Count>",
          "Character Count": "<Character Count>"
        }},

        "Scores": {{
          "Correctness": "<Correctness Percentage>",
          "Meaningfulness": "<Meaningfulness Percentage>",
          "Grading Feedback": "<Grading Comment>",
          "Grade": "<Grade Percentage, 0 for wrong answer>",
          "Accuracy": "<Accuracy Percentage>",
          "Confidence Level": "<Confidence Level Percentage>",
          "Semantic Similarity": "<Semantic Similarity Percentage , 0 for wrong answer>",
          "Conceptual Accuracy": "<Conceptual Accuracy Percentage>",
          "Contextual Relevance": "<Contextual Relevance Percentage , 0 for wrong answer>",
          "Syntax": "<Syntax Correctness Percentage>",
          "Grammar": "<Grammar Score Percentage>",
          "Clarity": "<Clarity Score Percentage>",
          "Depth": "<Depth of Explanation Score Percentage>",
          "Precision": "<Precision Score Percentage>",
          "Recall": "<Recall Score Percentage>",
          "Quality Score": "<Overall Quality Score Percentage>",
          "Answer Structure": "<Structure Quality Score Percentage>",
          "External References": "<Reference Accuracy Percentage>",
          "Topic Coherence": "<Topic Coherence Percentage>",
          "Citation Quality": "<Citation Quality Percentage>",
          "Relevance Score": "<Relevance Score Percentage>"
        }},

        "Predicted Grade": "<Predicted Grade>",
        "Student Engagement": "<Student Engagement Score Percentage>",
        "Marks": {{
          "Maximum Marks": "<Maximum Marks>",
          "Marks Obtained": "<Obtained Marks , 0 for wrong answer or not relevant or incorrect>",
          "Obtained Percentage": "<Obtained Percentage>"
        }},

        "Rectification Needed": "<Yes/No>",
        "Error List": ["<Error 1>", "<Error 2>", "<Error 3>"],
        "Additional Comments": "<Any Additional Comments>"
      }}
    }}
    """


# Function to get the response from the Gemini API
def get_gemini_answer(prompt):
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    response = requests.post(URL, headers=headers, params={'key': API_KEY}, json=data)
    if response.status_code == 200:
        response_json = response.json()
        return response_json['candidates'][0]['content']['parts'][0]['text']
    return f"Error {response.status_code}: {response.text}"


# Function to write the parsed response to a CSV file
def write_to_csv(parsed_data):
    # Define CSV file path and fieldnames
    csv_file = 'gemini_responses2.csv'
    fieldnames = [
        'myid', 'id', 'subtopic', 'question', 'answer', 'table_html', 'source', 'timestamp', 'title', 
        'chapter', 'corrected_question', 'corrected_answer', 'detailed_answer', 'strengths', 'areas_for_improvement',
        'issues', 'overall_comment', 'errors', 'relevance_to_question', 'grading_feedback', 'accuracy', 'confidence_level',
        'semantic_similarity', 'conceptual_accuracy', 'contextual_relevance', 'syntax', 'grammar', 'clarity', 'depth',
        'precision', 'recall', 'quality_score', 'answer_structure', 'external_references', 'topic_coherence', 
        'citation_quality', 'relevance_score', 'maximum_marks', 'marks_obtained', 'obtained_percentage', 'rectification_needed',
        'additional_comments'
    ]

    # Open the CSV file and write the data
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write the header only if the file is empty
        if file.tell() == 0:
            writer.writeheader()

        # Write the parsed data
        writer.writerow(parsed_data)


def parse_response(gemini_response, row):
    def extract_field(regex, text, default=None):
        match = re.search(regex, text)
        return match.group(1) if match else default

    # Extract fields from Gemini response
    chapter = extract_field(r'"Chapter": "([^"]+)"', gemini_response)
    corrected_question = extract_field(r'"Corrected Question": "([^"]+)"', gemini_response)
    corrected_answer = extract_field(r'"Corrected Answer": "([^"]+)"', gemini_response)
    detailed_answer = extract_field(r'"Detailed Answer": "([^"]+)"', gemini_response)
    strengths = extract_field(r'"Strengths": "([^"]+)"', gemini_response)
    areas_for_improvement = extract_field(r'"Areas for Improvement": "([^"]+)"', gemini_response)
    issues = extract_field(r'"Issues": "([^"]+)"', gemini_response)
    overall_comment = extract_field(r'"Overall Comment": "([^"]+)"', gemini_response)

    # Check if Errors field exists and is not empty
    errors_match = re.search(r'"Errors": \[([^\]]+)\]', gemini_response)
    errors = [err.strip().strip('"') for err in errors_match.group(1).split(',')] if errors_match else []

    relevance_to_question = extract_field(r'"Relevance to Question": "([^"]+)"', gemini_response)

    # Extract additional fields
    grading_feedback = extract_field(r'"Grading Feedback": "([^"]+)"', gemini_response)
    accuracy = extract_field(r'"Accuracy": "([^"]+)"', gemini_response)
    confidence_level = extract_field(r'"Confidence Level": "([^"]+)"', gemini_response)
    semantic_similarity = extract_field(r'"Semantic Similarity": "([^"]+)"', gemini_response)
    conceptual_accuracy = extract_field(r'"Conceptual Accuracy": "([^"]+)"', gemini_response)
    contextual_relevance = extract_field(r'"Contextual Relevance": "([^"]+)"', gemini_response)
    syntax = extract_field(r'"Syntax": "([^"]+)"', gemini_response)
    grammar = extract_field(r'"Grammar": "([^"]+)"', gemini_response)
    clarity = extract_field(r'"Clarity": "([^"]+)"', gemini_response)
    depth = extract_field(r'"Depth": "([^"]+)"', gemini_response)
    precision = extract_field(r'"Precision": "([^"]+)"', gemini_response)
    recall = extract_field(r'"Recall": "([^"]+)"', gemini_response)
    quality_score = extract_field(r'"Quality Score": "([^"]+)"', gemini_response)
    answer_structure = extract_field(r'"Answer Structure": "([^"]+)"', gemini_response)
    external_references = extract_field(r'"External References": "([^"]+)"', gemini_response)
    topic_coherence = extract_field(r'"Topic Coherence": "([^"]+)"', gemini_response)
    citation_quality = extract_field(r'"Citation Quality": "([^"]+)"', gemini_response)
    relevance_score = extract_field(r'"Relevance Score": "([^"]+)"', gemini_response)

    # Additional fields
    maximum_marks = extract_field(r'"Maximum Marks": "([^"]+)"', gemini_response)
    marks_obtained = extract_field(r'"Marks Obtained": "([^"]+)"', gemini_response)
    obtained_percentage = extract_field(r'"Obtained Percentage": "([^"]+)"', gemini_response)
    rectification_needed = extract_field(r'"Rectification Needed": "([^"]+)"', gemini_response)
    additional_comments = extract_field(r'"Additional Comments": "([^"]+)"', gemini_response)

    # Construct the result dictionary
    return {
        'chapter': chapter, 'subtopic': row['subtopic'], 'question': row['question'], 'answer': row['answer'],
        'corrected_question': corrected_question, 'corrected_answer': corrected_answer, 'detailed_answer': detailed_answer,
        'strengths': strengths, 'areas_for_improvement': areas_for_improvement, 'issues': issues, 'overall_comment': overall_comment,
        'errors': ', '.join(errors), 'relevance_to_question': relevance_to_question, 'grading_feedback': grading_feedback,
        'accuracy': accuracy, 'confidence_level': confidence_level, 'semantic_similarity': semantic_similarity,
        'conceptual_accuracy': conceptual_accuracy, 'contextual_relevance': contextual_relevance, 'syntax': syntax,
        'grammar': grammar, 'clarity': clarity, 'depth': depth, 'precision': precision, 'recall': recall, 'quality_score': quality_score,
        'answer_structure': answer_structure, 'external_references': external_references, 'topic_coherence': topic_coherence,
        'citation_quality': citation_quality, 'relevance_score': relevance_score, 'maximum_marks': maximum_marks, 
        'marks_obtained': marks_obtained, 'obtained_percentage': obtained_percentage, 'rectification_needed': rectification_needed,
        'additional_comments': additional_comments, 'myid': row['myid'], 'id': row['id'], 'subtopic': row['subtopic'], 
        'question': row['question'], 'answer': row['answer'], 'table_html': row['table_html'], 'source': row['source'], 
        'timestamp': row['timestamp'], 'title': row['title']
    }


# Read from records.csv and process each row
# Read from records.csv and process each row starting from 200th
with open('records.csv', mode='r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    start_from = 400  # Start from the 200th record
    current_record = 0  # Counter to track record position

    for row in reader:
        current_record += 1

        # Skip until the 200th record
        if current_record < start_from:
            continue

        id = row['myid']
        chapter = "Operating System"
        subtopic = row['subtopic']
        question = row['question']
        answer = row['answer']
        table_html = row['table_html']
        source = row['source']
        timestamp = row['timestamp']
        title = row['title']

        # Generate prompt and get Gemini response
        prompt = create_prompt(id, chapter, subtopic, question, answer)
        gemini_response = get_gemini_answer(prompt)

        # Parse the response and write to CSV
        parsed_data = parse_response(gemini_response, row)
        write_to_csv(parsed_data)

        print(f"Processed record {current_record}: {question}")

