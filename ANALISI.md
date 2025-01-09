# Analisi della complessità degli approcci usati
Sono stati adottati tre approcci principali per il sistema di raccomandazione:

## **Alternating Least Squares (ALS)**  
### **Formula**: ALS minimizza la funzione di costo:
$$\sum_{(u, i) \in D} (r_{ui} - \mathbf{x}_u^T \mathbf{y}_i)^2 + \lambda (\|\mathbf{x}_u\|^2 + \|\mathbf{y}_i\|^2)$$

Dove $\mathbf{x}_u$ e $\mathbf{y}_i$ rappresentano i vettori utente e item, $\lambda$ è il termine di regolarizzazione.
     
### **Complessità**:  
ALS alterna tra la risoluzione di due problemi di regressione lineare, ciascuno con una complessità di $O(k^2 m + k^3)$, dove:
- $k$ è il numero di fattori latenti;
- $m$ è il numero di righe nella matrice utente o film.  
     
Grazie all’implementazione distribuita di Spark, ALS è risultato scalabile anche con il dataset **Big**, completando l'addestramento in tempi ragionevoli.

## **PageRank**  
### **Formula**:  
$$p_{i} = \frac{1-d}{n} + d \sum_{j \rightarrow i} \frac{p_{j}}{m_{j}}
$$

Dove:  
- $d$ è il **fattore di damping**, con $0 < d < 1$, usato per gestire salti casuali;  
- $n$ è il numero totale di nodi nel grafo;  
- $L_{ij}$ rappresenta la connessione tra i nodi $i$ e $j$;  
- $m_{j}$ è il numero di connessioni totali del nodo $j$.  

Questo approccio consente di rappresentare anche il fatto che un utente  occasionalmente esplora film al di fuori delle proprie preferenze usuali.  

  
### **Complessità**:  

1. **Proiezione del grafo bipartito**  
La proiezione di un grafo bipartito su un set di nodi $U$ rispetto a un altro set $S$ comporta una complessità significativa. Secondo il paper di **Banerjee et al. (2017)** [1]:  
   - **Complessità temporale**: $O(n_1^2 n_2)$, dove:
     - $n_1 = |U|$, numero di nodi del set da proiettare;
     - $n_2 = |S|$, numero di nodi del set opposto.  
   - **Complessità spaziale**: $O(n_1^2)$, dato che viene creata una matrice di adiacenza di dimensione $n_1 \times n_1$.

2. **Algoritmo PageRank**  
   L'algoritmo iterativo di PageRank ha una complessità per iterazione di:
   $O(E + V)$
   Dove:  
   - $E$ è il numero di archi (valutazioni);  
   - $V$ è il numero di nodi (utenti e film).  
   
   Tuttavia, il numero di iterazioni necessarie per la convergenza può aumentare significativamente in grafi di grandi dimensioni.

3. **Complessità combinata**  
Combinando entrambe le operazioni:
- Proiezione: $O(n_1^2 n_2)$;  
- PageRank: $O(E + V)$ per iterazione,  

    Si ha quindi che l costo complessivo diventa proibitivo per dataset di grandi dimensioni e grafi bipartiti densi ($E \sim O(n_1 \cdot n_2))$. Per garantire scalabilità, è necessario adottare approcci ottimizzati o tecniche di riduzione della dimensionalità. 



## **SVD**
- **Formula**:  
La decomposizione si basa sulla rappresentazione della matrice $R$ come prodotto di tre matrici:
     $R = U \Sigma V^T$
Dove:
  - $U$ e $V$ contengono i vettori principali;
  - $\Sigma$ è una matrice diagonale dei valori singolari.

- **Complessità**:  
Il calcolo della decomposizione SVD ha una complessità di $O(m* n \cdot \min(m, n))$, dove:
  - $m$ e $n$ sono le dimensioni della matrice $R$.  

  Questo lo rende poco adatto per dataset di grandi dimensioni come il **Big**, dove la matrice è troppo grande per essere gestita efficientemente in memoria.
