from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, lit, collect_list, udf, explode
from pyspark.ml.recommendation import ALS
from pyspark.mllib.linalg.distributed import IndexedRowMatrix, IndexedRow
from pyspark.mllib.linalg import Vectors

# Creazione di una SparkSession
spark = SparkSession.builder \
    .appName("MovieLens Analysis") \
    .getOrCreate()

# Lettura dei file ratings.csv e movies.csv
ratings = spark.read.csv("ratings.csv", header=True, inferSchema=True)
movies = spark.read.csv("movies.csv", header=True, inferSchema=True)

# Join dei dati di ratings e movies
ratings = ratings.join(movies, on="movieId", how="inner")

# Controllo dei voti univoci
print("Unique ratings:")
ratings.select("rating").distinct().show()

# Calcolo dei film comuni valutati da più utenti
common_movies = ratings.groupBy("title").agg(count("userId").alias("count"))
print("Movies rated by more than one user:")
common_movies.filter(col("count") > 1).show(10)

# Mapping dei punteggi
mapping_score = {
    0.5: -1,
    1: -1,
    1.5: -0.5,
    2: 0,
    2.5: 0,
    3: 0,
    3.5: 0.5,
    4: 1,
    4.5: 1.1,
    5: 1.2
}
mapping_udf = udf(lambda x: mapping_score.get(x, 0))
ratings = ratings.withColumn("mapped_rating", mapping_udf(col("rating")))

# Costruzione di un grafo bipartito (approssimato con Spark)
user_movie_edges = ratings.select("userId", "title", "mapped_rating")

# Creazione delle proiezioni del grafo
user_movie_grouped = user_movie_edges.groupBy("userId").agg(collect_list("title").alias("movies"))
movie_user_grouped = user_movie_edges.groupBy("title").agg(collect_list("userId").alias("users"))

# Creazione della matrice user-movie per raccomandazioni
als = ALS(maxIter=10, regParam=0.1, userCol="userId", itemCol="movieId", ratingCol="mapped_rating", coldStartStrategy="drop")
model = als.fit(ratings)

# Generazione delle raccomandazioni per gli utenti
user_recommendations = model.recommendForAllUsers(10)
print("Recommendations for users:")
user_recommendations.show(5, truncate=False)

# Generazione delle raccomandazioni per i film
movie_recommendations = model.recommendForAllItems(10)
print("Recommendations for movies:")
movie_recommendations.show(5, truncate=False)

# Funzioni per il calcolo del vettore di preferenze e predizione dei film
@udf
def create_preference_vector(user_movies):
    total_score = sum([mapping_score.get(rating, 0) for rating in user_movies])
    return {movie: mapping_score.get(rating, 0) / total_score if total_score > 0 else 1 for movie, rating in user_movies}

ratings_with_pref = ratings.groupBy("userId").agg(collect_list(("title", "mapped_rating")).alias("user_movies"))
rating_vectors = ratings_with_pref.withColumn("preference_vector", create_preference_vector(col("user_movies")))

# Predizione per un utente specifico (approssimazione con Spark ALS)
def predict_user_movies(user_id):
    user_subset = ratings.filter(col("userId") == user_id)
    recommendations = model.recommendForUserSubset(user_subset, 10)
    return recommendations

# Esempio di predizione
user_id = 10
predictions = predict_user_movies(user_id)
print(f"Predictions for user {user_id}:")
predictions.show(truncate=False)
