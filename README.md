# django-social-networking

# Running the Django Application with Docker

Follow these steps to build and run the Django application using Docker.

## Prerequisites

- Docker installed on your machine
- Postman (for testing the APIs)

## Steps

1.**Download or clone the repository**
2.**navigate to the project directory**
3.**open terminal in the same directory**
   Open a terminal and navigate to the project directory. Run the following command to build the Docker image:
4. **Build the Docker Image**
      docker build -t app .
      
5.**Run the Docker Container**
   docker run -p 8000:8000 app
   
6. **Test the APIs with Postman**
  Open Postman.
  Import the shared Postman collection.
  Test the APIs as defined in the collection.

   
