# Movie Recommendation System

![Testo Alternativo](images/movie_rec_intro.jpg)

## Introduzione
Lo scopo di questo progetto è sviluppare un sistema di raccomandazione di film che offra suggerimenti personalizzati agli utenti, basandosi sulle loro preferenze riguardanti i film che hanno già visto e valutato.

Per raggiungere tale obiettivo sono state integrate diverse tecnologie: 
- **Spark** e **Hadoop** per il processamento distribuito dei dati, garantendo così la scalabilità necessaria per gestire grandi volumi di informazioni. <!--BAH SARA' FORSE VERO???abbiamo scalato bene?-->
- **Neo4j** viene impiegato per rappresentare e analizzare le relazioni tra utenti e film, essendo particolarmente adatto a gestire i grafi. <!--Da riscrivere meglio after Neo4j-->


## Datasets 

Inizialmente, l'intento era quello di utilizzare il **Netflix Prize Dataset** (~2 GB), oggetto di una competizione tenutasi su larga scala. Tuttavia, per motivi di praticità e di testing iniziale, si è scelto di adottare il **MovieLens Dataset**, disponibile in due varianti:

- **Small**: 100.000 valutazioni fatte a 9.000 film da parte di 600 utenti (~1 MB);
- **Full**: circa 33.000.000 valutazioni fatte a 86.000 film da parte di 330.975 utenti (~28 GB).

