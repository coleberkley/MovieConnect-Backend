# MovieConnect Backend

## Introduction
This README outlines everything about the MovieConnect backend. In essence, MovieConnect is both a movie-recommendation and social media platform which allows users to browse movies to watch and connect with other users. This repository contains all backend code for this application.

## Table of Contents
- Overview: High level description of the program and backend
- Expected Functionality: User Interface Functionality that this backend expects
- API Endpoints: Instructions on how to interact with this API
- Services and Configuration: Tech Stack, Design, Environment
- Set Up: Instructions on how to set up this backend on your local machine yourself.

## Overview
Finish later when backend is done

## Expected Functionality
Here I will explain the application functionality that this API expects to support.

Upon loading the application, a user is prompted to sign in. The user can switch to the sign up page if desired. If signing up, the user will provide a username, email, password, and birthdate. When clicking sign up, the user will automatically be signed in and returned to the home page. If signing in, the user will provide their username and password and will be redirected to the home page.

Upon viewing the home page, a user will see a list for each recommendation model we have. This could be anywhere from 1-3 lists depending on what is done. The user can click through each list, which can have a varying number of movies depending on the model and perhaps the user. From the home page, a user can click on a specific movie to view that movie and maybe rate or comment under it. A user can also logout, view their own profile, or search for a specific movie by title instead of finding one in the provided lists.

Upon viewing the user's profile, a user should be prompted with their information (username, email, maybe password, private status) and be able to edit this information. A user should also view their friends list in some way, and be able to remove any of those friends. A user should also have a list of incoming and outgoing friend requests. A user can deny or accept incoming friend requests, as well as cancel outgoing friend requests. A user may also see a list of movies they've already rated in their user profile. 

Users should be able to look up other users by username. If users are found, the current user should be able to click onto another user's profile and view it. If the viewed user is public or if the viewed user is friends with the current user, the current user can see the other user's rated movies list. The current user should be able to request a friendship with the viewed user if one hasn't been requested already (or they are already friends). Likewise, the current user should be able to unfriend the viewed user if they are friends.

Upon viewing a movie page, a user should see all relative information for that movie. This includes the title, genre(s), actor(s), director(s), runtime, adult status, poster, overview, release date, and overall rating. There should also be a comments section somewhere in this movie page that renders every comment for that movie. A user should be able to rate the movie if they haven't yet, or re-rate it if they have. Likewise, a user should be able to add comments to that movie's comment section. The page should refresh after these actions to retrieve the updated comment section and user rating. 


## API Endpoints 
This section details each endpoint of the MovieConnect API. 

### Related Code for Endpoints
- See mcbackend/urls.py and api/urls.py for url patterns
- See api/views.py for the functions each url pattern calls
- See api/serializers.py for the specifics of serialized JSON response data 
- See api/models.py for the database schema specifics

Remember to prepend `http://localhost:80` before each endpoint. 



### User Authentication

#### Register New User 
- Endpoint: `/api/user/signup/`
- Method: POST
- Purpose: Registers a new user in the system.
- Request Format: Provide a unique username, unique email, password, age (YYYY-MM-DD)
- Response Format: Returns successful 201 status and sets JWT access token in HTTPOnly cookies logging in the new user. If unsuccessful, returns a 400 status with specific error information. 

#### Login 
- Endpoint: `/api/token/`
- Method: POST
- Purpose: Authenticates a user based on provided credentials
- Request Format: Provide the user's username and password
- Response Format: Returns a successful 201 status and sets JWT token in response cookies logging in the user

#### Logout
- Endpoint: `/api/user/logout/`
- Method: POST
- Purpose: Logs out the current user by clearing the HttpOnly cookie containing the JWT access token. This endpoint requires the user to be authenticated but does not need any request body.
- Request Format: Provide user credentials (access token)
- Response Format: Returns a success message indicating the user has been logged out, and the access token cookie is cleared. 

