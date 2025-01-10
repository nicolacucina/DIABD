
# **PageRank**  
 
Il problema viene modellato come un **grafo bipartito user-movie**, dove i nodi rappresentano **utenti** e **film**, mentre gli archi rappresentano i **ratings**, ponderati dai punteggi assegnati.  

Tuttavia, per gli scopi di questo progetto **PageRank non può essere applicato direttamente** su un grafo bipartito, poiché calcola l'importanza dei nodi basandosi su connessioni tra nodi dello stesso tipo. 
Perciò,  il grafo bipartito viene proiettato in un sottografo chiamato *movie-movie*, dove i nodi sono solamente i film, collegati da archi che indicano una **similarità**, derivata dagli utenti che hanno valutato entrambi.  

Questa proiezione permette di usare **PageRank** per calcolare un ranking dei film che tenga conto della loro importanza all'interno del grafo.

## **Formula**:  
$$p_{i} = \frac{1-d}{n} + d \sum_{j \rightarrow i} \frac{p_{j}}{m_{j}}
$$

Dove:  
- $d$ è il **fattore di damping**, con $0 < d < 1$, usato per gestire salti casuali;  
- $n$ è il numero totale di nodi nel grafo;  
- $L_{ij}$ rappresenta la connessione tra i nodi $i$ e $j$;  
- $m_{j}$ è il numero di connessioni totali del nodo $j$.  

Questo approccio consente di rappresentare anche il fatto che un utente  occasionalmente esplora film al di fuori delle proprie preferenze usuali.  


## **Complessità**:  

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

    Si ha quindi che l costo complessivo diventa proibitivo per dataset di grandi dimensioni e grafi bipartiti densi ($E \sim n^2)$. Per garantire scalabilità, è necessario adottare approcci ottimizzati o tecniche di riduzione della dimensionalità. 



## **Osservazioni e limiti**  
 
### **Proiezione sui nodi che rappresentano i film**  
1. **Proiezione in Python**:  
   La proiezione è stata effettuata usando la libreria Python *networkx*. Tuttavia questa proiezione conta solamente i **vicini comuni** (utenti che hanno valutato entrambi i film) come misura di *similarità*. Questo approccio risulta piuttosto limitato in termini di semantica e qualità della misura, infatti si ottengono 13 milioni di archi per i 9719 film.
   Per risolvere tale problema si sarebbe dovuta  applicare una threshold per rimuovere archi con pesi bassi. 
   Ad esempio, si potrebbe assumere che un film popolare sia stato valutato da circa il 20% del dataset e tagliare tutti gli archi con pesi inferiori a questa soglia. 

2. **Proiezione in Spark**:  
   In pyspark i grafi sono rappresentati tramite *graphframes*, e ciò costringe ad utilizzare i metodi di tale libreria, tra cui però non compare la proiezione di grafi biparititi. Pertanto si è cercato di replicare la funzione di *networkx* in pyspark. 
   Tuttavia, nonostante la funzione scritta sia praticamente identica a quella di *networkx*, il risultato ottenuto è molto diverso: difatti si passa da 13 milioni di archi a circa 160.000, riducendo notevolmente la complessità del grafo, ma non risulta chiaro il motivo, anche data la lunga catena di conversione fra i vari stack software.


#### **Limitazioni di PageRank in Spark**  
Utilizzando il dataset *Small* emergono alcune criticità, legate al fatto che la versione di PageRank implementata in Spark differisce da quella Python. Infatti si sono ottenuti risultati diversi, dal momento che in Spark non è supportato il **vettore di personalizzazione**, fondamentale per adattare il ranking agli interessi specifici di un utente. 

Inoltre l'algoritmo in Spark ha avuto difficoltà a convergere, rendendo impossibile completare il calcolo.  
A causa di queste limitazioni, l’ analisi dei risultati è stata effettuata utilizzando **solo** la versione Python.  

#### **Analisi dei Tempi di Calcolo**  

- **Dataset Small**

    | **Metodo**     | **Numero di Archi** | **Tempo per Prediction** |
    |-----------------|---------------------|--------------------------|
    | Python  | ~13.000.000         | 15 s                     |
    | Spark     | ~160.000            | 0.5 s                    |  

- **Dataset Big**:  
Per quanto riguarda l'analisi del dataset *Big*, esso si compone di **86.000 nodi** e **8 milioni di archi**. Dunque, se tale problema venisse affrontato con un approccio di *forte filtraggio* simile a quello di Spark (ad esempio limitando ad esempio a 100 il n° di archi per ogni film), sarebbe possibile stimare i tempi di calcolo anche per tale dataset nel seguente modo:  
 
  - Il calcolo delle previsioni per un singolo utente richiederebbe circa **~15 secondi**.  
  - Avendo in questo caso ~300.000 utenti, il calcolo complessivo richiederebbe **1.300 ore** su un cluster simile a quello usato.  
  - Questo dimostra che il problema è potenzialmente affrontabile in **tempi ragionevoli** per dataset di grandi dimensioni.  

### **Confronto con la proiezione sui nodi che rappresentano gli utenti**  
Un approccio alternativo mira a creare raccomandazioni sfruttando la *similarità* tra gli utenti, sulla base dei film da loro visti.
Questo metodo individua i **10 utenti** più **simili** all'utente target e, attraverso le loro preferenze, gli consiglia dei film che non ha ancora visto. 
Ciò è possibile calcolando *PageRank* sul grafo proiettato **user-user**.

