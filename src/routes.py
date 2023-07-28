
# IMPORTS

from flask import request, jsonify, send_from_directory, ObjectId
from src.settings import app, myclient, tf_col, mc_col
from src.openai_api import generate_mult_choice, generate_true_false
import os
import yaml

# ROUTES


# /.well-known/ai-plugin.json

@app.route('/.well-known/ai-plugin.json')
def serve_manifest():
    return send_from_directory(os.path.dirname(__file__), 'ai-plugin.json') # Directory likely needs fixing.


# /openapi.yaml

@app.route('/openapi.yaml')
def serve_openapi_yaml():
    with open(os.path.join(os.path.dirname(__file__), 'openapi.yaml'), 'r') as f: # Again.
        yaml_data = f.read()
    yaml_data = yaml.load(yaml_data, Loader=yaml.FullLoader)
    return jsonify(yaml_data)


# /logo.png

@app.route('/logo.png')
def serve_logo():
    return send_from_directory(os.path.dirname(__file__), 'logo.png', mimetype='image/png') # And again. 


# /questions

@app.route('/questions', methods=['POST'])
def add_question():
    data = request.json
    tag = data['tag']
    level = data['level']
    number = data['number']  # New JSON argument for the number of questions
    qType = data['qType']

    if not tag or not level or not number:
        return {'error': 'Invalid input data'}

    questions_added = 0

    if qType == 'true_or_false':
        while questions_added < number:
            prompt_list = []
            ready = False

            while not ready:
                prompt_list = generate_true_false(tag, level).split("\n\n")  # Assuming run_generation is defined elsewhere
                if len(prompt_list) == 2:
                    ready = True

            question = prompt_list[0][3:]
            answer = prompt_list[1][3:].lower() == 'true'  # Assuming the answer is a boolean (True/False)

            question_data = {
                'tag': tag,
                'level': level,
                'question': question,
                'answer': answer,
                'status': "pending",
                'revised': False
            }

            try:
                tf_col.insert_one(question_data)
                questions_added += 1
            except Exception as e:
                return jsonify({'error': str(e)}), 404

        return jsonify({'message': f'{questions_added} questions added successfully'}), 200
    elif qType == 'multiple_choice':
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
                mc_col.insert_one(question_data)
                questions_added += 1
            except Exception as e:
                return jsonify({'error': str(e)}), 404
        return jsonify({'message': f'{number} questions added successfully'}), 200
    else:
        return jsonify({'message': 'Please specify what type of question again'}), 200
    

# GET /questions/<string:qType>
     
@app.route('/questions/<string:qType>', methods=['GET'])
def get_questions(qType):
    questions = []

    if qType == 'true_or_false':
        for question in tf_col.find():
            questions.append({
                'id': str(question['_id']),
                'tag': question['tag'],
                'level': question['level'],
                'question': question['question'],
                'answer': question['answer'],
                'status': question['status'],
                'revised': question['revised']
            })
        return jsonify({'questions': questions}), 200
    
    elif qType == 'multiple_choice':
        for question in mc_col.find():
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
    
    else:
        return jsonify({'message': 'Please specify what type of question again'}), 200
    

# /tags/<string:qType>

@app.route('/tags/<string:qType>', methods=['GET'])
def get_tags(qType):
    if qType == "true_or_false": 
        try: 
            tags = tf_col.distinct("tag")
            return jsonify(", ".join(tags)), 200  # Join the tags using a comma and space
        except Exception as e:
            return jsonify("Error retrieving tags."), 400
        
    elif qType == "multiple_choice":
        try: 
            tags = mc_col.distinct("tag")
            return jsonify(", ".join(tags)), 200  # Join the tags using a comma and space
        except Exception as e:
            return jsonify("Error retrieving tags."), 400
        
    else:
        return jsonify({'message': 'Please specify what type of question again'}), 200


# POST /questions/id
# This getter is a POST to maximize number of ids possible to get. Maybe this
# isn't necessary and I can just turn it to a parameter

@app.route('/questions/id', methods=['POST'])
def get_questions_by_ids():
    data = request.json
    question_ids = data['question_ids']

    if not question_ids:
        return jsonify({'message': 'No question IDs provided.'}), 400

    tf_questions = tf_col.find({'_id': {'$in': [ObjectId(q_id) for q_id in question_ids]}})
    mc_questions = mc_col.find({'_id': {'$in': [ObjectId(q_id) for q_id in question_ids]}})


    tf_result = []
    for question in tf_questions:
        tf_result.append({
            'id': str(question['_id']),
            'tag': question['tag'],
            'level': question['level'],
            'question': question['question'],
            'choices': question['choices'],
            'answer': question['answer'],
            'status': question['status'],
            'revised': question['revised']
        })

    mc_result = []
    for question in mc_questions:
        mc_result.append({
            'id': str(question['_id']),
            'tag': question['tag'],
            'level': question['level'],
            'question': question['question'],
            'choices': question['choices'],
            'answer': question['answer'],
            'status': question['status'],
            'revised': question['revised']
        })



    if mc_result or tf_result:
        return jsonify(mc_result + tf_result), 200
    else:
        return jsonify({'message': 'No questions found.'}), 404


 # GET  /questions/tag/<string:tag>/<string:qType>

