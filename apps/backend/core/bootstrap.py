from core.settings import settings

def initialize():
    settings.image_dir.mkdir(parents=True, exist_ok=True)
    settings.debug_dir.mkdir(parents=True, exist_ok=True)
    settings.json_dir.mkdir(parents=True, exist_ok=True)