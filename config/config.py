import os
import yaml

def update_paths(base_path, config_dict):
    for key, value in config_dict.items():
        if isinstance(value, dict):
            update_paths(base_path, value)
        elif isinstance(value, str):
            # Gérer spécifiquement les chemins commençant par '../..'
            if value.startswith('../../'):
                # Descendre de deux niveaux
                adjusted_path = os.path.normpath(os.path.join(base_path, '..', '..', value[6:]))
                config_dict[key] = adjusted_path
            # Gérer spécifiquement les chemins commençant par '../'
            elif value.startswith('../'):
                # Descendre d'un niveau
                adjusted_path = os.path.normpath(os.path.join(base_path, '..', value[3:]))
                config_dict[key] = adjusted_path
            else:
                config_dict[key] = os.path.normpath(os.path.join(base_path, value))

def load_config(config_file_path):
    with open(config_file_path, 'r') as f:
        config = yaml.safe_load(f)

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(config_file_path)))
    update_paths(project_root, config)
    return config

# Charger la configuration depuis le fichier YAML
config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yml")
config = load_config(config_file_path)

# Clés d'API
API_KEYS = config.get("api_keys", {})
