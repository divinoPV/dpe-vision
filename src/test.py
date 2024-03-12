from config.config import config

print('hello')
## hello 

# Récupération du chemin du doss
# ier logs
logs_path = config['logs']
print("Chemin du dossier logs:", logs_path)

datasets_path = config['datasets']
print("Chemin du dossier datasets_path:", datasets_path)
