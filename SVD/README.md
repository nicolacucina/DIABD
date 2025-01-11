# **SVD**

## **Formula**:  
La decomposizione si basa sulla rappresentazione della matrice $R$ come prodotto di tre matrici:
     $R = U \Sigma V^T$
Dove:
  - $U$ e $V$ contengono i vettori principali;
  - $\Sigma$ è una matrice diagonale dei valori singolari.

## **Analisi e stima**

| Dataset       | Dim. Dati | Dim. U | Dim. s | Dim. V | Tempo di calcolo |
|---------------|----------|---------|---------|--------|------------|
| __Small__         |  45,2 MB | 96 KB   |  3 KB  | 1,5 MB  | ~12m     |
| __Big__ (_Stimato_)|  212 GB  | 50,5 MB |  3 KB  | 13,1 MB | ~39g _Assumendo regime lineare_ |
| __Fattore di Crescita__ |  **~5000x** ( tra i dataset)

Come è possibile vedere, le dimensioni dei dati in memoria sono maggiori rispetto al csv in cui sono contenute. Questo perchè la matrice _user\_movie_ che viene decomposta è stata riempita con 0 al posto dei valori nulli, cosa non necessaria nella rappresentazione densa nel csv.

Già utilizzando il dataset _Small_ si osservano dei tempi di calcolo della decomposizione SVD elevati. Tuttavia una volta ricostruita la matrice tramite prodotto matriciale (eseguibile anche senza l'utilizzo di Spark date le dimensioni ridotte delle matrici), l'andare a creare raccomandazioni è un processo che non richiede particolari prestazioni ed è facilmente parallelizzabile.

Nel nostro caso non è stato possibile eseguire la decomposizione sul dataset _Big_ date le dimensioni proibitive della matrice completa, ma SVD si può comunque considerare un approccio perseguibile se si ha a disposizione un cluster che possa sostenere la risoluzione dell'algoritmo proprio perchè una volta ottenuta la matrice ricostruita, le prestazioni di previsione per gli utenti avranno delle tempistiche trascurabili.