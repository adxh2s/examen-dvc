# Examen DVC et Dagshub

## Structure Projet

```bash       
├── examen_dvc          
│   ├── data       
│   │   ├── processed_data      
│   │   └── raw_data       
│   ├── metrics       
│   ├── models        
│   ├── src       
│   │   ├── data      
│   │   └── models
|   ├── Makefile
|   ├── params.yaml    
│   └── README.md.py       
```

## Pré-requis

1. UV pour la gestion de l'environnement de travail local et son pyproject
2. le fichier csv de départ dans /data/raw
3. un git, dvc et dagshub paramétré
4. make pour lancer les différentes commandes du Makefile, les lignes de commandes attendent les parametres DAGSHUB user, repo et token

## Important !
> Attention : la commande make all lance toutes les commandes principales, dont le reset et l'init en début, pour avoir un environnement de travail propre.
> A ne faire qu'une seule fois, passer ensuite par make run et make save pour lancer le pipeline de traitement et la sauvegarde git/dvc
   
##  Dépot git / dagshub

1. Le git
> https://github.com/adxh2s/examen-dvc.git

1. Le dagshub
> https://dagshub.com/adx.h2s/examen-dvc
> le repository est normalement partagé avec le collaborateur licence pedagogique en lecture uniquement.

1. Makefile
> C'est orchestrateur des traitements - commandes principales :
> make all avec DAGSHUB_USER, REPO_NAME et DAGSHUB_TOKEN en parametres pour la gestion des sources/data/modeles, etc. par git/dvc.
> make run lance le pipeline de traitement complet pour tous les scripts
> make help donne toutes les commandes disponibles