@app.route('/questions/tag/<string:tag>/<string:qType>', methods=['GET'])
def get_questions_by_tag(tag, qType):
    if tag is None:
        return jsonify({'message': 'Tag parameter is missing.'}), 400
    

    if qType == 'true_or_false':
        questions = list(tf_col.find({"tag": tag}))

        if not questions:
            return jsonify({'message': 'No questions found with the specified tag.'}), 404

        formatted_questions = []
        for question in questions:
            formatted_question = {
                'id': str(question['_id']),
                'tag': question['tag'],
                'level': question['level'],
                'question': question['question'],
                'choices': question['choices'],
                'answer': question['answer'],
                'status': question['status'],
                'revised': question['revised']
            }
            formatted_questions.append(formatted_question)

        return jsonify({'questions': formatted_questions}), 200
    elif qType == 'multiple_choice':
        questions = list(mc_col.find({"tag": tag}))

        if not questions:
            return jsonify({'message': 'No questions found with the specified tag.'}), 404

        formatted_questions = []
        for question in questions:
            formatted_question = {
                'id': str(question['_id']),
                'tag': question['tag'],
                'level': question['level'],
                'question': question['question'],
                'answer': question['answer'],
                'status': question['status'],
                'revised': question['revised']
            }
            formatted_questions.append(formatted_question)

        return jsonify({'questions': formatted_questions}), 200
    else:
        return jsonify({'message': 'Please specify what type of question again'}), 200


# PUT /questions/id/

@app.route('/questions/id/', methods=['PUT'])
def update_questions_by_ids():
    data = request.json
    status = data['status']
    question_ids = data['question_ids']

    updated_count = 0

    for question_id in question_ids:
        if tf_col.find_one({'_id': ObjectId(question_id)}):
            tf_col.update_one(
                {'_id': ObjectId(question_id)}, 
                {'$set': {'status': status, 
                          'revised': True}}
            )
            updated_count += 1
        elif mc_col.find_one({'_id': ObjectId(question_id)}):
            mc_col.update_one(
                {'_id': ObjectId(question_id)}, 
                {'$set': {'status': status, 
                          'revised': True}}
            )
            updated_count += 1

    if updated_count > 0:
        return jsonify({'message': f'{updated_count} question(s) updated successfully.'}), 200
    else:
        return jsonify({'message': 'No questions found.'}), 404



# PUT  /questions/tag/

@app.route('/questions/tag/', methods=['PUT'])
def put_questions_by_tag(tag):
    data = request.json
    tag = data['tag']
    qType = data['qType']
    status = data['status']

    if tag is None:
        return jsonify({'message': 'Tag parameter is missing.'}), 400
    

    if qType == 'true_or_false':
        questions = list(tf_col.find({"tag": tag}))

        if not questions:
            return jsonify({'message': 'No questions found with the specified tag.'}), 404

        for question in questions:
                tf_col.update_one(
                {'_id': ObjectId(question["_id"])}, 
                {'$set': {'status': status, 
                          'revised': True}}
            )

        return jsonify({'message': "Set all questions!"}), 200
    elif qType == 'multiple_choice':
        questions = list(mc_col.find({"tag": tag}))
        if not questions:
            return jsonify({'message': 'No questions found with the specified tag.'}), 404

        for question in questions:
                mc_col.update_one(
                {'_id': ObjectId(question["_id"])}, 
                {'$set': {'status': status, 
                          'revised': True}}
            )

        return jsonify({'message': "Set all questions!"}), 200
    else:
        return jsonify({'message': 'Please specify what type of question again'}), 200

# PUT  /questions

@app.route('/questions', methods=['PUT'])
def put_questions_by_tag():
    data = request.json
    qType = data['qType']
    status = data['status']

    if qType == 'true_or_false':
        questions = list(tf_col.find())

        if not questions:
            return jsonify({'message': 'No questions found'}), 404

        for question in questions:
                tf_col.update_one(
                {'_id': ObjectId(question["_id"])}, 
                {'$set': {'status': status, 
                          'revised': True}}
            )

        return jsonify({'message': "Set all questions!"}), 200
    
    elif qType == 'multiple_choice':
        questions = list(mc_col.find())

        if not questions:
            return jsonify({'message': 'No questions found'}), 404

        for question in questions:
                mc_col.update_one(
                {'_id': ObjectId(question["_id"])}, 
                {'$set': {'status': status, 
                          'revised': True}}
            )

        return jsonify({'message': "Set all questions!"}), 200
    else:
        return jsonify({'message': 'Please specify what type of question again'}), 200

