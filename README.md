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

# Quiz API Documentation

This API allows users to interact with a database of quiz questions. It supports various operations such as adding, updating, retrieving, and deleting questions. Each question is characterized by a tag, a level, a type, and a status. The questions are either multiple choice or true or false. They can be approved or denied based on their content. 

## Endpoints

### 1. Add Questions
- **Endpoint:** `/questions`
- **Function:** `add_questions`
- **Method:** `POST`
- **Parameters:** None
- **Request body:**
```json
{
    "tag": "string",
    "level": "string",
    "number": "int",
    "qType": "string"  // Either "true_or_false" or "multiple choice"
}
```
- **Usage:** Add questions of a certain type, tag, level, and number to the database.

---

### 2. Update All Questions
- **Endpoint:** `/questions`
- **Function:** `update_all_questions`
- **Method:** `PUT`
- **Parameters:** None
- **Request body:**
```json
{
    "qType": "string",  // Either "true_or_false" or "multiple choice"
    "status": "string"  // Either "approved" or "denied"
}
```
- **Usage:** Update the status of all questions of a certain type.

---

### 3. Delete All Questions
- **Endpoint:** `/questions`
- **Function:** `delete_all_questions`
- **Method:** `DELETE`
- **Parameters:** None
- **Request body:**
```json
{
    "qType": "string"  // Either "true_or_false" or "multiple choice"
}
```
- **Usage:** Delete all questions of a certain type from the database.

---

### 4. Get All Questions
- **Endpoint:** `/questions/{qType}`
- **Function:** `get_all_questions`
- **Method:** `GET`
- **Parameters:** qType
- **Request body:** None
- **Usage:** Retrieve all questions of a certain type from the database.

---

### 5. Get Tags
- **Endpoint:** `/tags/{qType}`
- **Function:** `get_tags`
- **Method:** `GET`
- **Parameters:** qType
- **Request body:** None
- **Usage:** Retrieve all tags for questions of a certain type.

---

### 6. Get Questions By IDs
- **Endpoint:** `/questions/id`
- **Function:** `get_questions_by_ids`
- **Method:** `POST`
- **Parameters:** None
- **Request body:** 
```json
{
    "question_ids": ["array of strings"]
}
```
- **Usage:** Retrieve specific questions using their IDs.

---

### 7. Update Questions By IDs
- **Endpoint:** `/questions/id`
- **Function:** `update_questions_by_ids`
- **Method:** `PUT`
- **Parameters:** None
- **Request body:** 
```json
{
    "status": "string",  // Either "approved" or "denied"
    "question_ids": ["array of strings"]
}
```
- **Usage:** Update the status of specific questions using their IDs.

---

### 8. Delete Questions By IDs
- **Endpoint:** `/questions/id`
- **Function:** `delete_questions_by_ids`
- **Method:** `DELETE`
- **Parameters:** None
- **Request body:** 
```json
{
    "question_ids": ["array of strings"]
}
```
- **Usage:** Delete specific questions using their IDs.

---

### 9. Get Questions By Tag and Type
- **Endpoint:** `/questions/tag/{tag}/{qType}`
- **Function:** `get_questions_by_tag_and_type`
- **Method:** `GET`
- **Parameters:** tag, qType
- **Request body:** None
- **Usage:** Retrieve questions of a certain tag and type.

---

### 10. Update Questions By Tag
- **Endpoint:** `/questions/tag`
- **Function:** `update_questions_by_tag`
- **Method:** `PUT`
- **Parameters:** None
- **Request body:**
```json
{
    "tag": "string",
    "status": "string",  // Either "approved" or "denied"
    "qType": "string"  // Either "true_or_false" or "multiple choice"
}
```
- **Usage:** Update the status of questions with a certain tag.

---

### 11. Delete Questions By Tag
- **Endpoint:** `/questions/tag`
- **Function:** `delete_questions_by_tag`
- **Method:** `DELETE`
- **Parameters:** None
- **Request body:**
```json
{
    "tag": "string",
    "qType": "string"  // Either "true_or_false" or "multiple choice"
}
```
- **Usage:** Delete all questions with a certain tag.

---

## Note

- MC: Multiple Choice Questions
- TF: True or False Questions

Each operation is designed to work with both types of questions. Different operations might require different information to be provided in the request body. The request body should be a valid JSON object.

