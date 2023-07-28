
# Imports

import os
import openai

# OpenAI API usage and the generate_mult_choice function

openai.api_key = os.environ.get('OPENAI_API_KEY')

def generate_true_false(tag, level): 

    prompt = (
  
        "Generate one true or false question with an answer. This question should be a " + 
        "Duolingo English Language question at the {} level and should be in relation to this topic: {}. "

    ).format(level, tag)

    completion = openai.ChatCompletion.create(

        model="gpt-4-0613",
        messages=[
            {"role": "system", "content": 

            "You are a bot that exclusively generates true or false questions in this format:\n" +
            "Q: The earth is a sphere \n\nA: True\n" + 
            "Q: An elephant can fly \n\nA: False",
            
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.75
    )

    return completion.choices[0].message.content

def generate_mult_choice(tag, level): 

    prompt = (

        "Generate one multiple-choice-question with 4 options and the answer. "
        "This question should be a CEFR certified English Language Exam question at the {} level and should be in relation to this topic: {}. "

    ).format(level, tag)

    completion = openai.ChatCompletion.create(

        model="gpt-4-0613",
        messages=[
            {"role": "system", "content": 

            "You are a bot that exclusively generates multiple choice questions in this format:\n" +
            "Q: How do you ask for coffee in English?\n\nA) Can I have a coffee?\nB) Can I a coffee have?\nC) Have I a coffee can?\nD) A coffee can I?\n\nA: A) Can I have a coffee?\n" +
            "Q: What is the purpose of a rearview mirror in a car?\n\nA) To adjust the temperature inside the car.\nB) To display the current speed of the car.\nC) To reflect the view of the road behind the car.\nD) To control the audio system of the car.\n\nA: C) To reflect the view of the road behind the car."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.75
    )

    return completion.choices[0].message.content

# Optimized