#### Delete Account
- Endpoint: `/api/user/delete/`
- Method: DELETE
- Purpose: Deletes the signed in user's account and logs the user out
- Request Format: Provide user credentials (access token)
- Response Format: Returns a successful 204 status indicating the user has been deleted. We will remove the JWT cookie in the response like the Logout function does, so the user should be logged out upon deletion and routed to sign in/sign up. If user deletion somehow fails, it returns a 500 status. 



### User Profile Page

#### User Details
- Endpoint: `/api/user/profile/`
- Method: GET
- Purpose: Retrieves all user metadata for the signed in user. 
- Request Format: Provide user credentials (access token)
- Response Format: Returns a response body with fields: 'id', 'username', 'email', 'birth_date', 'is_private', 'bio'

#### Rated Movies
- Endpoint: `/api/user/movies/rated/`
- Method: GET
- Purpose: Retrieves all movies the signed in user has rated.
- Request Format: Provide user credentials (access token)
- Response Format: Returns a a list of movies in the response body. Each movie in the list has fields: 'id', 'title', 'poster_url', 'overview', 'release_date', 'runtime', 'adult', 'user_rating'
- Extra Notes: If the list is empty, the user has rated no movies. user_rating contains the signed-in user's rating for that movie.

#### Update Profile
- Endpoint: `/api/user/update/`
- Method: PUT
- Purpose: Updates the siged in user's profile. 
- Request Format: Provide user credentials (access token). Provide fields in the request body for any of the following to be updated: 'username', 'email', 'password', 'bio', 'is_private'. Any partial combination is supported, doesn't have to be all 4 fields.
- Response Format: 200 status if updated successfully or a 400 status if unsuccessful. 
- Extra Notes: The is_private should be a boolean. Up to you how to make this a frontend button. There can be a lot of reasons a 400 status is returned, like if the new email or username is already taken in the database. The response body should contain the corresponding type of error in a message. For simplicity we may just want to emit some 'unsuccessful' message on a 400 status response. 

#### Retrieve Friends List
- Endpoint: `/api/friends/`
- Method: GET
- Purpose: Retrieves the list of users the signed in user is friends with.
- Request Format: Provide user credentials (access token). 
- Response Format: Returns a list of users. Each user in the list has fields: 'id', 'username'
- Extra Notes: Prepare for empty lists as this signifies no friends. 

#### Remove a Friend
- Endpoint: `/api/user/remove-friend/<int:friend_id>/`
- Method: DELETE
- Purpose: Deletes the friendship object between two users. 
- Request Format: Provide user credentials (access token). The friend's id is provided in friend_id.
- Response Format: Returns 404 status for error and 204 status for successful deletion.
- Extra Notes: This requires the id of a FRIEND, not the id of the (accepted) request. Each friend's id is provided in the friends list.

#### Retrieve List of Incoming Requests
- Endpoint: `/api/friend-requests/incoming/`
- Method: GET
- Purpose: Retrieve all incoming friend requests for the signed in user.
- Request Format: Provide user credentials (access token)
- Response Format: A list of incoming requests is returned. Each request in the list contains fields: 'id', 'from_user', 'to_user', 'created_at', 'accepted'
- Extra Notes: id resembles the request id. from_user will be the sender username per request, and to_user will always be the signed in user's username. The only field that really matters for display purposes is the from_user username per request. 

#### Retrieve List of Outgoing Requests
- Endpoint: `/api/friend-requests/outgoing/`
- Method: GET
- Purpose: Retrieve all outgoing friend requests for the signed in user. 
- Request Format: Provide user credentials (access token)
- Response Format: A list of outgoing requests is returned. Each request in the list contains fields: 'id', 'from_user', 'to_user', 'created_at', 'accepted'
- Extra Notes: id resembles the request id. from_user will always be the signed in user, and to_user will be the recipient user of each request. The only field that really matters for display purposes is the to_user username per request. 

