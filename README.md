# MLOps
L'objectif est de concevoir et développer une pile LLMOps simple pour mettre à disposition des LLM et des modèles d'embedding via une API


## setup l'env
     je choisi de faire un env avec Venv Python 
     
     ### lignes a lancer sur le terminale pour la creation de l'env
         python3 -m venv env_mlops
         env_mlops\Scripts\activate
     ### ligne a lancer pour le setup 
        au niveau de la racine du projet lancer cette ligne 
        pip install -e .
     ### Installation + lancement local ZenML
     pip install zenml
     zenml init
     zenml stack set default
     zenml up --blocking

