# Fincome-2025  

## Présentation  

Ceci est un projet qui sert de test technique pour l'entreprise Fincome.  

Il s'agit d'une application permettant de créer un serveur REST pour la gestion de datasets.  

## Installation  

Pour installer le projet, vous pouvez :  

- **Télécharger le fichier Fincome-2025.exe**, qui se suffit à lui seul. Il est cependant conseillé de le placer dans un dossier propre, car il créera des fichiers.  

- **Cloner ce répertoire** et lancer le fichier `server.py` qui se trouve dans le dossier `src`. Toutes les bibliothèques nécessaires au fonctionnement du projet sont listées dans le fichier `requirements.txt`. Il vous suffira de les installer avec la commande :  

```bash
  pip install -r requirements.txt  
```

## Fonctionnalités  

Le serveur possède 7 endpoints, qui sont les suivants :  

- `GET /datasets` : Récupérer la liste de tous les datasets disponibles sur le serveur.  
- `GET /datasets/{dataset_id}` : Récupérer un dataset spécifique en fonction de son ID.  
- `POST /datasets` : Enregistrer un nouveau dataset sur le serveur. Le fichier doit être envoyé au format CSV en tant que `multipart/form-data`.  
- `DELETE /datasets/{dataset_id}` : Supprimer un dataset spécifique en fonction de son ID.  
- `GET /datasets/{dataset_id}/excel` : Récupérer un dataset spécifique en fonction de son ID au format Excel.  
- `GET /datasets/{dataset_id}/stats` : Récupérer les statistiques des colonnes numériques d'un dataset spécifique en fonction de son ID.  
- `GET /datasets/{dataset_id}/plots` : Récupérer des histogrammes des colonnes numériques d'un dataset spécifique en fonction de son ID.  

## Tests  

Pour tester le projet, deux datasets sont mis à votre disposition dans le dossier `test/datasets`.  

Une série de requêtes pour tester chaque endpoint est également disponible dans le fichier `test/requests.http`. Vous pouvez les exécuter avec l'extension **REST Client** de Visual Studio Code. Il vous suffira de lancer le serveur avant d'exécuter les requêtes.  

Pour les requêtes qui demandent un ID, celui-ci est par défaut initialisé à `1`.  
Pour les requêtes dont la réponse est un fichier, il faudra cliquer sur **"Save response body"** en haut à droite de la réponse pour le télécharger.  
