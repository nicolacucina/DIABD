import pandas as pd

# Open ratings.csv file
ratings = pd.read_csv("ml-latest-small/ratings.csv")
movies = pd.read_csv("ml-latest-small/movies.csv")

# Merge ratings and movies
user_movie_matrix = pd.merge(ratings, movies, on="movieId")
print(user_movie_matrix.head())

user = 10
user_table = user_movie_matrix[user_movie_matrix['userId'] == user]
print(user_table.head())

pd.DataFrame.to_csv(user_table, "user_10.csv")