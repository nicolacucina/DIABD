# **SVD**

## **Formula**:  
La decomposizione si basa sulla rappresentazione della matrice $R$ come prodotto di tre matrici:
     $R = U \Sigma V^T$
Dove:
  - $U$ e $V$ contengono i vettori principali;
  - $\Sigma$ è una matrice diagonale dei valori singolari.

- **Complessità**:  
Il calcolo della decomposizione SVD ha una complessità di $O(m* n \cdot \min(m, n))$, dove:
  - $m$ e $n$ sono le dimensioni della matrice $R$.  

  Questo lo rende poco adatto per dataset di grandi dimensioni come il **Big**, dove la matrice è troppo grande per essere gestita efficientemente in memoria.


