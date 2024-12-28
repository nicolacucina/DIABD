import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# Caricamento dei dati
ratings = pd.read_csv('ratings.csv')
movies = pd.read_csv('movies.csv')

# Merge dei dataset ratings e movies
user_movie_matrix = ratings.merge(movies, on="movieId", how="inner")

# Mappatura dei punteggi
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
user_movie_matrix['weight'] = user_movie_matrix['rating'].map(mapping_score)

# Creazione degli edge
edges = user_movie_matrix[['userId', 'movieId', 'weight']].rename(
    columns={'userId': 'src', 'movieId': 'dst'}
)
edges['src'] = edges['src'].astype(str)
edges['dst'] = edges['dst'].astype(str)

# Creazione dei vertici
user_vertices = pd.DataFrame(user_movie_matrix['userId'].astype(str).unique(), columns=['id'])
user_vertices['bipartite'] = 0

movie_vertices = pd.DataFrame(user_movie_matrix['movieId'].astype(str).unique(), columns=['id'])
movie_vertices['bipartite'] = 1

vertices = pd.concat([user_vertices, movie_vertices], ignore_index=True)

# Creazione del grafo bipartito
user_movie_graph = nx.Graph()
for _, edge in edges.iterrows():
    user_movie_graph.add_edge(edge['src'], edge['dst'], weight=edge['weight'])

# Proiezione user-user
def project_user_user_graph(user_movie_graph):
    user_user_edges = []
    users = [node for node, data in user_movie_graph.nodes(data=True) if data.get('bipartite') == 0]
    for i, u1 in enumerate(users):
        for u2 in users[i+1:]:
            common_movies = set(user_movie_graph.neighbors(u1)).intersection(user_movie_graph.neighbors(u2))
            weight = sum(
                user_movie_graph[u1][movie]['weight'] + user_movie_graph[u2][movie]['weight']
                for movie in common_movies
            )
            if weight > 0:
                user_user_edges.append((u1, u2, weight))
    user_user_graph = nx.Graph()
    user_user_graph.add_weighted_edges_from(user_user_edges)
    return user_user_graph

user_user_graph = project_user_user_graph(user_movie_graph)

# Proiezione movie-movie
def project_movie_movie_graph(user_movie_graph):
    movie_movie_edges = []
    movies = [node for node, data in user_movie_graph.nodes(data=True) if data.get('bipartite') == 1]
    for i, m1 in enumerate(movies):
        for m2 in movies[i+1:]:
            common_users = set(user_movie_graph.neighbors(m1)).intersection(user_movie_graph.neighbors(m2))
            weight = sum(
                user_movie_graph[user][m1]['weight'] + user_movie_graph[user][m2]['weight']
                for user in common_users
            )
            if weight > 0:
                movie_movie_edges.append((m1, m2, weight))
    movie_movie_graph = nx.Graph()
    movie_movie_graph.add_weighted_edges_from(movie_movie_edges)
    return movie_movie_graph

movie_movie_graph = project_movie_movie_graph(user_movie_graph)

# Funzione per calcolare il vettore di preferenze
def create_preference_vector(user_id, user_movie_graph):
    user_node = str(user_id)
    edges = [(neighbor, user_movie_graph[user_node][neighbor]['weight']) for neighbor in user_movie_graph.neighbors(user_node)]
    tot = sum(weight for _, weight in edges)
    if tot > 0:
        return {movie: weight / tot for movie, weight in edges}
    else:
        movies = [n for n, data in user_movie_graph.nodes(data=True) if data.get('bipartite') == 1]
        return {movie: 1 / len(movies) for movie in movies}

# Funzione di predizione
def predict_user(user_id, user_movie_graph, movie_movie_graph):
    p_vec = create_preference_vector(user_id, user_movie_graph)
    already_seen = [movie for movie, weight in p_vec.items() if weight > 0]
    if len(already_seen) == len(p_vec):
        return []
    pagerank = nx.pagerank(movie_movie_graph, alpha=0.95)
    item_rank = sorted(
        [(movie, rank) for movie, rank in pagerank.items() if movie not in already_seen],
        key=lambda x: x[1], reverse=True
    )
    return [movie for movie, _ in item_rank[:10]]

# Calcolo dell'indice di Adamic-Adar
def calculate_adamic_adar(graph):
    scores = []
    for u, v in nx.non_edges(graph):
        common_neighbors = set(nx.common_neighbors(graph, u, v))
        if common_neighbors:
            score = sum(1 / np.log(len(list(graph.neighbors(w)))) for w in common_neighbors)
            scores.append((u, v, score))
    return scores

# Aggiunta di link predetti
def add_predicted_links(graph, predicted_edges, threshold):
    for u, v, score in predicted_edges:
        if score > threshold:
            graph.add_edge(u, v, weight=score)
    return graph

# Uso delle funzioni
adamic_adar_scores = calculate_adamic_adar(user_movie_graph)
user_movie_graph_extended = add_predicted_links(user_movie_graph, adamic_adar_scores, 0.5)

# Predizione per un utente
user = 10
recommended_movies = predict_user(user, user_movie_graph_extended, movie_movie_graph)
print(f"Recommended movies for user {user}: {recommended_movies}")
