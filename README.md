### Datasets

Netflix Prize Dataset (~ 2GB): https://www.kaggle.com/datasets/netflix-inc/netflix-prize-data
MovieLens 100k movie reatings (~ 5MB): https://grouplens.org/datasets/movielens/100k/

### Filtering

- Collaborative Filtering

- - SVD / ALS / Matrix Factorization (forse Collaborative Filtering da quello che leggo ma guardare meglio i calcoli)
- - - https://github.com/alicefortuni/MovieRecommenderVis/tree/master
- - - Netflix Prize Solution : https://pantelis.github.io/cs301/docs/common/lectures/recommenders/netflix/
- - - https://builtin.com/articles/svd-algorithm
- - - https://github.com/adinmg/movie_recommender_system  ---> forse molto utile per svd, collaborative filtering e vector based

- - PageRank-based Filtering
- - - https://medium.com/eni-digitalks/a-simple-recommender-system-using-pagerank-4a63071c8cbf
- - - https://github.com/pranay-ar/PageRank-Recommendation-System/blob/main/src/main/scala/MovieLensPageRank.scala

- Content-based Filtering
- - - https://github.com/DATUMBRIGHT/content-based-movie-recommendation-system (sembra complesso ma completo come sistema di raccomandazione)

- - Item-based Filtering
- - - Serve il calcolo della similarità tra gli item(movies), se non è presente nel dataset facciamo SVD?
- - - https://www.stratascratch.com/blog/step-by-step-guide-to-building-content-based-filtering/
- - - https://www.scaler.com/topics/machine-learning/content-based-filtering/

- Hybrid Filtering

- Vector-Based Recommendation Systems: 
- - - https://www.e2enetworks.com/blog/how-to-create-a-vector-based-recommendation-system
- - - https://towardsdatascience.com/how-to-create-a-vector-based-movie-recommendation-system-b6d4f7582d66 con repo github: https://github.com/arditobryan/Projects/tree/master/20211126_movie_plot_transformers

- K-means-based Filtering

### Ranking

- Popularity-based Ranking
- KNN-based Ranking
- Matrix Factorization-based Ranking
- K-means-based Ranking
- PageRank-based Ranking

### Links

- Definition : https://spotintelligence.com/2024/07/26/ranking-algorithms/#What_are_the_Types_of_Ranking_Algorithms
- Correlation-based Ranking : https://www.geeksforgeeks.org/python-implementation-of-movie-recommender-system/
- Github Topic: https://github.com/topics/movie-recomendation-system
- Machine Learning : https://github.com/ankitacoder3/Movie-Recommendation-System-MOVICO
- Paper confronting different methods: https://pmc.ncbi.nlm.nih.gov/articles/PMC9269752/
- Machine-Learning Collaborative Filtering: https://www.freecodecamp.org/news/how-to-build-a-movie-recommendation-system-based-on-collaborative-filtering/
- Link Prediction : https://paperswithcode.com/task/link-prediction
- Link Prediction Survey : https://link.springer.com/article/10.1007/s11227-023-05591-8
- Link Prediction: https://github.com/Cloudy1225/Awesome-Link-Prediction
- Link Prediction for PageRank Fairness: https://github.com/ksemer/fairPRrec
- Matrix Completion for Recommended Systems: https://chenzl23.github.io/assets/pdf/ReviewOnRS-KAIS2022.pdf