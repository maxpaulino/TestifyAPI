# Imports

import os
import openai
import yaml
from flask import Flask, request, jsonify, send_from_directory 
from flask_pymongo import PyMongo
from bson import ObjectId
from flask_cors import CORS

# This code initializes a Flask application and configures a MongoDB database URI
# using PyMongo library. The API key for OpenAI API is also declared and
# initialized for future use. Lastly it also loads the environment variables from
# the .env file.

PORT = 5000

openai.api_key = os.environ.get('OPENAI_API_KEY')

app = Flask(__name__)
CORS(app, origins=[f"http://localhost:{PORT}", "https://chat.openai.com"])
app.config['MONGO_URI'] = f"mongodb+srv://maxipaulino:{os.environ.get('MONGO_PASSWORD')}@cluster0.ibeupug.mongodb.net/Testify?retryWrites=true&w=majority"
myclient = PyMongo(app)
mycol = myclient.db.Questions



# This is a Python function named `generate_mult_choice`. It takes in two 
# arguments: `tag` which represents a string topic, and `level` which is a string 
# representing the CEFR language level. The function generates a multiple-choice 
# question prompt based on the provided topic and language level using OpenAI's 
# GPT-3. The function returns the generated prompt as a string.

def generate_mult_choice(tag, level): 

    prompt = (

        "Generate a multiple-choice question with 4 options and the answer. "
        "This question should be a CEFR certified English Language Exam question at the {} level and should be in relation to this topic: {}. "

    ).format(level, tag)

    completion = openai.ChatCompletion.create(

        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": 

                "You are a bot that exclusively generates multiple-choice questions in this format:\n" + 
             "Q:\n\nA)\nB)\nC)\nD)\n\nA:"

             },
            {"role": "user", "content": prompt}
        ],
        temperature=0.75
    )

    return completion.choices[0].message.content

# This is a Flask route function that serves the 'ai-plugin.json' file located
# in the '.well-known' directory. The function uses the send_from_directory
# function to get the file from the directory and returns it in the response.

@app.route('/.well-known/ai-plugin.json')
def serve_manifest():
    return send_from_directory(os.path.dirname(__file__), 'ai-plugin.json')

# This is a Flask route handler that serves an OpenAPI specification file in
# YAML format. The file is read from the local directory, converted to a Python
# dictionary using the PyYAML library, and then returned as a JSON response
# using Flask's jsonify function.

@app.route('/openapi.yaml')
def serve_openapi_yaml():
    with open(os.path.join(os.path.dirname(__file__), 'openapi.yaml'), 'r') as f:
        yaml_data = f.read()
    yaml_data = yaml.load(yaml_data, Loader=yaml.FullLoader)
    return jsonify(yaml_data)

# This function serves the logo

@app.route('/logo.png')
def serve_logo():
    return send_from_directory(os.path.dirname(__file__), 'logo.png', mimetype='image/png')

# This function is a Flask route that handles the addition of a multiple choice
# question to a MongoDB database. It accepts a JSON request containing the tag
# and level of the question and calls the `generate_mult_choice` function to
# generate the question, choices, and answer. The generated data is then used
# to create a dictionary representing the question and inserted into the 
# "Questions" collection using PyMongo. Finally, a success message is returned 
# as a JSON response.

@app.route('/questions', methods=['POST'])
def add_question():
    data = request.json
    tag = data['tag']
    level = data['level']
    number = data['number']  # New JSON argument for the number of questions

    if not tag or not level or not number:
        return {'error': 'Invalid input data'}

    questions_added = 0

    while questions_added < number:
        prompt_list = []

        ready = False

        while ready == False:
            prompt_list = generate_mult_choice(tag, level).split('\n\n')
            if len(prompt_list) == 3:
                if len(prompt_list[2]) != 4:
                    ready = True

        question = prompt_list[0][3:]
        choices = prompt_list[1].split('\n')
        answer = prompt_list[2][3:]

        if answer.startswith('wer: '):
            answer = prompt_list[2][8:]

        question_data = {
            'tag': tag,
            'level': level,
            'question': question,
            'choices': choices,
            'answer': answer,
            'status': "pending",
            'revised': False
        }

        try:
            mycol.insert_one(question_data)
            questions_added += 1
        except Exception as e:
            return jsonify({'error': str(e)}), 404

    return jsonify({'message': f'{number} questions added successfully'}), 200




