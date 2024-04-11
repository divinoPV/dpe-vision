# MLOps
L'objectif est de concevoir et développer une pile LLMOps simple pour mettre à disposition des LLM et des modèles d'embedding via une API

# Pre-requis
Vous devez installer docker et docker compose sur votre host.

# Initialisation du projet
À la racine du projet lancer :
```bash
docker compose -f docker-compose.yml up -d --build
```
pour initialiser le container docker.

Ensuite, exécuter la commande :
```bash
docker compose exec python-service /bin/bash -c "pip install -e ."
```
afin d'installer le projet comme paquet éditable.


# Entrer dans le container python
```bash
docker compose exec python-service /bin/bash
```

# Install pip packages
```bash
docker compose exec python-service /bin/bash -c "pip install -r requirements.txt"
```

# Run les pipelines zenml
Train:
```bash
docker compose exec python-service /bin/bash -c "python src/zenml_train.py"
```

Predict:
```bash
docker compose exec python-service /bin/bash -c "python src/zenml_predict.py"
```

Full:
```bash
docker compose exec python-service /bin/bash -c "python src/zenml_full.py"
```

# Lancer le server zenml
```bash
docker compose exec python-service /bin/bash -c "zenml up --ip-address 0.0.0.0 --port 8237"
```