Esso presenta vantaggi e limiti:  
- **Dataset Small**: Avendo 610 utenti e ~160.000 archi, il grafo user-user è *quasi completo* (essendo il n° di archi possibili ~180.000), ma rimane sufficientemente piccolo da rendere il calcolo di PageRank processabile in tempi praticamente immediati.  
- **Dataset Big**: Tuttavia con 300.000 utenti il problema diventa più complesso e la definizione di una metrica di similarità adeguata per la proiezione diventa fondamentale.  

Inizialmente si era pensato di usare PageRank due volte: la prima per individuare i 10 utenti **più simili** a un dato utente, mentre la seconda per classificare i film visti da tali utenti sulla base del rating, per consigliare all'utente quelli che fra questi non ha già visto.   Tuttavia, a causa delle performance descritte in precedenza, calcolare PageRank per due volte non era computazionalmente gestibile.  

Pertanto, si è scelto di adottare un approccio più semplice che prevede una **singola** esecuzione di tale algoritmo, appunto per individuare i 10 utenti più simili al target.
La differenza è che a questo punto, tra i film a cui questi utenti hanno assegnato i punteggi più alti, ne vengono selezionati 10 in totale (uno per ogni utente simile) per creare l'elenco delle raccomandazioni per l'utente target, escludendo i film già visti.
Tale approccio ha migliorato significativamente l’efficienza senza compromettere la qualità delle raccomandazioni.  

## **Analisi su Tempo e Memoria** 



### **Dataset Small**  

Per il dataset *Small*, si sono misurati i tempi di esecuzione e la memoria utilizzata per ogni operazione fondamentale nel processo di raccomandazione, confrontando i due approcci basati su PageRank:  
1. **Proiezione su movie-movie**  
2. **Proiezione su user-user**  

Di seguito vengono riportati i risultati ottenuti:

| **Operazione**                          | **Tempo** | **Memoria**  | **Nodi**       | **Archi**       |
|-----------------------------------------|-----------|--------------|----------------|-----------------|
| Creazione grafo bipartito (user-movie)  | 4 s       | 6 MB         | 610 (user), 9719 (movie) | 100.000         |
| Creazione grafo proiettato (movie-movie)| 150 s     | 700 MB       | 9719 (movie)   | 13.154.589      |
| Creazione grafo proiettato (user-user)  | 5 s       | 8.7 MB       | 610 (user)     | 164.054         |
| PageRank su grafo movie-movie (1 utente)| 60 s      | -            | 9719 (movie)   | 13.154.589      |
| PageRank su grafo user-user (1 utente) + Raccomandazione | 0.5 s     | -            | 610 (user)     | 164.054         |
| **PageRank complessivo (movie-movie)**  | 36.600 s  | -            | 9719 (movie)   | 13.154.589      |
| **PageRank complessivo (user-user)**    | ~5 min    | -            | 610 (user)     | 164.054         |


---

### **Confronto: Proiezione movie-movie vs user-user**

La proiezione su **movie-movie** genera un grafo estremamente denso con **13.154.589 archi**, a fronte dei soli **164.054 archi** del grafo proiettato user-user. Questo comporta:  
- un **aumento della memoria**: da 8.7 MB (user-user) a 700 MB (movie-movie).  
- Tempi di calcolo significativamente più alti, dato che PageRank sul grafo movie-movie richiede **36.600 secondi** per tutti gli utenti, contro **5 minuti** nel caso del grafo user-user.  

---

### **Dataset Big**

Per **stimare** i tempi e l'occupazione in memoria nel caso del dataset *Big*, si deve tener conto dell'aumento delle seguenti dimensioni rispetto allo *Small*:  
- **Utenti**: da 610 a **330.000** (fattore di crescita: ~500x).  
- **Film**: da 9719 a **86.000** (fattore di crescita: ~10x).  
- **Relazioni**: da 100.000 a **33 milioni** (fattore di crescita: ~100x).  


1. **Grafo bipartito user-movie**  
   - **Tempo stimato**: ~2000 s (ipotizzando crescita lineare rispetto al numero di relazioni).  
   - **Memoria stimata**: ~600 MB.  

2. **Grafo proiettato movie-movie**  
   - **Tempo stimato**: ~15 ore (150 s x 100).  
   - **Memoria stimata**: ~70 GB.  

3. **PageRank su grafo movie-movie (per tutti gli utenti)**  
   - **Tempo stimato**: ~500 giorni (36.600 s x 500).  

4. **Grafo proiettato user-user**  
   - **Tempo stimato**: ~25 min (5 s x 500).  
   - **Memoria stimata**: ~4 GB.  

5. **PageRank su grafo user-user (per tutti gli utenti)**  
   - **Tempo stimato**: ~42 ore (5 min x 500).  

---

### **Osservazioni**  
L'approccio **user-user** è significativamente più scalabile, sia in termini di memoria che di tempo di esecuzione, rispetto all'approccio **movie-movie**. 
Inoltre il grafo user-user rimane processabile con risorse ragionevoli anche per dataset grandi, grazie alla sua struttura molto meno densa.  
Il grafo movie-movie risulta impraticabile per dataset Big senza tecniche di riduzione della dimensionalità (ad esempio, thresholding sugli archi).  





## **Sviluppi futuri: Link Prediction**

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





# Riferimenti

[1] Banerjee, Suman, Jenamani, Mamata, e Pratihar, Dilip Kumar. "Properties of a projected network of a bipartite network." In *2017 International Conference on Communication and Signal Processing (ICCSP)*, pp. 0143-0147. 2017. doi: [10.1109/ICCSP.2017.8286734](https://doi.org/10.1109/ICCSP.2017.8286734).