import joblib
import pandas as pd
import numpy as np
from api.models import Movie, Rating, GenericUser
from xgboost import XGBClassifier
from gensim.models import Word2Vec

def compute_vector_mean(model, words):
    vectors = [model.wv[word] for word in words if word in model.wv]
    if vectors:
        return np.mean(vectors, axis=0)
    else:
        return np.zeros(50)

def recommend_movies(username, top_n=20):
    # Load the model, vectorizer, and Word2Vec models
    model = XGBClassifier()
    model.load_model("api/algorithms/mc_rec_w2v.json")
    vectorizer = joblib.load("api/algorithms/tfidf_w2v.joblib")
    w2v_director = Word2Vec.load("api/algorithms/Word2Vec_director")
    w2v_keyword = Word2Vec.load("api/algorithms/Word2Vec_keyword")

    # Retrieve user info and their rated movie IDs
    user = GenericUser.objects.get(username=username)
    rated_movie_ids = Rating.objects.filter(user=user).values_list('movie__movie_id', flat=True)

    # Load movie data from CSV
    movie_df = pd.read_csv('data/xgboost_enhanced_data.csv')

    # Ensure columns for directors and keywords are not NaN and are strings
    movie_df['directors'] = movie_df['directors'].fillna('')
    movie_df['keywords'] = movie_df['keywords'].fillna('')
    
    # Add user_id to DataFrame for all entries
    movie_df['user_id'] = user.id
    
    # Vectorize directors and keywords
    movie_df['director_vectors'] = movie_df['directors'].apply(
        lambda x: compute_vector_mean(w2v_director, x.split())
    )
    movie_df['keyword_vectors'] = movie_df['keywords'].apply(
        lambda x: compute_vector_mean(w2v_keyword, x.split())
    )

    # Vectorize genres and transform into DataFrame columns
    genres_tfidf = vectorizer.transform(movie_df['genres'])
    genres_df = pd.DataFrame(genres_tfidf.toarray(), columns=vectorizer.get_feature_names_out())
    movie_df = pd.concat([movie_df, genres_df], axis=1)
    
    # Drop original columns for genres, directors, and keywords
    movie_df.drop(columns=['directors', 'keywords'], inplace=True)
    
    # Merge director and keyword vectors into the main dataframe
    director_columns = pd.DataFrame(movie_df['director_vectors'].tolist(), index=movie_df.index)
    director_columns.columns = [f'{i+1}director' for i in range(50)]
    keyword_columns = pd.DataFrame(movie_df['keyword_vectors'].tolist(), index=movie_df.index)
    keyword_columns.columns = [f'{i+1}keyword' for i in range(50)]
    movie_df = pd.concat([movie_df, director_columns, keyword_columns], axis=1)

    # Define the feature order
    feature_order = ['movie_id', 'runtime', 'adult', 'user_id'] + list(genres_df.columns) + \
                    [f'{i+1}director' for i in range(50)] + [f'{i+1}keyword' for i in range(50)]
    movie_df = movie_df[feature_order]

    if 'genres' in movie_df.columns:
        movie_df.drop(columns=['genres'], inplace=True)

    # Predict the likelihood of the user liking these movies
    predictions = model.predict_proba(movie_df)[:, 1]
    movie_df['likelihood'] = predictions

    # Recommend the top N movies based on likelihood
    top_movies = movie_df.nlargest(top_n, 'likelihood')['movie_id']

    # Exclude movies that the user has already rated
    recommended_movies = top_movies[~top_movies.isin(rated_movie_ids)]
    
    # Get the movie titles based on predicted movie IDs
    recommended_titles = Movie.objects.filter(movie_id__in=recommended_movies).values_list('title', flat=True)

    return list(recommended_titles)



