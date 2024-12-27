**ADAMIC ADAR PER LA LINK PREDICTION:**
The Adamic/Adar Index predicts links in a graph according to the amount of shared links between two nodes. The index sums up the reciprocals of the logarithm of the degree of all common neighbors between two nodes u and v.
Adamic-Adar è appropriato se: 
- un grafo bipartito o sparso.
- si può evitare il bias verso gli hub.
- se non si hanno informazioni di comunità o non si vuole aggiungere complessità

Link: 
- https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.link_prediction.adamic_adar_index.html#networkx.algorithms.link_prediction.adamic_adar_index
- https://networkit.github.io/dev-docs/notebooks/LinkPrediction.html
- Adamic-Adar in Neo4j: https://neo4j.com/docs/graph-data-science/current/alpha-algorithms/adamic-adar/
- Link Prediction in Neo4j with Adamic Adar: https://medium.com/neo4j/link-prediction-with-neo4j-part-1-an-introduction-713aa779fd9
- 

**MOTIVI PER POCHE CONNESSIONI PREDETTE con ADAMIC ADAR:**  

1) SPARSITA' DEL GRAFO =  La maggior parte degli utenti probabilmente ha valutato solo una piccola frazione dei 9000 film disponibili. Ad esempio, se ogni utente ha valutato solo  n<<9000 film, il numero di vicini comuni tra due nodi diventa piccolo. Adamic-Adar dipende dai vicini comuni, quindi il numero di connessioni predette sarà limitato dalla sparsità.   

2) STRUTTURA GRAFO = La proiezione riduce drasticamente il numero di nodi e connessioni considerati: 
- User-User projection: Due utenti sono collegati solo se hanno visto (e valutato) lo stesso film.
- Movie-Movie projection: Due film sono collegati solo se hanno ricevuto valutazioni dagli stessi utenti.
Questo riduce enormemente il numero di coppie di nodi su cui applicare Adamic-Adar.  

3)  FILTER =  se tolgo il ".filter(score>0)" allora tutte le coppie di nodi con almeno un vicino comune verrebbero considerate, ma molte di queste potrebbero avere punteggi insignificanti (vicini comuni con grado molto alto, che diluiscono il punteggio)--> infatti toglierlo fa passare appunto da 164.054 a 185.745 connessioni.