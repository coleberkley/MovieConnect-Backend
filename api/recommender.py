from .models import Movie, Rating
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from django.contrib.auth import get_user_model

# This file contains the code for the SVD + Cosine Similarity recommendation model

User = get_user_model()

def get_user_item_matrix():
    # Fetch all user ratings from the database
    ratings = Rating.objects.all().values_list('user_id', 'movie_id', 'rating')
    
    # Convert to DataFrame
    ratings_df = pd.DataFrame(ratings, columns=['user_id', 'movie_id', 'rating'])
    
    # Pivot to create the user-item matrix
    user_item_matrix = ratings_df.pivot(index='user_id', columns='movie_id', values='rating').fillna(0)
    
    # Generate mappings for user IDs to matrix indices and vice versa
    user_ids = list(user_item_matrix.index)
    movie_ids = list(user_item_matrix.columns)
    
    return user_item_matrix, user_ids, movie_ids


def get_user_factors_items_factors():
    user_item_matrix, user_ids, movie_ids = get_user_item_matrix()
    user_item_matrix_values = user_item_matrix.values  # Convert DataFrame to numpy array for SVD
    
    svd = TruncatedSVD(n_components=20, random_state=42)
    user_factors = svd.fit_transform(user_item_matrix_values)
    item_factors = svd.components_.T  # Transpose item factors for alignment
    
    return user_factors, item_factors, user_ids, movie_ids



def recommend_movies(username, top_n=10):
    try:
        user = User.objects.get(username=username)  # Fetch user by username
    except User.DoesNotExist:
        return []
    
    # Check if the user has rated at least 10 movies
    if Rating.objects.filter(user=user).count() < 5:
        # Not enough data to generate recommendations so it returns the first 10 movies in the database
        movies = Movie.objects.all()[:10]
        return list(movies.values_list('title', flat=True))
    
    user_factors, item_factors, user_ids, movie_ids = get_user_factors_items_factors()
    
    user_index = user_ids.index(user.id)
    user_vector = user_factors[user_index].reshape(1, -1)  # User vector for cosine similarity
    
    similarity_scores = cosine_similarity(user_vector, item_factors)[0]
    
    # Fetch rated movie IDs by the user
    rated_movie_ids = Rating.objects.filter(user=user).values_list('movie_id', flat=True)
    
    # Exclude movies that have already been rated by filtering out their indices
    # Only consider movie indices that are not in the user's rated movie IDs
    movie_indices_filtered = [index for index, movie_id in enumerate(movie_ids) if movie_id not in rated_movie_ids]
    
    # Adjust similarity scores to only include indices of non-rated movies
    similarity_scores_filtered = similarity_scores[movie_indices_filtered]
    movie_ids_filtered = [movie_ids[index] for index in movie_indices_filtered]
    
    # Get top N similar item indices from the filtered list based on similarity scores
    top_item_indices = similarity_scores_filtered.argsort()[-top_n:][::-1]
    
    # Map filtered indices back to movie IDs
    recommended_movie_ids = [movie_ids_filtered[index] for index in top_item_indices]
    
    recommended_movies = Movie.objects.filter(id__in=recommended_movie_ids).values_list('title', flat=True)
    
    # Return the list of movies which is currently set to 10
    return list(recommended_movies)