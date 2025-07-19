import json
import os
from qiki_bot.core.file_paths import LOCALES_FILE

class LocalizationManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LocalizationManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, language='ru'):
        if not hasattr(self, 'initialized'):
            self.language = os.getenv('QIKI_LANG', language)
            self.locales = self._load_locales()
            self.initialized = True

    def _load_locales(self):
        try:
            with open(LOCALES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Fallback to a minimal dictionary if file is missing or corrupt
            return {
                'en': {'error_loading_locales': 'Error loading localization file.'},
                'ru': {'error_loading_locales': 'Ошибка загрузки файла локализации.'}
            }

    def get(self, key, lang=None):
        """Gets a localized string for a given key."""
        target_lang = lang if lang else self.language
        return self.locales.get(target_lang, {}).get(key, key) # Return the key itself as a fallback

    def get_dual(self, key):
        """Gets a dual-language string (RU | EN)."""
        ru_text = self.get(key, 'ru')
        en_text = self.get(key, 'en')
        
        if ru_text == en_text: # If translations are the same or both are missing
            return ru_text
            
        return f"{ru_text} | {en_text}"

# Global instance for easy access
loc = LocalizationManager()
