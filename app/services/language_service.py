from langdetect import detect, LangDetectException


class LanguageService:
    SUPPORTED_LANGUAGES = {"en", "ja"}
    
    @staticmethod
    def detect_language(text: str) -> str:
        if not text or not text.strip():
            raise ValueError("Empty text cannot be processed")
        
        try:
            detected_lang = detect(text)
            if detected_lang == "en":
                return "en"
            elif detected_lang == "ja":
                return "ja"
            else:
                return "en"
        except LangDetectException:
            return "en"
    
    @staticmethod
    def is_supported(language: str) -> bool:
        return language in LanguageService.SUPPORTED_LANGUAGES


language_service = LanguageService()

