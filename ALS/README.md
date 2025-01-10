# **Alternating Least Squares (ALS)**  
## **Formula**: 
ALS minimizza la funzione di costo:
$$\sum_{(u, i) \in D} (r_{ui} - \mathbf{x}_u^T \mathbf{y}_i)^2 + \lambda (\|\mathbf{x}_u\|^2 + \|\mathbf{y}_i\|^2)$$

Dove $\mathbf{x}_u$ e $\mathbf{y}_i$ rappresentano i vettori utente e item, $\lambda$ è il termine di regolarizzazione.

Una volta calcolati, i vettori vengono utilizzati per ricostruire la matrice _user-movies_ dove avremo stimato le potenziali ratings di ogni utente per ogni film. A partire da questa, le raccomandazioni sono scelte come le rating previste più alte tra i film non ancora visti.
     
### **Complessità**:  
ALS alterna tra la risoluzione di due problemi di regressione lineare, ciascuno con una complessità di $O(k^2 m + k^3)$, dove:
- $k$ è il numero di fattori latenti;
- $m$ è il massimo tra il numero degli utenti o dei film.  
     
Grazie all’implementazione distribuita di Spark, ALS è riuscito nel predirre il dataset _Big_, completando l'addestramento in tempi ragionevoli.

## **Analisi su Tempo e Memoria**  

L'analisi è stata condotta considerando tempi di esecuzione e memoria occupata su:  
- **Dataset MovieLens Small**: ~7 MB.  
- **Dataset MovieLens Big**: ~2.5 GB.  

Sono state effettuate due tipologie di addestramento:  
1. **Senza Cross Validation** (singolo modello).  
2. **Con Cross Validation**, scegliendo 9 combinazioni di parametri.  

### **Tempi di Esecuzione**  
| Dataset      | Dimensione | Training (singolo modello) | Cross Validation | Fattore di Crescita |
|--------------|------------|---------------------|-------------------|--------------------|
| Small        | 7 MB       | 15 s               | 150 s            | **~10x**            |
| Big        | 2.5 GB     | 210 s              | 4651 s           | **~20x**           |
| Fattore di Crescita |  **~100x** ( tra i dataset) | **~15x**          | **~30x**           |  

Dai risultati ottenuti si può vedere il tempo di training cresce circa linearmente con la dimensione del dataset, coerentemente con la complessità temporale di ALS dove la dimensione del dataset compare come termine lineare.
Sebbene il dataset *Big* sia 100 volte più grande del dataset *Small*, il tempo di training senza Cross Validation è cresciuto di circa 15x, mentre con Cross Validation di circa 30x.

Pertanto si può trarre la conclusione che ALS sia un buon algoritmo per affrontare l'obiettivo prefissato del Netflix Prize Dataset , date le sue dimensioni di ~3 GB, comparabili con il dataset _Big_ utilizzato nel testing.







