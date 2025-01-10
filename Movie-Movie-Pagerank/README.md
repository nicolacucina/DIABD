
# **PageRank**  
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










## **Osservazioni e limiti**  

Per implementare PageRank nel contesto del sistema di raccomandazione, si è adottato un approccio basato su grafi, ma con alcune osservazioni:  

### **Proiezione Movie-Movie**  
1. **Proiezione in Python**:  
   La proiezione del grafo bipartito (utenti-film) in un sottografo movie-movie è stata effettuata usando una libreria Python. Tuttavia:  
   - Questa proiezione considera solamente i **vicini comuni** (utenti che hanno valutato entrambi i film) come misura di *similarità*. Questo approccio risulta piuttosto limitato in termini di semantica e qualità della misura.  
   - **Threshold**: Non è stato applicato alcun filtro per rimuovere archi con pesi bassi. Ad esempio, si potrebbe assumere che un film popolare sia stato valutato da circa il 20% del dataset e tagliare tutti gli archi con pesi inferiori a questa soglia. La mancanza di tale filtro ha portato a un numero eccessivo di archi nel grafo risultante (13 milioni).  

2. **Proiezione in Spark**:  
   La stessa libreria usata in Python è stata implementata in Spark. Tuttavia, in questo caso:  
   - Spark applica automaticamente un **filtraggio massivo** (da 13 milioni di archi in Python a circa 160.000 in Spark), riducendo notevolmente la complessità del grafo.  
   - Il filtraggio effettuato da Spark non è documentato o controllabile, ma risulta vantaggioso in termini di efficienza: con 160.000 archi, PageRank viene calcolato in **0.5 secondi**.  

### **Limitazioni di PageRank in Spark**  
Nonostante il filtraggio effettuato da Spark renda il problema computazionalmente più gestibile, già utilizzando il dataset *Small* emergono alcune criticità:  
1. **Differenze nei risultati**: La versione di PageRank implementata in Spark differisce da quella Python, producendo risultati non direttamente confrontabili.  
2. **Mancanza di personalizzazione**: La versione di PageRank in Spark non supporta il **vettore di personalizzazione**, fondamentale per adattare il ranking agli interessi specifici di un utente. Questo limita l’efficacia semantica del modello.  
3. **Problemi di convergenza**: PageRank in Spark non sembra riuscire a convergere, rendendo impossibile completare il calcolo.  

A causa di queste limitazioni, l’ analisi dei risultati è stata effettuata utilizzando **solo** la versione Python.  

### **Analisi dei Tempi di Calcolo**  
| **Metodo**     | **Numero di Archi** | **Tempo per Prediction** |
|-----------------|---------------------|--------------------------|
| Python  | ~13.000.000         | 15 s                     |
| Spark     | ~160.000            | 0.5 s                    |  

- **Dataset Big**:  
Per quanto riguarda l'analisi del dataset *Big*, esso si compone di **86.000 nodi** e **8 milioni di archi**. Dunque, se tale problema venisse affrontato con un approccio di *forte filtraggio* simile a quello di Spark (ad esempio limitando ad esempio a 100 il n° di archi per ogni film), sarebbe possibile stimare i tempi di calcolo anche per tale dataset nel seguente modo:  
 
  - Il calcolo delle previsioni per un singolo utente richiederebbe circa **~15 secondi**.  
  - Avendo in questo caso ~300.000 utenti, il calcolo complessivo richiederebbe **1.300 ore** su un cluster simile a quello usato.  
  - Questo dimostra che il problema è potenzialmente affrontabile in **tempi ragionevoli** per dataset di grandi dimensioni.  

### **Confronto con la Proiezione User-User**  
Un approccio alternativo basato su una proiezione **user-user** (dove si individuano gli utenti più simili tra loro sulla base dei film più visti) presenta vantaggi e limiti:  
- **Dataset Small**: Avendo 610 utenti e ~160.000 archi, il grafo user-user è *quasi completo* (essendo il n° di archi possibili ~180.000), ma rimane sufficientemente piccolo da rendere il calcolo di PageRank processabile in tempi praticamente immediati.  
- **Dataset Big**: Tuttavia con 300.000 utenti il problema diventa più complesso e la definizione di una metrica di similarità adeguata per la proiezione diventa fondamentale.  

#### **Strategia Finale**  
Una versione precedente prevedeva l’uso di PageRank due volte:  
1. Per individuare i 10 utenti **più simili** a un dato utente.  
2. Per classificare sulla base del rating **i film** visti da questi 10 utenti simili al fine di consigliare all'utente quelli che fra questi egli non ha già visto.  

Tuttavia, a causa delle performance descritte, questa soluzione non era gestibile.  

**Soluzione adottata**:  
- Si sono individuati i 10 utenti più simili con una singola esecuzione di PageRank.
- Tra i film a cui questi utenti hanno assegnato i punteggi più alti, ne vengono selezionati 10 in totale (uno per ogni utente simile) per generare l'elenco delle 10 raccomandazioni per l'utente target, escludendo i film già visti.
- Questo approccio ha migliorato significativamente l’efficienza senza compromettere la qualità delle raccomandazioni.  

