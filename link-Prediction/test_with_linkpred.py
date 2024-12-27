from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, size, collect_list
from pyspark.sql.types import IntegerType, FloatType, StringType
from graphframes import GraphFrame

# Creazione della sessione Spark
spark = SparkSession.builder \
    .appName("PageRank Recommendation System with Link Prediction") \
    .config("spark.jars.packages", "graphframes:graphframes:0.8.2-spark3.1-s_2.12") \
    .getOrCreate()

# Caricamento dei dati
ratings = spark.read.csv("ratings.csv", header=True, inferSchema=True)
movies = spark.read.csv("movies.csv", header=True, inferSchema=True)

# Unione tra ratings e movies
ratings = ratings.join(movies, on="movieId")
ratings.show(5)

# Mappatura dei punteggi
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

map_score_udf = spark.udf.register("map_score", lambda x: mapping_score.get(x, 0), FloatType())
ratings = ratings.withColumn("weight", map_score_udf(col("rating")))

# Creazione degli archi per il grafo (Utente -> Film)
edges = ratings.select(
    col("userId").cast(StringType()).alias("src"),
    col("title").alias("dst"),
    col("weight")
)

# Creazione dei vertici (utenti e film)
vertices_users = ratings.select(col("userId").cast(StringType()).alias("id")).distinct().withColumn("bipartite", lit(0))
vertices_movies = ratings.select(col("title").alias("id")).distinct().withColumn("bipartite", lit(1))
vertices = vertices_users.union(vertices_movies)

# Creazione del grafo
user_movie_graph = GraphFrame(vertices, edges)

# Proiezione del grafo: utente-utente e film-film
user_user_edges = user_movie_graph.edges.alias("e1") \
    .join(user_movie_graph.edges.alias("e2"), col("e1.dst") == col("e2.dst")) \
    .select(
        col("e1.src").alias("src"),
        col("e2.src").alias("dst"),
        (col("e1.weight") + col("e2.weight")).alias("weight")
    ).filter(col("src") != col("dst"))

user_user_graph = GraphFrame(user_movie_graph.vertices, user_user_edges)

movie_movie_edges = user_movie_graph.edges.alias("e1") \
    .join(user_movie_graph.edges.alias("e2"), col("e1.src") == col("e2.src")) \
    .select(
        col("e1.dst").alias("src"),
        col("e2.dst").alias("dst"),
        (col("e1.weight") + col("e2.weight")).alias("weight")
    ).filter(col("src") != col("dst"))

movie_movie_graph = GraphFrame(user_movie_graph.vertices, movie_movie_edges)

# Funzione per calcolare la similarità tra due film usando i vicini comuni
def common_neighbors_similarity(movie1, movie2, user_movie_graph):
    users1 = user_movie_graph.edges.filter(col("dst") == movie1).select("src").rdd.flatMap(lambda x: x).collect()
    users2 = user_movie_graph.edges.filter(col("dst") == movie2).select("src").rdd.flatMap(lambda x: x).collect()
    
    # Calcolare i vicini comuni
    common_users = set(users1).intersection(set(users2))
    return len(common_users)

# Funzione per predire i link tra un utente e un film
def predict_links(user_id, movie_id, user_movie_graph):
    movies = user_movie_graph.vertices.filter(col("bipartite") == 1).select("id").rdd.map(lambda row: row[0]).collect()
    
    similarity_scores = []
    for movie in movies:
        if movie != movie_id:
            score = common_neighbors_similarity(movie_id, movie, user_movie_graph)
            similarity_scores.append((movie, score))
    
    # Ordina i film in base alla similarità
    similarity_scores.sort(key=lambda x: x[1], reverse=True)
    return similarity_scores[:10]  # Restituisci i 10 film più simili

# Funzione per creare il vettore di preferenze per un utente
def create_preference_vector(user_id, user_movie_graph):
    edges = user_movie_graph.edges.filter(col("src") == user_id).rdd.map(lambda row: (row["dst"], row["weight"])).collect()
    tot = sum([weight for _, weight in edges])
    if tot > 0:
        return {movie: weight / tot for movie, weight in edges}
    else:
        movies = user_movie_graph.vertices.filter(col("bipartite") == 1).select("id").rdd.map(lambda row: row[0]).collect()
        return {movie: 1 / len(movies) for movie in movies}

# Funzione per prevedere i film per un utente
def predict_user(user_id, user_movie_graph, movie_movie_graph):
    p_vec = create_preference_vector(user_id, user_movie_graph)
    already_seen = [movie for movie, weight in p_vec.items() if weight > 0]
    
    # Predici i film che l'utente potrebbe apprezzare
    predicted_links = []
    for movie in already_seen:
        similar_movies = predict_links(user_id, movie, user_movie_graph)
        for movie_id, score in similar_movies:
            if movie_id not in already_seen:
                predicted_links.append((movie_id, score))
    
    # Calcola il PageRank per i film
    pagerank_results = movie_movie_graph.pageRank(resetProbability=0.95, maxIter=20)
    item_rank = pagerank_results.vertices.select("id", "pagerank").rdd.map(lambda row: (row["id"], row["pagerank"])).collectAsMap()
    
    # Combina le raccomandazioni
    recommendations = sorted(predicted_links, key=lambda x: x[1], reverse=True)
    
    # Ordina i film in base al punteggio di PageRank
    recommendations += sorted(
        (movie for movie in item_rank if movie not in already_seen),
        key=lambda x: item_rank[x], reverse=True
    )
    
    return recommendations[:10]

# Prevedi i film per un utente specifico
user = "10"  # ID dell'utente di esempio
recommended_movies = predict_user(user, user_user_graph, movie_movie_graph)
print(f"Recommended movies for user {user}: {recommended_movies[:10]}")
