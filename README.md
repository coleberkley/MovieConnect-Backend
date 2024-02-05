# MovieConnect Backend

## Developer Notes

### Django
Python Django is our chosen backend framework. 

### Django Rest Framework
Django Rest Framework is our API framework. It works inside our broader Django backend framework.
This API will listen on port 8000 and run inside a docker container in development and production.
We will use Green Unicorn (Gunicorn) instead of Django's basic Web Server Gateway Interface to run our API on port 8000.

### Postgres
The Postgres server will listen on port 5432 and run inside its own docker container.
Database data will be stored in a Docker Volume. This is a type of in-house database maintenance, using Docker.
To shell into PSQL (Postgres interactive shell) to see models in development database run
'psql -h db -d mcdatabase_dev -U mcuser' from the Postgres server's docker container's shell
Other shell commands:
'\dt' show database tables
'\l' list databases
'\c' change database
'\q' quit psql
'select * from <model in db>' select all instances of a model

### Nginx
Nginx is the reverse proxy server that will handle all incoming requests from the external world and route the requests into our backend services.
Our Nginx server will support SSL certificates for HTTPS (in production), and we will generate free SSL certs using Let's Encrypt's certbot.
The Nginx server will run in a docker container on port 8080 and proxy requests to either port 8000 (Django) or a static folder location for static files.

### Docker
Docker containers are isolated runtime environments for software to run inside of.
We will have a Docker container for each of the following: API server, Postgres server, Nginx proxy server, TorchServe Model API
We will use Docker Compose to automatically orchestrate the build and purpose of each container. See the docker-compose.yml file.

To run Docker containers in detatched mode (and build if never built before) run 'docker-compose up -d'
To rebuild containers run 'docker-compose build' or 'docker-compose up -d --build'
To stop containers run 'docker-compose stop'
To stop and remove containers run 'docker-compose down'
To remove containers and volumes run 'docker-compose down -v'
To see all running containers run 'docker ps'
To shell into a specific container run 'docker exec -it <container_name_or_id> /bin/bash'
To exit shell run 'exit'

## Using the API

### User Authentication

This API uses with simplejwt JSON Web Tokens for authenticating requests.
These tokens are production-level, as they are not stored in our database, have customizable expiration times, and are completely unique per creation. 
The frontend will basically request for a new token when logging in a user and will store this token in the frontend for usage. 
The token will be stored in the browser cookies and will automatically be included in the authorization header per http request. 
If a token expires, the frontend will request to refresh it. 

#### User Creation
Our React frontend will send POST requests to .../api/user/signup/ when creating a user for the first time and will then be sent to a login page.
User creation will not directly work with obtaining or refreshing tokens. 

#### Signing in a User
React will send POST requests to .../api/token/ to obtain a new token. This token will be automatically stored in the browser's HttpOnly cookies, as
this is an HTTP field included in the response which is configured from the backend. The frontend shouldn't have to directly work with storing or accessing the tokens at all. 
Once a proper POST request is sent to /api/token/, every request from that browser session onwards should automatically be verified.

### Refreshing tokens
Depending on our chosen refresh timer, eventually tokens will expire if a User is still signed into a browser with such token for over the expiration limit.
A token becomes invalid once expired, so the frontend should send a proper refresh request to /api/token/refresh/ to refresh its token. 
The token should automatically refresh and return in HttpOnly cookies just like when obtaining a new token. 

