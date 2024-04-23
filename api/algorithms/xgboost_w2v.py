import joblib
import pandas as pd
import numpy as np
from api.models import Movie, Rating, GenericUser
from xgboost import XGBClassifier
from gensim.models import Word2Vec

def recommend_movies(username, top_n=10):
    # Load the model, vectorizer, and Word2Vec models
    model = XGBClassifier()
    model.load_model("api/algorithms/mc_rec_w2v.json")
    vectorizer = joblib.load("api/algorithms/tfidf_w2v.joblib")
    w2v_director = Word2Vec.load("api/algorithms/Word2Vec_director")
    w2v_keyword = Word2Vec.load("api/algorithms/Word2Vec_keyword")

    # Retrieve user info and their rated movie IDs
    user = GenericUser.objects.get(username=username)
    rated_movie_ids = Rating.objects.filter(user=user).values_list('movie__movie_id', flat=True)

    # Retrieve movies not yet rated by the user, and related data
    movies_to_rate = Movie.objects.exclude(movie_id__in=rated_movie_ids).prefetch_related('genres', 'directors', 'keywords')

    # Prepare data for DataFrame construction
    movie_data = []
    genres_list = []
    for movie in movies_to_rate:
        genres = ', '.join(genre.name for genre in movie.genres.all())
        directors = ' '.join(director.name for director in movie.directors.all())
        keywords = ' '.join(keyword.name for keyword in movie.keywords.all())

        director_vectors = [w2v_director.wv[word] for word in directors.split() if word in w2v_director.wv]
        keyword_vectors = [w2v_keyword.wv[word] for word in keywords.split() if word in w2v_keyword.wv]

        movie_info = {
            "movie_id": movie.movie_id,
            "runtime": movie.runtime,
            "adult": movie.adult,
            "user_id": user.id,
            **{f"{i+1}director": np.mean(director_vectors, axis=0)[i] if director_vectors else 0 for i in range(50)},
            **{f"{i+1}keyword": np.mean(keyword_vectors, axis=0)[i] if keyword_vectors else 0 for i in range(50)}
        }

        movie_data.append(movie_info)
        genres_list.append(genres)

    # Create DataFrame
    movie_df = pd.DataFrame(movie_data)

    # Apply TF-IDF to all genres at once
    genres_tfidf = vectorizer.transform(genres_list)
    tfidf_df = pd.DataFrame(genres_tfidf.toarray(), columns=vectorizer.get_feature_names_out())
    movie_df = pd.concat([movie_df, tfidf_df], axis=1)

    # Reorder DataFrame columns to match the model's training order
    model_feature_order = ['movie_id', 'runtime', 'adult', 'user_id'] + list(tfidf_df.columns) + \
                          [f'{i+1}director' for i in range(50)] + [f'{i+1}keyword' for i in range(50)]
    movie_df = movie_df[model_feature_order]

    # Ensure the 'genres' column is dropped if it exists
    if 'genres' in movie_df.columns:
        movie_df.drop(columns=['genres'], inplace=True)

    # Predict the likelihood of the user liking these movies
    predictions = model.predict_proba(movie_df)[:, 1]
    movie_df['likelihood'] = predictions

    # Recommend the top N movies based on likelihood
    top_movies = movie_df.nlargest(top_n, 'likelihood')['movie_id']

    # Get the movie titles based on predicted movie IDs
    recommended_titles = Movie.objects.filter(movie_id__in=top_movies).values_list('title', flat=True)

    return list(recommended_titles)


