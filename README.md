# django-social-networking

# Running the Django Application with Docker

Follow these steps to build and run the Django application using Docker.

## Prerequisites

- Docker installed on your machine
- Postman (for testing the APIs)

## Steps

1.**Download or clone the repository**
      gh repo clone Nutan4518/django-social-networking
2.**navigate to the project directory**
      cd django-social-networking
3.**Build the Docker Image**
      docker build -t app .
      
4.**Run the Docker Container**
      docker run -p 8000:8000 app
   
5.**Test the APIs with Postman**
      Open Postman.
      Import the shared Postman collection.
      Test the APIs as defined in the collection.

 
   
