# MovieConnect Backend

## Overview
This README outlines the structure and operational details of our Django-based API and its related services, including Django Rest Framework, Postgres, Nginx, and Docker.

## Services and Configuration

### Backend Framework
- Django: Chosen for its robustness and flexibility in building backend applications.

### API Framework
- Django Rest Framework: Integrated with Django to provide a powerful toolkit for building Web APIs. The API operates on port 8000 and is containerized for both        development and production environments.

### Web Server
- Gunicorn: Employed as the Web Server Gateway Interface (WSGI) to serve the Django application, enhancing performance over Django's built-in server.

### Database
- Postgres: Utilizes port 5432 and runs in a dedicated Docker container. Data persistence is managed via Docker Volumes.
- Development Database Access: Use `psql -h db -d mcdatabase_dev -U mcuser` to interact with the development database.
    - Common PSQL Commands:
    - `\dt`: Display database tables.
    - `\l`: List all databases.
    - `\c`: Switch databases.
    - `\q`: Quit the PSQL shell.
    - `select * from <model>`: Fetch all instances of a model.

### Reverse Proxy Server
- Nginx: Handles incoming requests and routes them to the appropriate backend service. Supports SSL for HTTPS in production with certificates from Let's Encrypt. Nginx listens on port 8080 and proxies requests to Django or serves static files as needed.

### Containerization
- Docker: Provides isolated environments for each service (API server, Postgres, Nginx, etc.). Docker Compose orchestrates the container setup and management.
    - Docker Commands:
        - `docker-compose up -d`: Start containers in detached mode.
        - `docker-compose build`, `docker-compose up -d --build`: Rebuild containers.
        - `docker-compose stop`: Stop running containers.
        - `docker-compose down`: Remove containers.
        - `docker-compose down -v`: Remove containers and volumes.
        - `docker ps`: List active containers.
        - `docker exec -it <container_name_or_id> /bin/bash`: Access container shell.
        - `exit`: Leave container shell.

## API Usage

### User Authentication
The API leverages simplejwt for secure, token-based user authentication. Tokens are not persisted in the database, ensuring a high level of security and performance.

### Workflow
1. User Creation: The React frontend sends POST requests to `/api/user/signup/` for new user registrations, redirecting to the login page upon success.
2. User Login: To sign in, POST requests are sent to `/api/token/`, automatically storing the obtained token in HttpOnly cookies via the backend.
3. Token Refresh: Tokens have a configurable lifespan and must be refreshed via `/api/token/refresh/` when expired. The process mirrors initial token acquisition.

## API Endpoints for Frontend Integration
This section offers a detailed guide for frontend React developers on interacting with our Django backend API endpoints. It's crucial to note that authentication tokens (JWT) are managed via HttpOnly cookies to enhance security. This means the tokens are stored securely by the browser and cannot be accessed directly by JavaScript, offering protection against XSS attacks.

### User Management

#### Register New User
- Endpoint: `/api/user/signup/`
- Method: POST
- Expects: unique username, unique email, password, age (YYYY-MM-DD)
- Purpose: Registers a new user in the system. The request should include necessary user details, such as username and password.
- Response: Returns the newly created user's details on success with a 201 Created status. On failure (e.g., missing required fields or duplicate username), it returns error details with a 400 Bad Request status.

#### User Profile
- Endpoint: `/api/user/profile/`
- Method: GET
- Expects: userCredentials
- Purpose: Just for testing authentication
- Response: Returns the authenticated user's username

### Authentication and Token Management

#### Obtain Token (Login)
- Endpoint: `/api/token/`
- Method: POST
- Expects: username and password
- Purpose: Authenticates a user based on provided credentials (username and password) and sets JWT access tokens in HttpOnly cookies.
- Response: Upon successful authentication, sets an HttpOnly cookie with the JWT access token and returns a refresh token in the response body. On authentication failure, returns a 401 Unauthorized status.

#### Refresh Token
- Endpoint: `/api/token/refresh/`
- Method: POST
- Expects: Refresh token 
- Purpose: Refreshes the JWT access token using the refresh token, automatically managing this through the HttpOnly cookie without direct frontend intervention.
- Response: Updates the access token in the HttpOnly cookie. If the refresh process fails (e.g., refresh token is expired), returns a 401 Unauthorized status.

#### Logout
- Endpoint: `/api/user/logout/`
- Method: POST
- Expects: userCredentials
- Purpose: Logs out the current user by clearing the HttpOnly cookie containing the JWT access token. This endpoint requires the user to be authenticated but does not need any request body.
- Response: Returns a success message indicating the user has been logged out, and the access token cookie is cleared.

### Guidelines for Frontend Developers
- HttpOnly Cookie Management: Since JWTs are stored in HttpOnly cookies, the frontend does not directly handle token storage or transmission. The browser automatically includes these tokens in requests to the backend.
- Handling Authentication: For endpoints requiring authentication, ensure your API calls are made with the proper credentials and cookies enabled. If an API call returns a 401 Unauthorized status, initiate a token refresh or redirect the user to the login page as appropriate.
- Secure Communication: Always use HTTPS for production deployments to prevent the interception of requests and to ensure the security of data in transit.
