# django-social-networking

# Running the Django Application with Docker

Follow these steps to build and run the Django application using Docker.

## Prerequisites

- Docker installed on your machine
- Postman (for testing the APIs)

## Steps

1. **Build the Docker Image**

   Open a terminal and navigate to the project directory. Run the following command to build the Docker image:

   ```bash
   docker build -t app .
2. **Run the Docker Container**
   docker run -p 8000:8000 app
   
4. **Test the APIs with Postman**
  Open Postman.
  Import the shared Postman collection.
  Test the APIs as defined in the collection.
