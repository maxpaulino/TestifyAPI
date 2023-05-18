# Imports
import os
import openai
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import datetime
from bson import ObjectId
from dotenv import load_dotenv

# This code initializes a Flask application and configures a MongoDB database
# URI using PyMongo library. The API key for OpenAI API is also declared and
# initialized for future use. Lastly it also loads the environment variables 
# from the .env file.
load_dotenv()
app = Flask(__name__)
openai.api_key = os.environ['OPENAI_API_KEY']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=1)  # Access token expiration time
app.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET_KEY']
app.config['MONGO_URI'] = os.environ['MONGO_URI']
mongo = PyMongo(app)
jwt = JWTManager(app)

# This is a Python function named `generate_mult_choice`. It takes in two 
# arguments: `tag` which represents a string topic, and `level` which is a string 
# representing the CEFR language level. The function generates a multiple-choice 
# question prompt based on the provided topic and language level using OpenAI's 
# GPT-3. The function returns the generated prompt as a string.
def generate_mult_choice(tag, level): 
    prompt = (
        "Generate a multiple-choice question with 4 options and the answer. "
        "This question should be a CEFR English Language Exam question at the {} level and should be in relation to this topic: {}. "
    ).format(level, tag)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": 
                # "Here are the CEFR Guidelines for each level: \n" +
                #     "A1 (Basic User): Can understand and use familiar everyday expressions and very basic phrases aimed at the satisfaction of needs of a concrete type. Can introduce him/herself and others and can ask and answer questions about personal details such as where he/she lives, people he/she knows and things he/she has. Can interact in a simple way provided the other person talks slowly and clearly and is prepared to help.\n" +
                #     "A2 (Basic User): Can understand sentences and frequently used expressions related to areas of most immediate relevance (e.g. very basic personal and family information, shopping, local geography, employment). Can communicate in simple and routine tasks requiring a simple and direct exchange of information on familiar and routine matters. Can describe in simple terms aspects of his/her background, immediate environment and matters in areas of immediate need.\n" +
                #     "B1 (Independent User): Can understand the main points of clear standard input on familiar matters regularly encountered in work, school, leisure, etc. Can deal with most situations likely to arise whilst travelling in an area where the language is spoken. Can produce simple connected text on topics which are familiar or of personal interest. Can describe experiences and events, dreams, hopes & ambitions and briefly give reasons and explanations for opinions and plans.\n" +
                #     "B2 (Independent User): Can understand the main ideas of complex text on both concrete and abstract topics, including technical discussions in his/her field of specialisation. Can interact with a degree of fluency and spontaneity that makes regular interaction with native speakers quite possible without strain for either party. Can produce clear, detailed text on a wide range of subjects and explain a viewpoint on a topical issue giving the advantages and disadvantages of various options.\n" +
                #     "C1 (Proficient User): Can understand a wide range of demanding, longer texts, and recognise implicit meaning. Can express him/ herself fluently and spontaneously without much obvious searching for expressions. Can use language flexibly and effectively for social, academic and professional purposes. Can produce clear, well-structured, detailed text on complex subjects, showing controlled use of organisational patterns, connectors and cohesive devices.\n" +
                #     "C2 (Proficient User): Can understand with ease virtually everything heard or read. Can summarise information from different spoken and written sources, reconstructing arguments and accounts in a coherent presentation. Can express him/herself spontaneously, very fluently and precisely, differentiating finer shades of meaning even in more complex situations.\n\n" +
                # "Don't mention the CEFR guidelines explicitly but keep them in mind when responding. " +
                # "You are a question generator. " +
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
    if username != 'admin' or password != 'password':
        return jsonify({'message': 'Invalid credentials'}), 401
    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200

# This code defines a Flask route for an endpoint that is protected with JWT authentication. 
# The endpoint returns a JSON response containing a message and the current user's 
# identity.
@app.route('/protected', methods=['GET'])
@jwt_required()  # Require valid access token for authentication
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
@jwt_required()  # Require valid access token for authentication
def add_question():
    data = request.json
    tag = data['tag']
    level = data['level']
    if not tag or not level:
        return {'error': 'Invalid input data'}
    prompt_list = []
    while len(prompt_list) != 3:
        while len(prompt_list[3]) == 4:
            prompt_list = generate_mult_choice(tag, level).split('\n\n')
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
        'status': "unchecked",
        'revised': False
    }
    questions_collection = mongo.db.questions
    try:
        questions_collection.insert_one(question_data)
    except Exception as e:
        return {'error': str(e)}
    return {'message': 'Question added successfully'}
# This is a Flask route function that handles a GET request for a collection of
# questions from a MongoDB database. The function creates a list of dictionaries
# containing the relevant fields for each question and returns it as a JSON 
# object. It is well-organized and employs good coding practices with clear variable
# naming and a simple for loop to iterate through the database records.
@app.route('/questions', methods=['GET'])
@jwt_required()  # Require valid access token for authentication
def get_questions():
    questions_collection = mongo.db.questions
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
@jwt_required()  # Require valid access token for authentication
def get_question_by_id(question_id):
    questions_collection = mongo.db.questions
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
@jwt_required()  # Require valid access token for authentication
def delete_question_by_id(question_id):
    questions_collection = mongo.db.questions
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
@jwt_required()  # Require valid access token for authentication
def delete_denied_questions():
    questions_collection = mongo.db.questions
    result = questions_collection.delete_many({'status': 'denied'})
    return {'message': f'{result.deleted_count} questions with status "denied" deleted successfully.'}

# This code defines a Flask route that handles PUT requests to update a question
# in a MongoDB database. The route first retrieves the question with the given
# ID from the database, then updates its "status" and "revised" fields based
# on the query parameters provided in the request. If the question is found and
# updated, the route returns a success message with a 200 status code. If the
# question is not found, it returns a "not found" message with a 404 status code. 
# Overall, this code provides a RESTful endpoint for updating question data
# in a backend system.
@app.route('/questions/<question_id>', methods=['PUT'])
@jwt_required()  # Require valid access token for authentication
def update_question_by_id(question_id):
    questions_collection = mongo.db.questions
    question = questions_collection.find_one({'_id': ObjectId(question_id)})
    if question:
        status = request.args.get('status')
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
    app.run(debug=True)