#### Accept or Deny Incoming Request
- Endpoint: `/api/friend-requests/update/<int:request_id>/`
- Method: POST, DELETE
- Purpose: Accept or deny an incoming request. Denying will delete the friend request object. 
- Request Format (POST): Provide user credentials (access token). The request's id is provided in request_id. 
- Response Format (POST): Returns 404 status if failed. Returns 200 status if request successfully accepted.
- Request Format (DELETE): Provide user credentials (access token). The request's id is provided in request_id. 
- Response Format (DELETE): Returns 404 status if failed. Returns 204 status if successfully deleted.
- Extra Notes: This requires the id of a REQUEST, not the id of the user who sent the request. The request id per incoming request is provided in the incoming requests list.

#### Cancel Outgoing Request
- Endpoint: `/api/friend-requests/cancel/<int:request_id>/`
- Method: DELETE
- Purpose: Cancels an outgoing request which will delete the friend request object. 
- Request Format: Provide user credentials (access token). The request's id is provided in request_id. 
- Response Format: Returns 204 status if successful, 404 if unsuccessful
- Extra Notes: This requires the id of a REQUEST, not the id of the user who sent the request. The request id per incoming request is provided in the incoming requests list.



### Movie Lists 

#### Get Recommendation List 
- Endpoint: `/api/user/movies/`
- Method: GET
- Expects: userCredentials
- Purpose: Returns a recommendation list of movies for the signed in user
- Model Type: Currently set to our simple SVD/cosine similarity model. In the middle of switching to more accurate SVD/XGBoost model. Both are collaborative models based on user ratings. 
- Request Format: Provide user credentials (access token)
- Response Format: Returns a list of recommended movies for that user. Each movie in the list will have fields: 'id', 'title', 'poster_url', 'overview', 'release_date', 'runtime', 'adult'
- Extra Notes: Model will only be called if the user has rated a certain number of movies. Else, we return a list of randomly picked movies from the database. 

#### Get Popular Movies List
- Endpoint: `/api/movies/popular/`
- Method: GET
- Expects: userCredentials
- Purpose: Returns the X most popular movies in our database based on average rating. X currently set to 10. 
- Request Format: Provide user credentials (access token)
- Response Format: Returns a list of popular movies. Each movie in the list will have fields: 'id', 'title', 'poster_url', 'overview', 'release_date', 'runtime', 'adult'
- Extra Notes: This list will return much faster than the recommendation list.

#### Get User's Watch List
- Endpoint: `/api/movies/watch/`
- Method: GET
- Expects: userCredentials
- Purpose: Returns the list of movies the user has added to their watch list. 
- Request Format: Provide user credentials (access token)
- Response Format: Returns a list of movies. Each movie in the list will have fields: 'id', 'title', 'poster_url', 'overview', 'release_date', 'runtime', 'adult'
- Extra Notes: This list can vary in length.



### Searching

#### Search for a User
- Endpoint: `/api/user/search/`
- Method: GET
- Purpose: Search for user(s) given a username
- Request Format: Provide user credentials (access token). Query params should contain the 'username' field. 
- Response Format: Returns a list of users that contain that username. Each user in the list has fields: 'id', 'username'
- Extra Notes: An example would be `/api/user/search?username=johndoe`. Prepare for empty lists as this will signify no results from the search. 

#### Search for a Movie
- Endpoint: `/api/movie/search/`
- Method: POST
- Purpose: Search for movie(s) given a title
- Request Format: Provide user credentials (access token). Query params should contain the 'title' field.
- Response Format: Provides a list of movies that match that title (Likely a list of 1 movie) with fields for each movie: 'id', 'title', 'poster_url', 'overview', 'release_date', 'runtime', 'adult'
- Extra Notes: An example POST request for title 'avengers' should look like `/api/movie/search?title=avengers`. Prepare for empty lists as this will signify no results from the search. 



### Movie Page

