# Set base image (host OS)
FROM python:3.8-slim-buster

# Copy the content of the project directory to the working directory
COPY . /app

# Set the working directory in the container
WORKDIR /app

# Install any dependencies
RUN pip3 install -r requirements.txt

# Specify the Flask environment port
ENV PORT 5000

# By default, listen on port 80
EXPOSE 5000

# Set the directive to specify the executable that will run when the container is initiated
ENTRYPOINT [ "python3" ]

# Specify the command to run on container start
CMD [ "main.py" ]