<!-- MAGARI UTILE METTERLO NEI RISULTATI???? CONSIDERAZIONI FINALI???

### Confronto tra approcci
- **ALS** ha dimostrato di essere scalabile grazie alla sua implementazione iterativa distribuita su Spark, rendendolo adatto anche per il dataset **Big**.  
- **PageRank** e **SVD**, pur essendo efficaci per dataset più piccoli, hanno fallito su dataset di grandi dimensioni a causa della complessità computazionale e della memoria richiesta. -->

## Analisi su Tempo e Memoria

L'analisi è stata condotta sui seguenti parametri:

- **Tempo di esecuzione e memoria** su dataset Small e conseguenti **stime** per il dataset Big basate sui risultati ottenuti nello Small;
- **RMSE** (Root Mean Squared Error) per il modello ALS, che ha dimostrato migliori performance rispetto agli altri approcci.
<!--DA VEDERE SE VERAMENTE USIAMO RMSE PER ALS, PER ORA NO, CASOMAI TOGLIERE -->

> Nota: Questa sezione sarà completata DOPO la raccolta dei dati.



# Sviluppi futuri con Link Prediction

Un'estensione interessante del progetto potrebbe essere rappresentata dall'implementazione della **Link Prediction** per predire nuovi collegamenti tra utenti e film non ancora valutati. Questo approccio consentirebbe di migliorare le raccomandazioni ottenute attraverso tecniche come PageRank. Sebbene non sia stato implementato/testato nel sistema attuale, sono state analizzate diverse metodologie per identificare quella più adatta al nostro contesto.  

Tra le tecniche considerate, si è ritenuto che l'indice di **Adamic-Adar** fosse il più promettente per la sua efficacia nell'analisi di grafi bipartiti come il grafo user-movie. Questo metodo calcola la **similarità** tra due nodi di un grafo in base ai loro **vicini comuni**, attribuendo un peso maggiore ai vicini con un basso grado, considerati più significativi.  

La formula per calcolare l'indice di Adamic-Adar tra due nodi $u$ e $v$ è:

$$
A(u, v) = \sum_{w \in N(u) \cap N(v)} \frac{1}{\log |N(w)|}
$$

Dove:
- $N(u)$ è l'insieme dei vicini del nodo $u$.
- $N(v)$ è l'insieme dei vicini del nodo $v$.
- $N(w)$ è l'insieme dei vicini del nodo $w$ (nodo comune tra $u$ e $v$).
- $|N(w)|$ rappresenta il grado del nodo $w$.

L'uso diretto dell'indice di Adamic-Adar nel grafo bipartito user-movie non è però possibile. 
Ciò è dovuto alla struttura del grafo bipartito che connette utenti a film, poiché non esistono **vicini comuni** tra un utente e un film che l'utente non ha ancora valutato. 
Di conseguenza, l'indice di Adamic-Adar non può essere utilizzato per predire direttamente nuovi collegamenti tra un utente e un film.  

Tuttavia, l'indice di Adamic-Adar potrebbe essere applicato alle **proiezioni del grafo bipartito**. In particolare:  
- Nel grafo **user-user**, che connette utenti che hanno valutato gli stessi film;  
- Nel grafo **movie-movie**, che collega film valutati dagli stessi utenti.  

In queste proiezioni, la presenza di vicini comuni rende l'uso dell'indice di Adamic-Adar una soluzione valida e utile per migliorare le raccomandazioni, rilevando relazioni latenti tra utenti o tra film.


## Riferimenti

[1] Banerjee, Suman, Jenamani, Mamata, e Pratihar, Dilip Kumar. "Properties of a projected network of a bipartite network." In *2017 International Conference on Communication and Signal Processing (ICCSP)*, pp. 0143-0147. 2017. doi: [10.1109/ICCSP.2017.8286734](https://doi.org/10.1109/ICCSP.2017.8286734).