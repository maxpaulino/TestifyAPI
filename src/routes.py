
# Imports

from flask import request, jsonify, send_from_directory
from src.settings import app, myclient, mycol
from src.openai_api import generate_mult_choice
import os
import yaml

# Flask routes

@app.route('/.well-known/ai-plugin.json')
def serve_manifest():
    return send_from_directory(os.path.dirname(__file__), 'ai-plugin.json') # Directory likely needs fixing.


@app.route('/openapi.yaml')
def serve_openapi_yaml():
    with open(os.path.join(os.path.dirname(__file__), 'openapi.yaml'), 'r') as f: # Again.
        yaml_data = f.read()
    yaml_data = yaml.load(yaml_data, Loader=yaml.FullLoader)
    return jsonify(yaml_data)

@app.route('/logo.png')
def serve_logo():
    return send_from_directory(os.path.dirname(__file__), 'logo.png', mimetype='image/png') # And again. 

@app.route('/questions', methods=['POST'])
def add_question():
    data = request.json
    tag = data['tag']
    level = data['level']
    number = data['number']  # New JSON argument for the number of questions
    questionType = data['type'] 

    if not tag or not level or not number:
        return {'error': 'Invalid input data'}

    questions_added = 0

    if questionType == 'true_or_false':


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
    elif questionType == 'multiple_choice':
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


@app.route('/questions', methods=['GET'])
def get_questions():
    # The content of the function is omitted for brevity
    pass

@app.route('/questions/tag', methods=['POST'])
def get_questions_by_tag():
    # The content of the function is omitted for brevity
    pass

@app.route('/questions/id', methods=['POST'])
def get_questions_by_ids():
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
