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



### User Management

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

#### User Details
- Endpoint: `/api/user/userprofile/`
- Method: GET
- Purpose: Retrieves all user metadata for the signed in user. 
- Request Format: Provide user credentials (access token)
- Response Format: Returns a response body with fields: 'id', 'username', 'email', 'birth_date', 'is_private', 'bio'

#### Rated Movies
- Endpoint: `/api/user/movies/rated/`
- Method: GET
- Purpose: Retrieves all movies the signed in user has rated.
- Request Format: Provide user credentials (access token)
- Response Format: Returns a a list of movies in the response body. Each movie in the list has fields: 'id', 'title', 'poster_url', 'overview', 'release_date', 'runtime', 'adult'
- Extra Notes: If the list is empty, the user has rated no movies.

#### Update Profile
- Endpoint: `/api/user/update/`
- Method: PUT
- Purpose: 
- Request Format: Provide user credentials (access token)
- Response Format: 200 status if updated successfully or a 400 status if unsuccessful.



### Movie Lists 

#### Get Primary Recommendation List 
- Endpoint: `/api/user/movies/`
- Method: GET
- Expects: userCredentials
- Purpose: Returns a recommendation list of movies for the signed in user
- Model Type: Currently set to our simple SVD/cosine similarity model. In the middle of switching to more accurate SVD/XGBoost model. Both are collaborative models based on user ratings. 
- Request Format: Provide user credentials (access token)
- Response Format: Returns a list of recommended movies for that user. Each movie in the list will have fields: 'id', 'title', 'poster_url', 'overview', 'release_date', 'runtime', 'adult'
- Extra Notes: Model will only be called if the user has rated a certain number of movies. Else, we return a list of randomly picked movies from the database.


#### Get Secondary Recommendation List
- Endpoint: None yet
- Method: GET
- Purpose: Returns a recommendation list of movies for the signed in user
- Model Type: Nothing implemented yet. ML team has a model for content-based filtering, or recommending movies based on similar movies, so that would be integrated on a separate endpoint for the separate list. 
- Behavior: undecided
- Request Format: Provide user credentials (access token)
- Response Format: undecided



### Movie Views

#### Search for a Movie
- Endpoint: `/api/movie/search/`
- Method: POST
- Purpose: Search for movie(s) given a title
- Request Format: Provide user credentials (access token). Query params should contain the 'title' field.
- Response Format: Provides a list of movies that match that title (Likely a list of 1 movie) with fields for each movie: 'id', 'title', 'poster_url', 'overview', 'release_date', 'runtime', 'adult'
- Extra Notes: An example POST request for title 'avengers' should look like `/api/movie/search?title=avengers`. Prepare for empty lists as this will signify no results from the search. 

#### Get a Movie's Details
- Endpoint: `/api/movie/<int:pk>/`
- Method: GET
- Purpose: Retrieves the details of a movie given its id 
- Request Format: Provide user credentials (access token). The movie id is provided in the url.
- Response Format: Returns a response body with fields: 'id', 'title', 'poster_url', 'overview', 'runtime', 'adult', 'cast', 'release_date', 'genres', 'average_rating', 'rated'
- Extra Notes: The 'rated' field will be 0 if the signed in user has not rated the movie yet. If the user has, the field will include the current user's rating for that movie (1-5). The genres will be a list of genre names. The cast field includes both actors and crew (directors, other staff), so frontend may need extra handling on the cast field to display these people in their appropriate places. The runtime is an integer in minutes. See models.py, views.py, and serializers.py for more info. 

#### Get a Movie's Comments
- Endpoint: `/api/movie/<int:pk>/comments/`
- Method: GET
- Purpose: Retrieves all comments for that movie given its movie id
- Request Format: Provide user credentials (access token). The movie id is provided in the url. 
- Response Format: Returns a list of all comments for that movie. Each comment contains the fields: 'id', 'body', 'timestamp', 'username'
- Extra Notes: Timestamp will likely have to be converted to something readable if it is used.

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



### Interaction

#### Search for a User
- Endpoint: `/api/user/search/`
- Method: GET
- Purpose: Search for user(s) given a username
- Request Format: Provide user credentials (access token). Query params should contain the 'username' field. 
- Response Format: Returns a list of users that contain that username. Each user in the list has fields: 'id', 'username'
- Extra Notes: An example would be `/api/user/search?username=johndoe`. Prepare for empty lists as this will signify no results from the search. 

#### View a User's Rated Movies
- Endpoint: `user/<int:user_id>/movies/rated/`
- Method: GET
- Purpose: If a given user is public or friends with the signed in user, a list of rated movies will return for that other user.
- Request Format: Provide user credentials (access token). Other user id is specified in the url. 
- Response Format: Returns 404 if user id not found. Returns 403 status if user is private. If successful, returns 200 status with a list of movies in the response body. Each movie in the list has fields: 'id', 'title', 'poster_url', 'overview', 'release_date', 'runtime', 'adult'
- Extra Notes: If the response status is 200 but the list is empty, then the user has not rated any movies.

#### Retrieve Friends List
- Endpoint: `/api/friends/`
- Method: GET
- Purpose: Retrieves the list of users the signed in user is friends with.
- Request Format: Provide user credentials (access token). 
- Response Format: Returns a list of users. Each user in the list has fields: 'id', 'username'
- Extra Notes: Prepare for empty lists as this signifies no friends. 

#### Send a Friend Request
- Endpoint: `/api/send-friend-request/<int:to_user_id>/`
- Method: POST
- Purpose: Sends a friend request to a user id from the signed in user. 
- Request Format: Provide user credentials (acess token). The recipient id is provided in the url. 
- Response Format: Returns 201 status if successful, 404 if unsuccessful
- Extra Notes: Should only fail if the recipient doesn't exist.

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

#### Remove a Friend
- Endpoint: `user/remove-friend/<int:friend_id>/`
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

#### Debugging Scripts:
- log_missing_tmdb.py : Logs any movie_id that is missing tmdb_id
- log_missing_fields.py : Logs any movie_id with their missing metadata fields
- log_missing_credits.py : Logs any movie_id with their missing credits fields
- print_tmdb_query : Prints a TMDb query response to console
- print_user_ratings : Prints a user's rated movies to console
- print_user_recs : Prints a user's recommendations to console

Any scripts that are no longer important start with 'old'.