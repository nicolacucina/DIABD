# Analisi della complessità degli approcci usati

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


# Sviluppi futuri 

## Link Prediction 

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


## Consigli sulla base di utenti simili

Si è anche valutata la possibilità di integrare un approccio basato sulla *similarità* tra utenti, al fine di aumentare la rilevanza delle raccomandazioni. 
Questo metodo mira a individuare i **10 utenti** più **simili** all'utente target e, attraverso le loro preferenze, raccomandare film che il target non ha ancora visto. Ciò è possibile sfruttando l'algoritmo *PageRank personalizzato* sul grafo proiettato **user-user**: per il nostro utente target, che evidenzia i 10 utenti più simili  a lui.

Una volta ottenuti i 10 utenti più simili, il sistema può costruire un **preference vector** per l'utente target, considerando esclusivamente i film valutati da questi utenti simili. Successivamente, si esegue un PageRank sul grafo **movie-movie**, utilizzando il preference vector come punto di personalizzazione, per calcolare un ranking dei film potenzialmente interessanti. Infine fra questi film vengono esclusi quelli già visti dall'utente target, e come raccomandazioni finali si selezionano 10 film con il punteggio più alto tra i rimanenti.

Inoltre l'approccio consente di incorporare una *penalità* per la popolarità dei film, riducendo il bias verso contenuti estremamente popolari.

Tuttavia, questo approccio è stato escluso dalla versione finale del progetto per via della complessità computazionale che avrebbe comportato su dataset di grandi dimensioni. La necessità di:
1. **Proiettare e calcolare PageRank** sia sul grafo **user-user** sia sul grafo **movie-movie**;
2. **Gestire la penalizzazione per la popolarità** e la normalizzazione dei punteggi;
3. **Iterare il processo per ogni utente target e per ogni suo utente simile**;

avrebbe potuto portare a una complessità computazionale elevata, specialmente considerando grandi moli di dati reali.



# Riferimenti

[1] Banerjee, Suman, Jenamani, Mamata, e Pratihar, Dilip Kumar. "Properties of a projected network of a bipartite network." In *2017 International Conference on Communication and Signal Processing (ICCSP)*, pp. 0143-0147. 2017. doi: [10.1109/ICCSP.2017.8286734](https://doi.org/10.1109/ICCSP.2017.8286734).