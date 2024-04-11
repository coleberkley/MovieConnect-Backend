from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split
from .models import Rating, Movie, GenericUser  # Adjust your import paths as needed
import pandas as pd
import xgboost as xgb
from django.db.models import Case, When

# This file contains the code for the SVD + XGBoost recommendation model

def get_recommendations_for_user(username):

    # Fetch data from the database
    data = Rating.objects.all().values_list('user_id', 'movie__movie_id', 'rating')
    
    # Creating a DataFrame
    df = pd.DataFrame(list(data), columns=['userId', 'movieId', 'rating'])

    # Define the scale of your dataset ratings
    reader = Reader(rating_scale=(1, 5))
    
    # Load the dataset from the DataFrame
    data = Dataset.load_from_df(df[['userId', 'movieId', 'rating']], reader)
    
    # Build the full trainset
    trainset = data.build_full_trainset()
    
    # Define the SVD algorithm
    algo = SVD(n_factors=100, biased=True, random_state=15)
    
    # Train the algorithm on the trainset
    algo.fit(trainset)

    # Fetch the list of movies that the user has rated
    user_rated_movies = list(Rating.objects.filter(user__username=username).values_list('movie__movie_id', flat=True))

    # all_movie_ids is a list of all movie IDs in the dataset
    all_movie_ids = list(Movie.objects.values_list('movie_id', flat=True))

    # Predict ratings for all unrated movies
    predictions = []
    for movie_id in set(all_movie_ids) - set(user_rated_movies):
        predictions.append((movie_id, algo.predict(username, movie_id).est))
    
    # Convert predictions to a dataframe for XGBoost
    predictions_df = pd.DataFrame(predictions, columns=['movieId', 'predicted_rating'])

    # Save model from notebook doing xgb_model.save_model('xgb_model.json')

    # # Load pre-trained XGBoost model
    # xgb_model = xgb.XGBRegressor()
    # xgb_model.load_model('path_to_model.json')

    # # Predict with XGBoost
    # predictions_df['predicted_rating'] = xgb_model.predict(predictions_df)

    # # Sort the predictions in descending order of predicted rating
    # predictions_df.sort_values(by='predicted_rating', ascending=False, inplace=True)

    # # Fetch the top N recommendations, you can define N
    # top_n_recommendations = predictions_df.head(10)

    # # Retrieve detailed information for the top N recommendations
    # # Use Django's 'Case' and 'When' to preserve the order of recommendations when querying the database
    # preserved_order = Case(*[When(movie_id=pk, then=pos) for pos, pk in enumerate(top_n_recommendations['movieId'])])
    # recommended_movies = Movie.objects.filter(movie_id__in=top_n_recommendations['movieId']).annotate(order=preserved_order).order_by('order')
    
    # # Return list to views.py
    # return list(recommended_movies.values_list('title', flat=True))

    
    



