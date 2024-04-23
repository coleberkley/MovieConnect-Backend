import joblib
import pandas as pd
from api.models import Movie, Rating, GenericUser
from xgboost import XGBClassifier

def recommend_movies(username, top_n=20):
    # Load the model and vectorizer
    model = XGBClassifier()
    model.load_model("api/algorithms/MC_rec.json")
    vectorizer = joblib.load("api/algorithms/tfidf.joblib")

    # Retrieve user info
    user = GenericUser.objects.get(username=username)
    user_ratings = Rating.objects.filter(user=user).values_list('movie__movie_id', flat=True)


    movie_df = pd.read_csv('data/xgboost_static_data.csv')

    # Handle possible NaNs in 'movie_id'
    if movie_df['movie_id'].isna().any():
        print(f"Warning: NaN values found in movie_id column, dropping rows.")
        movie_df.dropna(subset=['movie_id'], inplace=True)

    if movie_df['adult'].isnull().any():
        movie_df['adult'].fillna(False, inplace=True)

    # Ensure the 'adult' column is of type integer
    movie_df['adult'] = movie_df['adult'].astype(int)

    # Add user_id to DataFrame for all entries
    movie_df['user_id'] = user.id

    
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

    # Exclude movies that the user has already rated
    recommended_movies = top_movies[~top_movies.isin(user_ratings)]
    
    # Get the movie titles based on predicted movie IDs
    recommended_titles = Movie.objects.filter(movie_id__in=recommended_movies).values_list('title', flat=True)
    
    return list(recommended_titles)
