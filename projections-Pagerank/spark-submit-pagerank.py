# https://stackoverflow.com/questions/68246173/python-was-not-found-but-can-be-installed-when-using-spark-submit-on-windows


# pip install findspark
import findspark
findspark.init()

import pyspark
from pyspark.sql import SparkSession

spark = SparkSession.builder \
        .appName("Spark basic example") \
        .config("spark.driver.memory", "6g") \
        .getOrCreate()

from pyspark.sql import SQLContext
sqlContext = SQLContext(spark)

spark.sparkContext._conf.getAll()  # check the config

ratings = spark.read.csv('hdfs://localhost:9001/test/ratings.csv', header=True, inferSchema=True)

movies = spark.read.csv('hdfs://localhost:9001/test/movies.csv', header=True, inferSchema=True)

user_movie_matrix = ratings.join(movies, on="movieId", how="inner")

mapping_score = {
    0.5: -1.0,
    1: -1.0,
    1.5: -0.5,
    2: 0.0,
    2.5: 0.0,
    3: 0.0,
    3.5: 0.5,
    4: 1.0,
    4.5: 1.1,
    5: 1.2
}

from pyspark.sql.types import IntegerType, FloatType, StringType
from pyspark.sql.functions import col

map_score_udf = spark.udf.register("map_score", lambda x: mapping_score.get(x, 0), FloatType())
user_movie_matrix = user_movie_matrix.withColumn("weight", map_score_udf(col("rating")))

edges = user_movie_matrix.select(
    col("userId").cast(StringType()).alias("src"),
    col("title").alias("dst"),
    col("weight")
)

from pyspark.sql.functions import lit

user_vertices = user_movie_matrix.select(col("userId").cast(StringType()).alias("id")).distinct().withColumn("bipartite", lit(0))
movie_vertices = user_movie_matrix.select(col("title").alias("id")).distinct().withColumn("bipartite", lit(1))
vertices = user_vertices.union(movie_vertices)

# https://stackoverflow.com/questions/39261370/unable-to-run-a-basic-graphframes-example

# Depending on your spark version, all you have to do is download the graphframe jar corresponding to your version
# of spark here https://spark-packages.org/package/graphframes/graphframes.

# Then you'll have to copy the jar downloaded to your spark jar directory and rename it to graphframes.jar.

# # # pyspark --packages graphframes:graphframes-0.8.4-spark3.5-s_2.12 --jars graphframes-0.8.4-spark3.5-s_2.12.jar
from graphframes import GraphFrame

user_movie_graph = GraphFrame(vertices, edges)

# Debug: Check the graph construction
print("First 10 nodes in the graph:")
user_movie_graph.vertices.show(10, truncate=False)
print("First 10 edges in the graph:")
user_movie_graph.edges.show(10, truncate=False)

# user_user_edges = user_movie_graph.edges.alias("e1") \
#     .join(user_movie_graph.edges.alias("e2"), col("e1.dst") == col("e2.dst")) \
#     .select(
#         col("e1.src").alias("src"),
#         col("e2.src").alias("dst"),
#         (col("e1.weight") + col("e2.weight")).alias("weight")
#     ).filter(col("src") != col("dst"))

# user_user_graph = GraphFrame(user_movie_graph.vertices, user_user_edges)

# # Debug: Check the graph construction
# print("First 10 nodes in the graph:")
# user_user_graph.vertices.show(10, truncate=False)
# print("First 10 edges in the graph:")
# user_user_graph.edges.show(10, truncate=False)

# Project movie-movie graph
movie_movie_edges = user_movie_graph.edges.alias("e1") \
    .join(user_movie_graph.edges.alias("e2"), col("e1.src") == col("e2.src")) \
    .select(
        col("e1.dst").alias("src"),
        col("e2.dst").alias("dst"),
        (col("e1.weight") + col("e2.weight")).alias("weight")
    ).filter(col("src") != col("dst"))

movie_movie_graph = GraphFrame(user_movie_graph.vertices, movie_movie_edges)

# Debug: Check the graph construction
print("First 10 nodes in the graph:")
movie_movie_graph.vertices.show(10, truncate=False)
print("First 10 edges in the graph:")
movie_movie_graph.edges.show(10, truncate=False)

def create_preference_vector(user_id, user_movie_graph):
    edges = user_movie_graph.edges.filter(col("src") == user_id).rdd.map(lambda row: (row["dst"], row["weight"])).collect()
    print(f"Preference vector for user {user_id}: {list(edges)[:10]}")
    tot = sum([weight for _, weight in edges])    
    print(f"Total weight for user {user_id}: {tot}")
    if tot > 0:
        return {movie: weight / tot for movie, weight in edges}
    else:
        movies = user_movie_graph.vertices.filter(col("bipartite") == 1).select("id").rdd.map(lambda row: row[0]).collect()
        return {movie: 1 / len(movies) for movie in movies}

def predict_user(user_id, user_movie_graph, movie_movie_graph):
    p_vec = create_preference_vector(user_id, user_movie_graph)
    print(f"Preference vector for user {user_id}: {list(p_vec)[:10]}")
    already_seen = [movie for movie, weight in p_vec.items() if weight > 0]
    print(f"Already seen movies for user {user_id}: {list(already_seen)[:10]}")
    if len(already_seen) == len(p_vec):
        return []
    pagerank_results = movie_movie_graph.pageRank(resetProbability=0.95, maxIter=20)
    item_rank = pagerank_results.vertices.select("id", "pagerank").rdd.map(lambda row: (row["id"], row["pagerank"])).collectAsMap()
    recommendations = sorted(
        (movie for movie in item_rank if movie not in already_seen),
        key=lambda x: item_rank[x], reverse=True
    )
    return recommendations

user = "10"
try: 
    s_t = predict_user(user, user_movie_graph, movie_movie_graph)
    print(f"Predicted movies for user {user}: {s_t[:10]}")
except Exception as e:
    print(f"Error: {e}")