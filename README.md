# English Language Exam Question Generator

This application generates English Language Exam questions based on given topics and CEFR language level. The generated questions are in multiple-choice format. The questions are generated using the OpenAI GPT-3 model.

The application is developed in Python using Flask, MongoDB, PyMongo, and OpenAI's GPT-3 model. It is Dockerized for easy setup and deployment.

### Features

- Generation of multiple-choice English Language Exam questions.
- Questions can be added and retrieved from the MongoDB database.
- Questions can be updated and deleted based on their ID.
- All questions with the 'denied' status can be deleted at once.

### Installation

Since the application is dockerized, the installation process is very straightforward.

First, clone the repository:

```bash
git clone https://github.com/maxpaulino/TestifyChat.git
cd project
```

Then, build the Docker image:

```bash
docker build -t english-question-generator .
```

And run the application:

```bash
docker run -p 5000:5000 english-question-generator
```

The application will be available at `http://localhost:5000`.

### Environment Variables

The application uses the following environment variables:

- `OPENAI_API_KEY` - Your OpenAI API key.
- `MONGO_PASSWORD` - The password for your MongoDB database.

These variables should be set in your environment or in a .env file.

### API Endpoints

- `GET /.well-known/ai-plugin.json` - Serves the AI plugin JSON file.
- `GET /.well-known/openapi.yaml` - Serves the OpenAPI YAML file.
- `POST /questions` - Generates a question and adds it to the MongoDB database.
- `GET /questions` - Retrieves all the questions from the MongoDB database.
- `GET /questions/<question_id>` - Retrieves a question by its ID.
- `DELETE /questions/<question_id>` - Deletes a question by its ID.
- `DELETE /questions/denied` - Deletes all questions with the 'denied' status.
- `PUT /questions/<question_id>` - Updates the status and revision of a question by its ID.



1. 
Endpoint: /.well-known/ai-plugin.json
Function: serve_manifest
Methods: GET
Parameters: None
Request body used: No

2. 
Endpoint: /openapi.yaml
Function: serve_openapi_yaml
Methods: GET
Parameters: None
Request body used: No

3. 
Endpoint: /logo.png
Function: serve_logo
Methods: GET
Parameters: None
Request body used: No

4.
Endpoint: /questions
Function: add_questions
Methods: POST
Parameters: None
Request body: 
{
    tag: "string"
    level: "string" 
    number: "int"
    qType: "string" (Either true_or_false or multiple choice)
}

5. 
Endpoint: /questions
Function: update_all_questions
Methods: PUT
Parameters: None
Request body:
{
    qType: "string" (Either true_or_false or multiple choice)
    status: "status" (Either approved or denied)
}

6. 
Endpoint: /questions
Function: delete_all_questions
Methods: DELETE
Parameters: None
Request body:
{
    qType: "string" (Either true_or_false or multiple choice)
}

7.
Endpoint: /questions/{qType}
Function: get_all_questions
Methods: GET
Parameters: qType
Request body: None

8.
Endpoint: /tags/{qType}
Function: get_tags
Methods: GET
Parameters: qType
Request body: None

9. 
Endpoint: /questions/id
Function: get_questions_by_ids
Methods: POST
Parameters: None
Request body: 
{
    question_ids: "array of strings"
}

10. 
Endpoint: /questions/id
Function: update_questions_by_ids
Methods: PUT
Parameters: None
Request body: 
{
    status: "string" (Either approved or denied)
    question_ids: "array of strings"
}

11.
Endpoint: /questions/id
Function: delete_questions_by_ids
Methods: DELETE
Parameters: None
Request body: 
{
    question_ids: "array of strings"
}

12. 
Endpoint: /questions/tag/{tag}/{qType}
Function: 
Methods: GET
Parameters: tag, qType
Request body: None

13. 
Endpoint: /questions/tag
Function: update_questions_by_tag
Methods: PUT
Parameters: None
Request body:
{
    tag: "string"
    status: "status" (Either approved or denied)
    qType: "string" (Either true_or_false or multiple choice)

}

14. 
Endpoint: /questions/tag
Function: delete_questions_by_tag
Methods: DELETE
Parameters: None
Request body:
{
    tag: "string"
    qType: "string" (Either true_or_false or multiple choice)

}

