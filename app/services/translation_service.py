from googletrans import Translator
from typing import Optional
from app.services.logging_service import logger


class TranslationService:
    def __init__(self):
        try:
            self.translator = Translator()
        except Exception as e:
            logger.warning(f"googletrans initialization failed: {e}")
            self.translator = None
    
    def translate(self, text: str, target_lang: str, source_lang: Optional[str] = None) -> str:
        if not text or not text.strip():
            return text
        
        if self.translator is None:
            logger.warning("Translator not initialized. Returning original text.")
            return text
            
        try:
            lang_map = {"en": "en", "ja": "ja"}
            target = lang_map.get(target_lang, "en")
            
            result = self.translator.translate(
                text,
                dest=target,
                src=source_lang if source_lang else None
            )
            
            return result.text
        except Exception as e:
            logger.warning(f"Translation error: {e}. Returning original text.")
            return text


translation_service = TranslationService()