Entrambe le versioni sono reperibili sul sito ufficiale di GroupLens: [MovieLens Dataset](https://grouplens.org/datasets/movielens/latest/). Per il progetto si è inizialmente utilizzata la versione small per testare e ottimizzare l'implementazione, al fine di  scalare successivamente alla versione big. <!--Eh dove possibile però perché poi crasha-->

Il **MovieLens Dataset** è composto da diversi file che descrivono valutazioni, film e altri metadati.
In particolare, i file utilizzati sono:

- **`ratings.csv`**: contiene informazioni riguardanti le valutazioni che gli utenti hanno fornito ai film visti. Questo file include 100.836 record e presenta i seguenti campi:
  - **userId**: identificativo univoco dell'utente;
  - **movieId**: identificativo univoco del film;
  - **rating**: valutazione assegnata dall'utente al film, espressa su una scala da 0.5 a 5.0;
  - **timestamp**: data e ora in formato timestamp in cui la valutazione è stata registrata.

- **`movies.csv`**: include i dettagli sui film, con un totale di 9.000 record. I campi principali sono:
  - **movieId**: identificativo univoco del film, che corrisponde al campo `movieId` in `ratings.csv`;
  - **title**: titolo del film;
  - **genres**: generi del film, separati da un carattere "|" (ad esempio, *Action|Adventure|Fantasy*).

Si è scelto il dataset MovieLens anche perché rende possibile la riproduzione della struttura del **Netflix Prize Dataset**. 
La struttura del dataset di Netflix è infatti la seguente:  
- **CustomerID**: identificativo univoco dell'utente;  
- **Rating**: valutazione assegnata, su una scala intera da 1 a 5;  
- **Date**: data della valutazione, nel formato `YYYY-MM-DD`.

Le caratteristiche principali del dataset di Netflix includono:  
- ID dei film che variano da 1 a 17.770 in ordine sequenziale;  
- CustomerID che vanno da 1 a 2.649.429, con alcune lacune nei numeri;  
- Un totale di 480.189 utenti attivi.  

Grazie all'operazione di *pivot* sui dati di MovieLens, è possibile generare una struttura dati analoga, mappando gli utenti e i film secondo una rappresentazione coerente con quella di Netflix, semplificando così le analisi comparative e l'estensione del sistema di raccomandazione.  

## Implementazione
Sono stati adottati tre approcci principali per il sistema di raccomandazione:

1. **Alternating Least Squares (ALS)**  
ALS è un algoritmo di fattorizzazione delle matrici utilizzato per la raccomandazione collaborativa (*Collaborative Filtering*). 
La tecnica suddivide la matrice delle valutazioni in due matrici più piccole (utenti e film), riducendo le dimensioni e preservando le relazioni latenti.
   
  - **Formula**: ALS minimizza la funzione di costo:
     $$\sum_{(u, i) \in D} (r_{ui} - \mathbf{x}_u^T \mathbf{y}_i)^2 + \lambda (\|\mathbf{x}_u\|^2 + \|\mathbf{y}_i\|^2)$$

     Dove $\mathbf{x}_u$ e $\mathbf{y}_i$ rappresentano i vettori utente e item, $\lambda$ è il termine di regolarizzazione.
     
     
   - **Complessità**:  
     ALS alterna tra la risoluzione di due problemi di regressione lineare, ciascuno con una complessità di $O(k^2 m + k^3)$, dove:
     - $k$ è il numero di fattori latenti;
     - $m$ è il numero di righe nella matrice utente o film.  
     
     Grazie all’implementazione distribuita di Spark, ALS è risultato scalabile anche con il dataset **Big**, completando l'addestramento in tempi ragionevoli.

2. **PageRank**  
Utilizzato per misurare l'importanza relativa dei nodi all'interno di un grafo bipartito (utenti-film). Dopo la conversione dei dati in grafi con la libreria *GraphFrames*:
   - Gli archi rappresentano le valutazioni (con peso derivato dal rating).
   - PageRank classifica film e utenti in base alla loro influenza. <!--NON CREDO SIA PROPRIO VERO, RIVEDI A MENTE LUCIDA--> 

    Il metodo si basa su un modello iterativo che tiene conto delle connessioni tra i nodi. 

  - **Formula**:  
  $p_{i} = \frac{1-d}{n} + d \sum_{j \rightarrow i} \frac{p_{j}}{m_{j}}
  $

    Dove:  
    - $d$ è il **fattore di damping**, con $0 < d < 1$, usato per gestire salti casuali;  
    - $n$ è il numero totale di nodi nel grafo;  
    - $L_{ij}$ rappresenta la connessione tra i nodi $i$ e $j$;  
    - $m_{j}$ è il numero di connessioni totali del nodo $j$.  

    Questo approccio consente di rappresentare anche il fatto che un utente  occasionalmente esplora film al di fuori delle proprie preferenze usuali.  
  I dettagli completi del calcolo e dell'implementazione verranno discussi nel notebook dedicato. 
  
  - **Complessità**:  
      L'algoritmo iterativo di PageRank ha una complessità di $O(E + V)$ per iterazione, dove:
      - $E$ è il numero di archi (valutazioni);
      - $V$ è il numero di nodi (utenti e film).  
      Tuttavia, il numero di iterazioni richiesto per la convergenza può aumentare significativamente in grafi molto grandi, rendendo l'approccio non praticabile con il dataset **Big**.



3. **SVD (Singular Value Decomposition)**    
SVD scompone la matrice delle valutazioni per estrarre feature latenti che rappresentano correlazioni tra utenti e film.  
- **Formula**:  
La decomposizione si basa sulla rappresentazione della matrice \(R\) come prodotto di tre matrici:
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

## Architettura del sistema

[INSERIRE IMG SCHEMA CLUSTER]
Il sistema viene implementato realizzando un cluster Hadoop con un nodo Master (Namenode) e due nodi Slave (Datanode), connessi tramite rete bridgiata. Il Master agisce anche come Resource Manager, mentre si utilizza HDFS per l'archiviazione distribuita del dataset MovieLens.

L'applicazione inoltre sfrutta YARN per la gestione delle risorse e Spark per l'elaborazione distribuita, integrandosi con il Graph Database Neo4j per le analisi.
[TODO]


## Prerequisiti
In questa sezione sono elencati i prerequisiti software necessari per l'esecuzione del sistema:
1. **Apache Hadoop 3.2.4**; [[hadoop](https://hadoop.apache.org/release/3.2.4.html)]
2. **Apache Spark 3.5.4** [[spark](https://spark.apache.org/downloads.html)]
3. **Java 8**;  [[java](https://www.oracle.com/java/technologies/javase/javase8u211-later-archive-downloads.html)]
4. **Neo4j 1.6.1**;

Il programma di installazione di Java installerà automaticamente il jdk in C:\Program Files\Java\jdk1.8.0_351, mentre la destinazione JRE può essere modificata. 
I file di Hadoop e Spark possono essere estratti in qualsiasi cartella, ma si consiglia di estrarli nella root del disco per evitare percorsi lunghi.


## Setup/Configurazione del Cluster

**1. Creazione di un Utente Dedicato per Hadoop**

Per motivi di sicurezza, è consigliabile creare un utente separato per Hadoop:

```bash
sudo usermod -aG sudo master
```

**2. Comunicazione fra le macchine tramite SSH**
 

Hadoop utilizza SSH per la comunicazione tra i nodi. È quindi necessario configurare l'accesso SSH *Passwordless* per l'utente Hadoop. 
Per semplificare la configurazione, tutti i dispositivi del cluster (nodo master e due nodi worker) utilizzano lo stesso nome utente (`master`), 
la stessa password e una configurazione condivisa delle chiavi pubbliche.  
Nonostante ciò, le tre macchine risultano comunque riconoscibili, come risulta nel file `/etc/hosts` presente in tutti i nodi:  
   ```text
   <IP_master>    master
   <IP_worker1>   worker1
   <IP_worker2>   worker2
   ```  

Con questa configurazione, Hadoop sarà in grado di comunicare tra i nodi senza richiedere continuamente l'inserimento di password, 
semplificando l'implementazione e l'esecuzione dei servizi.

**3. Download e Installazione di Hadoop**

- E' necessario scaricare l'ultima versione stabile di Hadoop dal sito ufficiale:

  ```bash
  wget https://downloads.apache.org/hadoop/common/hadoop-3.2.4/hadoop-3.2.4.tar.gz
  ```

- Successivamente, estrarre l'archivio e spostare i file:

  ```bash
  tar -xvzf hadoop-3.2.4.tar.gz
  mv hadoop-3.2.4 ~/hadoop
  ```

- Si è creato uno script `custom-env.sh` in cui sono state inserite tutte le variabili d'ambiente utili per Hadoop, Spark e Java.
[RICONTROLLARE CHE SIA TIPO COSI':]
  ```bash
  export HADOOP_HOME=~/hadoop
  export HADOOP_INSTALL=$HADOOP_HOME
  export HADOOP_MAPRED_HOME=$HADOOP_HOME
  export HADOOP_COMMON_HOME=$HADOOP_HOME
  export HADOOP_HDFS_HOME=$HADOOP_HOME
  export YARN_HOME=$HADOOP_HOME
  export HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
  export PATH=$PATH:$HADOOP_HOME/sbin:$HADOOP_HOME/bin
  export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
  ```


**4. Configurazione dei File di Hadoop**
A questo punto per configurare un ambiente Hadoop è sufficiente modificare una serie di file di configurazione:
- Nel file `hadoop-env.sh` va specificato il percorso di Java:

  ```bash
  nano $HADOOP_HOME/etc/hadoop/hadoop-env.sh
  ```

  Assicurarsi che la riga seguente punti al percorso corretto di Java:

  ```bash
  export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
  ```

- Nel file `core-site.xml` aggiungere:

  ```xml
  <configuration>
    <property>
      <name>fs.defaultFS</name>
      <value>hdfs://localhost:9000</value>
    </property>
  </configuration>
  ```

- Nel file `hdfs-site.xml`:

  ```xml
  <configuration>
    <property>
      <name>dfs.replication</name>
      <value>1</value>
    </property>
    <property>
      <name>dfs.namenode.name.dir</name>
      <value>file:///C:/Hadoop/hadoop-3.2.4/data/namenode</value>
    </property>
    <property>
      <name>dfs.datanode.data.dir</name>
      <value>file:///C:/Hadoop/hadoop-3.2.4/data/datanode</value>
    </property>
  </configuration>
  ```

- Nel file `mapred-site.xml`:

  ```xml
  <configuration>
    <property>
      <name>mapreduce.framework.name</name>
      <value>yarn</value>
    </property>
  </configuration>
  ```

- Nel file `yarn-site.xml`:

  ```xml
  <configuration>
  <property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
  </property>
  <property>
    <name>yarn.nodemanager.auxservices.mapreduce.shuffle.class</name>  
    <value>org.apache.hadoop.mapred.ShuffleHandler</value>
  </property>
</configuration>
  ```

**5. Creazione delle directories**
A questo punto creare le cartelle `namenode` e `datanode` nella cartella `data`:
```shell
> mkdir %HADOOP_HOME%\data\namenode
> mkdir %HADOOP_HOME%\data\datanode
```

**6. Formattazione del NameNode**

Prima di avviare Hadoop, è necessario formattare il NameNode:

```bash
hdfs namenode -format
```

**7. Avvio del Cluster Hadoop**

A questo punto verificare che l'istallazione sia andata a buon fine:
```shell
> hadoop version
```

E per avviare i servizi Hadoop eseguire:
```bash
start-dfs.sh
start-yarn.sh
```

A questo punto il servizio è in esecuzione presso: `http://localhost:8088/`



 




## Analisi
L'analisi è stata condotta sui seguenti parametri:

- **Tempo di esecuzione e memoria** su dataset Small e conseguenti **stime** per il dataset Big basate sui risultati ottenuti nello Small;
- **RMSE** (Root Mean Squared Error) per il modello ALS, che ha dimostrato migliori performance rispetto agli altri approcci.
<!--DA VEDERE SE VERAMENTE USIAMO RMSE PER ALS, PER ORA NO, CASOMAI TOGLIERE -->

> Nota: Questa sezione sarà completata DOPO la raccolta dei dati.

## Sviluppi futuri con Link Prediction

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





## LINK UTILI e TOPIC:




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

- - Link-Prediction Filtering
nel senso che si cerca di prevedere la probabilità di una relazione tra due nodi, per noi questa relazione è la valutazione di un film da parte di un utente, quindi se uso svd per prevedere la valutazione di un film da parte di un utente, posso usare link-prediction per fare la stessa cosa e confronto

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