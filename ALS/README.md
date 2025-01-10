# **Alternating Least Squares (ALS)**  
### **Formula**: ALS minimizza la funzione di costo:
$$\sum_{(u, i) \in D} (r_{ui} - \mathbf{x}_u^T \mathbf{y}_i)^2 + \lambda (\|\mathbf{x}_u\|^2 + \|\mathbf{y}_i\|^2)$$

Dove $\mathbf{x}_u$ e $\mathbf{y}_i$ rappresentano i vettori utente e item, $\lambda$ è il termine di regolarizzazione.
     
### **Complessità**:  
ALS alterna tra la risoluzione di due problemi di regressione lineare, ciascuno con una complessità di $O(k^2 m + k^3)$, dove:
- $k$ è il numero di fattori latenti;
- $m$ è il numero di righe nella matrice utente o film.  
     
Grazie all’implementazione distribuita di Spark, ALS è risultato scalabile anche con il dataset **Big**, completando l'addestramento in tempi ragionevoli.

### **Analisi su Tempo e Memoria**  

L'analisi è stata condotta considerando tempi di esecuzione e memoria su due dataset di dimensioni diverse:  
- **Dataset MovieLens Small**: 7 MB.  
- **Dataset MovieLens Large**: 2.5 GB.  

Sono state effettuate due tipologie di addestramento:  
1. **Senza Cross Validation** (singolo modello).  
2. **Con Cross Validation**, scegliendo 9 combinazioni di parametri.  

#### **Tempi di Esecuzione**  
| Dataset      | Dimensione | Training (singolo modello) | Cross Validation | Fattore di Crescita |
|--------------|------------|---------------------|-------------------|--------------------|
| Small        | 7 MB       | 15 s               | 150 s            | **10x**            |
| Large        | 2.5 GB     | 210 s              | 4651 s           | **~20x**           |
| Fattore di Crescita |  **100x** ( tra i dataset) | **~10x**          | **~30x**           |  

#### **Osservazioni**  
1. **Crescita quasi lineare**:  
   - Il tempo di training cresce circa linearmente con la dimensione del dataset, coerentemente con la complessità temporale di ALS, che è ~$O(k^2 m)$ (dove $m$ è il numero di dati).  
   - Sebbene il dataset Large sia 100 volte più grande del dataset Small, il tempo di training senza Cross Validation è cresciuto di circa 10x, e con Cross Validation di circa 30x.  

2. **Effetto della Cross Validation**:  
   - Con il dataset Small, come si si poteva aspettare, l'addestramento con Cross Validation richiede un incremento di 10x rispetto a quello senza CV.  
   - Per il dataset Large, l'incremento è di quasi 20x.  

3. **Prospettive future**:  
   - L'incremento quasi lineare osservato nei tempi di esecuzione suggerisce che ALS potrebbe scalare bene anche su dataset di dimensioni comparabili al Netflix Prize Dataset (~ 3 GB).  

Questa osservazione rafforza l'idea che l'implementazione distribuita di ALS su Spark sia adatta per grandi dataset, rispettando la complessità teorica prevista.  






