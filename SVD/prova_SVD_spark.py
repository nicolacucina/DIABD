from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, max
from pyspark.ml.linalg import Vectors
from pyspark.sql import Row
import numpy as np
from pyspark.ml.feature import StandardScaler
from scipy.sparse.linalg import svds

# Creazione della sessione Spark
spark = SparkSession.builder.appName("SVD Recommender System").getOrCreate()

# Caricamento dei dataset
movies = spark.read.csv('ml-latest-small/ml-latest-small/movies.csv', header=True, inferSchema=True)
ratings = spark.read.csv('ml-latest-small/ml-latest-small/ratings.csv', header=True, inferSchema=True)

# Esplorazione dei dataset
print("Movies dataset:")
movies.show(5)
print("Ratings dataset:")
ratings.show(5)

# Creazione della matrice utente-film
user_movie_matrix = ratings.groupBy("userId").pivot("movieId").agg(max("rating")).fillna(0)
print("User-movie matrix:")
user_movie_matrix.show(5)

# Conversione in formato vettoriale per SVD
def row_to_vector(row):
    return Row(userId=row[0], featureVector=Vectors.dense(row[1:]))

user_movie_rdd = user_movie_matrix.rdd.map(lambda row: row_to_vector(row))
user_movie_df = spark.createDataFrame(user_movie_rdd)

# Standardizzazione dei dati prima di applicare SVD
scaler = StandardScaler(inputCol="featureVector", outputCol="scaledFeatures", withMean=True, withStd=True)
scaler_model = scaler.fit(user_movie_df)
scaled_data = scaler_model.transform(user_movie_df)

# Applicazione di SVD
# Conversione dei dati in matrice numpy per SVD
feature_matrix = np.array(scaled_data.select("scaledFeatures").rdd.map(lambda row: row[0].toArray()).collect())
U, sigma, Vt = svds(feature_matrix, k=20)  # k: numero di feature latenti

#debug print: stampa dei primi 10 elementi di U, sigma e Vt
print("U:") 
print(U[:10])
print("Sigma:")
print(sigma[:10])
print("Vt:")
print(Vt[:10])

# Ricostruzione approssimata della matrice utente-film
sigma_diag = np.diag(sigma)
approx_user_movie_matrix = np.dot(np.dot(U, sigma_diag), Vt)

# Creazione DataFrame predetto
user_movie_predictions = spark.createDataFrame(
    [(int(user_id), Vectors.dense(predictions)) for user_id, predictions in enumerate(approx_user_movie_matrix)],
    ["userId", "predictions"]
)

print("Matrice predetta:")
user_movie_predictions.show(5, truncate=False)

# Calcolo della similarità coseno tra i film
movie_features = Vt.T  # Feature latenti dei film
cosine_sim = np.dot(movie_features, movie_features.T) / (
    np.linalg.norm(movie_features, axis=1).reshape(-1, 1) * np.linalg.norm(movie_features, axis=1)
)

# Mappatura movieId -> indice nella matrice
movie_id_to_index = {movie_id: idx for idx, movie_id in enumerate(user_movie_matrix.columns)}

# Verifica della correlazione tra similarità e generi
movie_genres = movies.rdd.map(lambda row: (row.movieId, row.genres)).collectAsMap()
similar_movies = {}

for movie_id, idx in movie_id_to_index.items():
    similar_indices = np.argsort(-cosine_sim[idx])[:10]
    similar_movies[movie_id] = [
        (list(movie_id_to_index.keys())[sim_idx], movie_genres.get(list(movie_id_to_index.keys())[sim_idx], "Unknown"))
        for sim_idx in similar_indices
        if list(movie_id_to_index.keys())[sim_idx] in movie_genres
    ]

# Output dei risultati
print("Film simili in base alle feature latenti:")
for movie_id, similars in list(similar_movies.items())[:5]:
    movie_title = movies.filter(movies.movieId == movie_id).select("title").collect()[0][0]
    print(f"Film: {movie_title} ({movie_genres[movie_id]})")
    for sim_movie_id, sim_genre in similars:
        sim_movie_title = movies.filter(movies.movieId == sim_movie_id).select("title").collect()[0][0]
        print(f"  Simile a: {sim_movie_title} ({sim_genre})")
    print()
