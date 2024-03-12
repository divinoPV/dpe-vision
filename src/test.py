from config.config import config

print('hello')
## hello 

# Récupération du chemin du dossier logs
logs_path = config['logs']
print("Chemin du dossier logs:", logs_path)
