
# IMPORTS

from flask import request, jsonify, send_from_directory, ObjectId
from src.settings import app, myclient, mycol
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

@app.route('/questions/<string:qType>', methods=['POST'])
def add_question(qType):
    data = request.json
    tag = data['tag']
    level = data['level']
    number = data['number']  # New JSON argument for the number of questions

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
                mycol.insert_one(question_data)
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
                mycol.insert_one(question_data)
                questions_added += 1
            except Exception as e:
                return jsonify({'error': str(e)}), 404
        return jsonify({'message': f'{number} questions added successfully'}), 200
    else:
        return jsonify({'message': 'Please specify what type of question again'}), 200
    

# /questions/<string:qType>
     
@app.route('/questions/<string:qType>', methods=['GET'])
def get_questions(qType):
    questions = []

    if qType == 'true_or_false':
        for question in mycol.find():
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
    
    else:
        return jsonify({'message': 'Please specify what type of question again'}), 200
    

# /tags/<string:qType>

@app.route('/tags/<string:qType>', methods=['GET'])
def get_tags(qType):
    if qType == "true_or_false": 
        try: 
            tags = mycol.distinct("tag")
            return jsonify(", ".join(tags)), 200  # Join the tags using a comma and space
        except Exception as e:
            return jsonify("Error retrieving tags."), 400
        
    elif qType == "multiple_choice":
        try: 
            tags = mycol.distinct("tag")
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


@app.route('/questions/id', methods=['POST'])
def get_questions_by_ids():
    # The content of the function is omitted for brevity
    pass

@app.route('/questions/tag', methods=['POST'])
def get_questions_by_tag():
    # The content of the function is omitted for brevity
    pass



@app.route('/questions/id', methods=['DELETE'])
def delete_question_by_id():
    # The content of the function is omitted for brevity
    pass

@app.route('/questions/denied', methods=['DELETE'])
def delete_denied_questions():
    # The content of the function is omitted for brevity
    pass

@app.route('/questions/id', methods=['PUT'])
def update_questions_by_ids():
    # The content of the function is omitted for brevity
    pass