@app.route('/tags', methods=['GET'])
def get_tags():
    try: 
        tags = mycol.distinct("tag")
        return jsonify(", ".join(tags)), 200  # Join the tags using a comma and space
    except Exception as e:
        return jsonify("Error retrieving tags."), 400







# This is a Flask route function that handles a GET request for a collection of
# questions from a MongoDB database. The function creates a list of dictionaries
# containing the relevant fields for each question and returns it as a JSON 
# object. 

@app.route('/questions', methods=['GET'])
def get_questions():

    questions = []

    for question in mycol.find():
        questions.append({
            'id': str(question['_id']),
            'tag': question['tag'],
            'level': question['level'],
            'question': question['question'],
            'choices': question['choices'],
            'answer': question['answer'],
            'status': question['status'],
            'revised': question['revised']
        })

    return jsonify({'questions': questions}), 200

# This function takes in a `question_id` parameter in the URL and attempts to
# retrieve the corresponding question from the MongoDB database. If found, the
# question data is returned in a JSON format similar to the original 
# `get_questions` handler. If the question is not found, a 404 error message is 
# returned instead.


@app.route('/questions', methods=['GET'])
def get_question_by_id():
    question_ids = request.args.getlist('id')

    questions = mycol.find({'_id': {'$in': [ObjectId(q_id) for q_id in question_ids]}})
    
    if questions:
        result = []
        for question in questions:
            result.append({
                'id': str(question['_id']),
                'tag': question['tag'],
                'level': question['level'],
                'question': question['question'],
                'choices': question['choices'],
                'answer': question['answer'],
                'status': question['status'],
                'revised': question['revised']
            })
        return jsonify(result), 200
    else:
        return jsonify({'message': 'No questions found.'}), 404

# This function deletes a question from the MongoDB database by its ID.
# It takes in a question_id parameter and uses it to query the questions 
# collection in the database. If the question is found and successfully deleted, 
# it returns a JSON object with the message "Question deleted successfully". If 
# the question is not found, it returns a JSON object with the message 
# "Question not found" and a 404 status code.

@app.route('/questions/<question_id>', methods=['DELETE'])
def delete_question_by_id(question_id):

    result = mycol.delete_one({'_id': ObjectId(question_id)})

    if result.deleted_count > 0:
        return jsonify({'message': 'Question deleted successfully.'}), 200
    else:
        return jsonify({'message': 'Question not found.'}), 404

# This function is a Flask route that accepts DELETE requests at the endpoint 
# '/questions/denied'. It first accesses the 'questions' collection in the 
# MongoDB database using the PyMongo library. Then, it deletes all documents 
# from the 'questions' collection having the 'status' field set to 'denied', and 
# returns a JSON object containing a message indicating the number of documents 
# matching the query that were deleted.

@app.route('/questions/denied', methods=['DELETE'])
def delete_denied_questions():

    result = mycol.delete_many({'status': 'denied'})

    return jsonify({'message': f'{result.deleted_count} questions with status "denied" deleted successfully.'}), 200

# This code defines a Flask route that handles PUT requests to update a question
# in a MongoDB database. The route first retrieves the question with the given
# ID from the database, then updates its "status" and "revised" fields based
# on the query parameters provided in the request. If the question is found and
# updated, the route returns a success message with a 200 status code. If the
# question is not found, it returns a "not found" message with a 404 status code. 
# Overall, this code provides a RESTful endpoint for updating question data.

@app.route('/questions/<question_id>', methods=['PUT'])
def update_question_by_id(question_id):

    question = mycol.find_one({'_id': ObjectId(question_id)})

    if question:
        data = request.json
        status = data['status']
        revised = True

        mycol.update_one(
            {'_id': ObjectId(question_id)}, 
            {'$set': {'status': status, 
                      'revised': revised}}
        )
        return jsonify({'message': 'Question updated successfully.'}), 200
    else:
        return jsonify({'message': 'Question not found.'}), 404

# Main function

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
