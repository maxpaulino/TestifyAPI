
# Imports

import os
import openai

# OpenAI API usage and the generate_mult_choice function

openai.api_key = os.environ.get('OPENAI_API_KEY')

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

# Optimized

