import pandas as pd

ratings = pd.read_csv("ml-latest-small/ratings.csv")
movies = pd.read_csv("ml-latest-small/movies.csv")

user_movie_matrix = ratings.pivot(index="userId", columns="movieId", values="rating").fillna(0)
print("User-movie matrix:")
print(user_movie_matrix.head())
pd.DataFrame(user_movie_matrix).to_csv("user_movie_matrix.csv")