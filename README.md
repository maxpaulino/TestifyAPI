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
- `POST /questions - Generates` a question and adds it to the MongoDB database.
- `GET /questions - Retrieves` all the questions from the MongoDB database.
- `GET /questions/<question_id>` - Retrieves a question by its ID.
- `DELETE /questions/<question_id>` - Deletes a question by its ID.
- `DELETE /questions/denied` - Deletes all questions with the 'denied' status.
- `PUT /questions/<question_id>` - Updates the status and revision of a question by its ID.
