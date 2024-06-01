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
      
      [ACCUKNOX_assignment.postman_collection.json](https://interstellar-spaceship-1619.postman.co/workspace/New-Team-Workspace~5a2a28e7-403e-4c71-83fa-213ea5e59697/collection/28968127-42c6b510-3360-4fd7-bc60-2fe6fd559d34?action=share&creator=28968127&active-environment=28968127-8b6d89b5-8715-4a3f-bf5c-aa83e42950d9)

 
   
