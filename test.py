###PROVA PRIMO BLOCCO:

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, size, collect_list
from pyspark.sql.types import IntegerType, FloatType, StringType
from graphframes import GraphFrame

# Creazione della sessione Spark
spark = SparkSession.builder \
    .appName("PageRank Recommendation System") \
    .config("spark.jars.packages", "graphframes:graphframes:0.8.2-spark3.1-s_2.12") \
    .getOrCreate()

# Open ratings.csv file
ratings = spark.read.csv("ratings.csv", header=True, inferSchema=True)
#print dei ratings
ratings.show(5)

# Open movies.csv file
movies = spark.read.csv("movies.csv", header=True, inferSchema=True)

# Merge ratings e movies
ratings = ratings.join(movies, on="movieId")
ratings.show(5)

# Check for common movies rated by multiple users
common_movies = ratings.groupBy("title").count().filter(col("count") > 1) # Print movies rated by more than one user
common_movies.show(10)

####PROVA SECONDO BLOCCO

# Map rating to scores
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

# # Funzione per mappare i punteggi --> non c'è nell'originale, ma pare necessario?
map_score_udf = spark.udf.register("map_score", lambda x: mapping_score.get(x, 0), FloatType())
ratings = ratings.withColumn("weight", map_score_udf(col("rating")))
ratings.show(5)



####PROVA TERZO BLOCCO
# Create a directed graph called user_movie_graph and then we will add the edges and nodes to it
edges = ratings.select(
    col("userId").cast(StringType()).alias("src"),
    col("title").alias("dst"),
    col("weight")
)
vertices_users = ratings.select(col("userId").cast(StringType()).alias("id")).distinct().withColumn("bipartite", lit(0))
vertices_movies = ratings.select(col("title").alias("id")).distinct().withColumn("bipartite", lit(1))
vertices = vertices_users.union(vertices_movies)

# Build the user-movie graph
user_movie_graph = GraphFrame(vertices, edges)

# Debug: Check the graph construction
print("First 10 nodes in the graph:")
user_movie_graph.vertices.show(10, truncate=False)
print("First 10 edges in the graph:")
user_movie_graph.edges.show(10, truncate=False)


#### PROVA QUARTO BLOCCO: proiezione del grafo
# Project the graph
# Filter the vertices to get the users and movies
# Project user-user graph
user_user_edges = user_movie_graph.edges.alias("e1") \
    .join(user_movie_graph.edges.alias("e2"), col("e1.dst") == col("e2.dst")) \
    .select(
        col("e1.src").alias("src"),
        col("e2.src").alias("dst"),
        (col("e1.weight") + col("e2.weight")).alias("weight")
    ).filter(col("src") != col("dst"))

user_user_graph = GraphFrame(user_movie_graph.vertices, user_user_edges)

# Project movie-movie graph
movie_movie_edges = user_movie_graph.edges.alias("e1") \
    .join(user_movie_graph.edges.alias("e2"), col("e1.src") == col("e2.src")) \
    .select(
        col("e1.dst").alias("src"),
        col("e2.dst").alias("dst"),
        (col("e1.weight") + col("e2.weight")).alias("weight")
    ).filter(col("src") != col("dst"))

movie_movie_graph = GraphFrame(user_movie_graph.vertices, movie_movie_edges)

# Debug: Check the projected graphs
print("User-user graph:")
user_user_graph.edges.show(5)
print("Movie-movie graph:")
movie_movie_graph.edges.show(5)


# ### PROVA QUINTO BLOCCO: using weights 
#DA VERIFICARE SE E' VERO CHE: "In Spark, la gestione delle proiezioni su grafi bipartiti è diversa rispetto a NetworkX.
#La proiezione pesata (e.g., weighted_projected_graph) non ha un'implementazione diretta con GraphFrames, quindi nel mio codice 
# ho evitato la costruzione manuale delle proiezioni pesate e ho utilizzato gli strumenti 
# di GraphFrames per calcolare direttamente il PageRank sulle componenti connesse."



###PROVA SETTIMO BLOCCO: create function for creating the preference vector
# Funzione per creare il vettore di preferenze
def create_preference_vector(user_id, user_movie_graph):
    edges = user_movie_graph.edges.filter(col("src") == user_id).rdd.map(lambda row: (row["dst"], row["weight"])).collect()
    print(f"Preference vector for user {user_id}: {edges}")
    tot = sum([weight for _, weight in edges])
    print(f"Total weight for user {user_id}: {tot}")
    if tot > 0:
        return {movie: weight / tot for movie, weight in edges}
    else:
        movies = user_movie_graph.vertices.filter(col("bipartite") == 1).select("id").rdd.map(lambda row: row[0]).collect()
        return {movie: 1 / len(movies) for movie in movies}

###PROVA OTTAVO BLOCCO: create function for predicting the movies
# Function to predict movies
def predict_user(user_id, user_movie_graph, movie_movie_graph):
    p_vec = create_preference_vector(user_id, user_movie_graph)
    print(f"Preference vector for user {user_id}: {p_vec}")
    already_seen = [movie for movie, weight in p_vec.items() if weight > 0]
    print(f"Already seen movies for user {user_id}: {already_seen}")
    if len(already_seen) == len(p_vec):
        return []
    pagerank_results = movie_movie_graph.pageRank(resetProbability=0.95, maxIter=20)
    item_rank = pagerank_results.vertices.select("id", "pagerank").rdd.map(lambda row: (row["id"], row["pagerank"])).collectAsMap()
    recommendations = sorted(
        (movie for movie in item_rank if movie not in already_seen),
        key=lambda x: item_rank[x], reverse=True
    )
    return recommendations

###PROVA NONO BLOCCO: predict the next movie
# Predict the next movie
user = "10"
s_t = predict_user(user, user_user_graph, movie_movie_graph)
print(f"Predicted movies for user {user}: {s_t[:10]}")




