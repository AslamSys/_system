"""
Carregador de configuração
"""

import yaml
from pathlib import Path

def load_config():
    """Carrega configuração do arquivo YAML"""
    config_path = Path(__file__).parent.parent / 'config' / 'audio.yaml'
    
    if not config_path.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config