#### Get a Movie's Details
- Endpoint: `/api/movie/<int:pk>/`
- Method: GET
- Purpose: Retrieves the details of a movie given its id 
- Request Format: Provide user credentials (access token). The movie id is provided in the url.
- Response Format: Returns a response body with fields: 'id', 'title', 'poster_url', 'overview', 'runtime', 'adult', 'release_date', 'genres', 'actors', 'directors', 'average_rating', 'rated'
- Extra Notes: The 'rated' field will be 0 if the signed in user has not rated the movie yet. If the user has, the field will include the current user's rating for that movie (1-5). The genres, actors, and directors fields will each be a list of objects that each have a name field. The runtime is an integer in minutes. See models.py, views.py, and serializers.py for more info. 

#### Get a Movie's Comments
- Endpoint: `/api/movie/<int:pk>/comments/`
- Method: GET
- Purpose: Retrieves all comments for that movie given its movie id
- Request Format: Provide user credentials (access token). The movie id is provided in the url. 
- Response Format: Returns a list of all comments for that movie. Each comment contains the fields: 'id', 'body', 'timestamp', 'username'
- Extra Notes: Timestamp will likely have to be converted to something readable if it is used.

#### Get a Movie's Similar Movies List
- Endpoint: `/api/movie/<int:pk>/similar/`
- Method: GET
- Purpose: Retrieves the ten most similar movies for that movie given its movie id
- Request Format: Provide user credentials (access token). The movie id is provided in the url. 
- Response Format: Returns a list of movies where each movie in the list has fields: 'id', 'title', 'poster_url', 'overview', 'release_date', 'runtime', 'adult'
- Extra Notes: Pretty much the same response as other movie lists.

#### Rate a Movie
- Endpoint: `/api/movie/<int:pk>/rate/`
- Method: POST
- Purpose: Rate a movie given its id
- Request Format: Provide user credentials (access token). In the request body, provide a 'rating' field. The movie id is provided in the url. 
- Response Format: Returns 201 status if created, 200 status if updated, 400 status if failed. If 200 or 201 status, response will also have a body containing the data for that new rating if its needed.
- Extra Notes: Rating field will obviously hold the rating value. If the user has already rated this movie, we will update that rating instead of add a new one. 

#### Comment under a Movie
- Endpoint: `/api/movie/<int:pk>/comment/`
- Method: POST, DELETE
- Purpose: Add or delete a comment for a movie
- Request Format (ADD): Provide user credentials (access token). In the request body, provide a 'body' field. Movie is provided in the url. 
- Response Format (ADD): Returns a 400 status if there is an error adding the comment. Returns 201 if added successfully.
- Request Format (DELETE): Provide user credentials (acess token). In the request body, provide a 'comment_id' field. Movie is provided in the url.
- Response Format (DELETE): Returns a 400 status if no comment_id, 404 if comment not found, 204 if comment deleted successfully.
- Extra Notes: Body field will obviously hold the comment body. Timestamp is generated in the backend. Comment_id will hold the id of the comment desired to be deleted.

#### Add or Remove a Movie from Watch List
- Endpoint: `/api/movie/<int:pk>/watch/`
- Method: POST, DELETE
- Purpose: Add or remove a movie from the signed in user's watch list.
- Request Format (ADD): Provide user credentials (access token). The movie id to add to the list is provided in the url.
- Response Format (ADD): Returns a 404 status if error, 201 if movie added successfully.
- Request Format (DELETE): Provide user credentials (access token). The movie id to remove from the list is provided in the url.
- Response Format (DELETE): Returns a 404 status if error, 204 if movie removed successfully.
- Extra Notes: None for now.



### Other User Page

#### Other User Profile
- Endpoint: `/api/user/<int:user_id>/profile/`
- Method: GET
- Purpose: Get another user's profile data
- Request Format: Provide user credentials (access token). The desired user's id is provided in the url. Get this id from searching for a user or from a user list like a friends list. 
- Response Format: Returns the following fields for that user: 'id', 'username', 'bio', 'is_private', 'is_friend', 'is_outgoing', 'is_incoming'
- Extra Notes: is_private is true if the user is private, false otherwise. is_friend contains a friendship id if the signed in user is friends with user_id and is null otherwise. is_outgoing contains the outgoing friend request id if there is one, null otherwise. is_incoming contains the incoming request if there is one, null otherwise. 

