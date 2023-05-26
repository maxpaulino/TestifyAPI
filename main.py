# Imports

import os
import openai
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import datetime
from bson import ObjectId
from dotenv import load_dotenv

# This code initializes a Flask application and configures a MongoDB database URI
# using PyMongo library. The API key for OpenAI API is also declared and
# initialized for future use. Lastly it also loads the environment variables from
# the .env file.

# load_dotenv()


openai.api_key = os.environ.get('OPENAI_API_KEY')

app = Flask(__name__)
app.config['MONGO_URI'] = f"mongodb+srv://maxpaulino:{os.environ.get('MONGO_PASSWORD')}@testify.mgathan.mongodb.net/Questions?retryWrites=true&w=majority"
mongo = PyMongo(app)

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=1)  
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
jwt = JWTManager(app)

def_username = os.environ.get('USERNAME')
def_password = os.environ.get('PASSWORD')

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

# This is a Flask route for user login authentication. The code receives a POST
# request with username and password data in JSON format. If the credentials
# are invalid, a 401 error is returned, otherwise, an access token is created
# and returned with a 200 success status code.

@app.route('/login', methods=['POST'])
def login():

    username = request.json.get('username')
    password = request.json.get('password')

    if username != def_username or password != def_password:
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=username)

    return jsonify({'access_token': access_token}), 200

# This code defines a Flask route for an endpoint that is protected with JWT authentication. 
# The endpoint returns a JSON response containing a message and the current user's 
# identity.

@app.route('/protected', methods=['GET'])
@jwt_required()  
def protected():

    current_user = get_jwt_identity()

    return jsonify({'message': 'Protected endpoint', 'user': current_user}), 200

# This function is a Flask route that handles the addition of a multiple choice
# question to a MongoDB database. It accepts a JSON request containing the tag
# and level of the question and calls the `generate_mult_choice` function to
# generate the question, choices, and answer. The generated data is then used
# to create a dictionary representing the question and inserted into the 
# "Questions" collection using PyMongo. Finally, a success message is returned 
# as a JSON response.

@app.route('/questions', methods=['POST'])
@jwt_required() 
def add_question():

    data = request.json
    tag = data['tag']
    level = data['level']

    if not tag or not level:
        return {'error': 'Invalid input data'}

    prompt_list = []

    ready = False

    while ready == False:
        prompt_list = generate_mult_choice(tag,level).split('\n\n')
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

    questions_collection = mongo.db.mc_questions
    try:
        questions_collection.insert_one(question_data)
    except Exception as e:
        return {'error': str(e)}

    return {'message': 'Question added successfully'}

# This is a Flask route function that handles a GET request for a collection of
# questions from a MongoDB database. The function creates a list of dictionaries
# containing the relevant fields for each question and returns it as a JSON 
# object. 

@app.route('/questions', methods=['GET'])
@jwt_required()  
def get_questions():

    questions_collection = mongo.db.mc_questions
    questions = []

    for question in questions_collection.find():
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

    return {'questions': questions}

# This function takes in a `question_id` parameter in the URL and attempts to
# retrieve the corresponding question from the MongoDB database. If found, the
# question data is returned in a JSON format similar to the original 
# `get_questions` handler. If the question is not found, a 404 error message is 
# returned instead.

@app.route('/questions/<question_id>', methods=['GET'])
@jwt_required()  
def get_question_by_id(question_id):

    questions_collection = mongo.db.mc_questions
    question = questions_collection.find_one({'_id': ObjectId(question_id)})
    
    if question:
        return {
            'id': str(question['_id']),
            'tag': question['tag'],
            'level': question['level'],
            'question': question['question'],
            'choices': question['choices'],
            'answer': question['answer'],
            'status': question['status'],
            'revised': question['revised']
        }
    else:
        return {'message': 'Question not found.'}, 404

# This function deletes a question from the MongoDB database by its ID.
# It takes in a question_id parameter and uses it to query the questions 
# collection in the database. If the question is found and successfully deleted, 
# it returns a JSON object with the message "Question deleted successfully". If 
# the question is not found, it returns a JSON object with the message 
# "Question not found" and a 404 status code.

@app.route('/questions/<question_id>', methods=['DELETE'])
@jwt_required()  
def delete_question_by_id(question_id):

    questions_collection = mongo.db.mc_questions
    result = questions_collection.delete_one({'_id': ObjectId(question_id)})

    if result.deleted_count > 0:
        return {'message': 'Question deleted successfully.'}
    else:
        return {'message': 'Question not found.'}, 404

# This function is a Flask route that accepts DELETE requests at the endpoint 
# '/questions/denied'. It first accesses the 'questions' collection in the 
# MongoDB database using the PyMongo library. Then, it deletes all documents 
# from the 'questions' collection having the 'status' field set to 'denied', and 
# returns a JSON object containing a message indicating the number of documents 
# matching the query that were deleted.

@app.route('/questions/denied', methods=['DELETE'])
@jwt_required() 
def delete_denied_questions():

    questions_collection = mongo.db.mc_questions
    result = questions_collection.delete_many({'status': 'denied'})

    return {'message': f'{result.deleted_count} questions with status "denied" deleted successfully.'}

# This code defines a Flask route that handles PUT requests to update a question
# in a MongoDB database. The route first retrieves the question with the given
# ID from the database, then updates its "status" and "revised" fields based
# on the query parameters provided in the request. If the question is found and
# updated, the route returns a success message with a 200 status code. If the
# question is not found, it returns a "not found" message with a 404 status code. 
# Overall, this code provides a RESTful endpoint for updating question data.

@app.route('/questions/<question_id>', methods=['PUT'])
@jwt_required()  
def update_question_by_id(question_id):

    questions_collection = mongo.db.mc_questions
    question = questions_collection.find_one({'_id': ObjectId(question_id)})

    if question:
        data = request.json
        status = data['status']
        revised = True

        questions_collection.update_one(
            {'_id': ObjectId(question_id)}, 
            {'$set': {'status': status, 
                      'revised': revised}}
        )
        return {'message': 'Question updated successfully.'}, 200
    else:
        return {'message': 'Question not found.'}, 404

# Main function

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
