# Testify API

This is a Flask-based API that generates multiple-choice questions and provides endpoints to manage and retrieve the questions. The questions are generated using OpenAI's GPT-3 language model.

## Setup

1. Clone the repository:

```bash
git clone <repository-url>
```

2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Create a .env file in the root directory and add the following environment
   variables:

```
OPENAI_API_KEY=<your-openai-api-key>
MONGO_URI=<your-mongodb-uri>
JWT_SECRET_KEY=<your-jwt-secret-key>
USERNAME=<your-username>
PASSWORD=<your-password>
```

4. Start the Flask server:

```bash
python app.py
```

5. The API will be accessible at http://localhost:5000.

### Endpoints

- `POST /login`: Authenticate and obtain an access token.

- `GET /protected`: Protected endpoint that requires authentication.

- `POST /questions`: Add a multiple-choice question to the database.

- `GET /questions`: Get a collection of all questions in the database.

- `GET /questions/<question_id>`: Get a question by its ID.

- `DELETE /questions/<question_id>`: Delete a question by its ID.

- `DELETE /questions/denied`: Delete all questions with the "denied" status.

- `PUT /questions/<question_id>`: Update the status of a
  question by its ID.

### Usage

1. Authenticate by sending a POST request to `/login` with the following JSON
   payload:

```json
{
  "username": "<your-username>",
  "password": "<your-password>"
}
```

The response will contain an access token that you can use for protected
endpoints.

2. Use the obtained access token in the Authorization header for protected
   endpoints:

```bash
GET /protected
Authorization: Bearer <access-token>
```

3. Add a multiple-choice question by sending a POST request to `/questions` with
   the following JSON payload:

```json
{
  "tag": "<question-tag>",
  "level": "<question-level>"
}
```

The API will generate the question and store it in the database.

4. Retrieve all questions by sending a GET request to `/questions`.

5. Retrieve a specific question by sending a GET request to
   `/questions/<question_id>`.

6. Delete a question by sending a DELETE request to `/questions/<question_id>`.

7. Delete all questions with the "denied" status by sending a DELETE request to
   `/questions/denied`.

8. Update the status of a question by sending a PUT request to
   `/questions/<question_id> with the following JSON payload. You can
   set the states to "approved" or "denied".

```json
{
  "status": "<denied||approved>"
}
```