#### Other User Friends List
- Endpoint: `/api/user/<int:user_id>/friends/`
- Method: GET
- Purpose: Get another user's friends list
- Request Format: Provide user credentials (access token). The desired user's id is provided in the url. 
- Response Format: Returns a list of users that are friends with the specified user. Each user in the list will contain an 'id' and 'username' just like the signed-in user's friends endpoint response.
- Extra Notes: This should only be displayed if the user is public and/or friends with the signed in user. 

#### View a User's Rated Movies
- Endpoint: `/api/user/<int:user_id>/movies/rated/`
- Method: GET
- Purpose: Get another user's rated movies list. 
- Request Format: Provide user credentials (access token). The desired user's id is provided in the url.
- Response Format: Returns a 200 status when successful with a list of movies. Each movie in the list has fields: 'id', 'title', 'poster_url', 'overview', 'release_date', 'runtime', 'adult', 'user_rating'
- Extra Notes: If the response status is 200 but the list is empty, then the user has not rated any movies. user_rating contains that user's rating for that movie.

#### Send a Friend Request
- Endpoint: `/api/send-friend-request/<int:to_user_id>/`
- Method: POST
- Purpose: Sends a friend request to a user id from the signed in user. 
- Request Format: Provide user credentials (acess token). The recipient id is provided in the url. 
- Response Format: Returns 201 status if successful, 404 if unsuccessful
- Extra Notes: Should only fail if the recipient doesn't exist. We can check if the signed-in user is already friends with to_user_id from querying to_user_id's profile data (is_friend status). We can also check if there's a pending request already sent to this user if to_user_id exists in the user ids from the signed-in user's outgoing friend requests list. 




## Services and Configuration

### Backend Framework
- Django: Chosen for its robustness and flexibility in building backend applications.

### API Framework
- Django Rest Framework: Integrated with Django to provide a powerful toolkit for building Web APIs. The API operates on port 8000 and is containerized for both development and production environments.

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


## Set Up
Will explain how to install this backend here.

### Rough Outline for Now

- Install Docker, Postgres, Python, etc.
- Creating a Postgres superuser
- Clone repository
- Creating venv and installing dependencies 
- Setting up environment variables and settings.py
- Building and running docker containers
- Setting up local DB in Postgres server container
- Setting up postgres user for django to use
- Creating a Django superuser for that DB instance
- Running management scripts to populate local database with data
- Running, Stopping, Using the backend
- Deploying the backend

### Notes on Management Scripts

Outlining what each management script does. Need to refurbish these soon for Set Up instructions but purpose should stay.

#### CSV-Sourced DB Population Scripts
- install_movies.py : Reads movies.csv and installs each movie's movie_id and genres
- install_links.py : Reads links.csv and finds each movie_id and maps to a tmdb_id
- install_ratings.py : Reads ratings.csv and creates users and ratings for each new user and rating

#### API-Sourced DB Scripts
- query_metadata.py : Queries TMDb API for remaining metadata per movie
- query_credits.py : Queries TMDb API for Director and Actor data per movie

#### Validation Scripts:
- clean_data.py : Deletes any movie and its associated ratings if a movie is missing any fields
- fix_user_passwords : fixes the passwords of script-generated user accounts

#### Debugging Scripts:
- log_missing_tmdb.py : Logs any movie_id that is missing tmdb_id
- log_missing_fields.py : Logs any movie_id with their missing metadata fields
- log_missing_credits.py : Logs any movie_id with their missing credits fields
- print_tmdb_query : Prints a TMDb query response to console
- print_user_ratings : Prints a user's rated movies to console
- print_user_recs : Prints a user's recommendations to console
- build_datasets : builts csv datasets from current database data for training models

Any scripts that are no longer important start with 'old'.