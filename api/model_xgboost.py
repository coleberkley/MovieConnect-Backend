import joblib
import pandas as pd
from api.models import Movie, Rating, GenericUser
from xgboost import XGBClassifier

def recommend_movies(username, top_n=10):
    # Load the model and vectorizer
    model = XGBClassifier()
    model.load_model("api/MC_rec.json")
    vectorizer = joblib.load("api/tfidf.joblib")

    # Retrieve user info
    user = GenericUser.objects.get(username=username)
    
    # Get all movies and user ratings
    user_ratings = Rating.objects.filter(user=user).select_related('movie')
    rated_movie_ids = [rating.movie.movie_id for rating in user_ratings]
    
    # Filter out movies that the user has already rated
    movies_to_rate = Movie.objects.exclude(movie_id__in=rated_movie_ids)

    # Prepare movie data for prediction
    movie_data = [{
        "movie_id": movie.movie_id,  # Include movie_id to satisfy model's current structure
        "genres": ', '.join([genre.name for genre in movie.genres.all()]),
        "runtime": movie.runtime,
        "adult": movie.adult,
        "user_id": user.id  # user_id is constant for all predictions
    } for movie in movies_to_rate]
    
    movie_df = pd.DataFrame(movie_data)
    
    # Transform genres using the vectorizer
    tfidf_matrix = vectorizer.transform(movie_df['genres'])
    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())
    movie_df = pd.concat([movie_df, tfidf_df], axis=1)
    movie_df.drop(columns=['genres'], inplace=True)
    
    # Predict the likelihood of the user liking these movies
    predictions = model.predict_proba(movie_df)[:, 1]  # get the probability of 'liked'
    movie_df['likelihood'] = predictions

    # Recommend the top N movies
    top_movies = movie_df.nlargest(top_n, 'likelihood')['movie_id']
    
    # Get the movie titles based on predicted movie IDs
    recommended_titles = Movie.objects.filter(movie_id__in=top_movies).values_list('title', flat=True)
    
    return list(recommended_titles)







