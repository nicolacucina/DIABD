To create a bipartite graph in Neo4j where users and movies are separated into two groups and the links are given by the ratings, you can use the following Cypher queries:
- Load the CSV files and create nodes for users and movies:

```sql
LOAD CSV WITH HEADERS FROM "file:///C:/movies.csv" AS line
MERGE (m:Movie {movieId: line.movieId, title: line.title})
```

```sql
LOAD CSV WITH HEADERS FROM "file:///C:/ratings.csv" AS line
MERGE (u:User {userId: line.userId})
```

- Create relationships between users and movies based on the ratings:

```sql
LOAD CSV WITH HEADERS FROM "file:///C:/ratings.csv" AS line
MATCH (u:User {userId: line.userId}), (m:Movie {movieId: line.movieId})
MERGE (u)-[:RATED {rating: toFloat(line.rating)}]->(m)
```

These queries will create a bipartite graph with User and Movie nodes and RATED relationships that include the rating given by the user to the movie

To project the bipartite graph onto the two different sets of points (users and movies), you can use the following Cypher queries:

- Project the bipartite graph onto the user nodes:

```sql
MATCH (u1:User)-[r1:RATED]->(m:Movie)<-[r2:RATED]-(u2:User)
WHERE u1 <> u2
MERGE (u1)-[s:SIMILAR]->(u2)
ON CREATE SET s.commonMovies = 1
ON MATCH SET s.commonMovies = s.commonMovies + 1
```
Project the bipartite graph onto the movie nodes:

```sql
MATCH (m1:Movie)<-[r1:RATED]-(u:User)-[r2:RATED]->(m2:Movie)
WHERE m1 <> m2
MERGE (m1)-[s:SIMILAR]->(m2)
ON CREATE SET s.commonUsers = 1
ON MATCH SET s.commonUsers = s.commonUsers + 1
```

These queries will create SIMILAR relationships between users and between movies based on the common movies they have rated and the common users who have rated them, respectively.