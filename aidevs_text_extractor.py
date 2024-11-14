import os
from typing import List, Type
from aidevs import transcribe_audio_file, extract_text_from_image

class TextExtractorPlugin:
    """Base class for text extraction plugins"""
    supported_extensions: List[str] = []
    
    def extract(self, filepath: str) -> str:
        raise NotImplementedError("Each plugin must implement extract method")
    
    @classmethod
    def can_handle(cls, extension: str) -> bool:
        """Check if plugin can handle given file extension"""
        return extension.lower() in cls.supported_extensions

class TextFilePlugin(TextExtractorPlugin):
    supported_extensions = ['.txt']
    
    def extract(self, filepath: str) -> str:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

class AudioFilePlugin(TextExtractorPlugin):
    supported_extensions = ['.mp3', '.wav', '.m4a']
    
    def extract(self, filepath: str) -> str:
        return transcribe_audio_file(filepath, model_name="turbo", language="pl")

class ImageFilePlugin(TextExtractorPlugin):
    supported_extensions = ['.png', '.jpg', '.jpeg']
    
    def extract(self, filepath: str) -> str:
        return extract_text_from_image(filepath, method="tesseract", language="pol+eng")

class TextExtractor:
    """Factory class that creates appropriate extractor based on file type"""
    
    @classmethod
    def _get_all_plugins(cls) -> List[Type[TextExtractorPlugin]]:
        """Use reflection to get all TextExtractorPlugin subclasses"""
        def get_all_subclasses(base_class):
            all_subclasses = []
            for subclass in base_class.__subclasses__():
                all_subclasses.append(subclass)
                all_subclasses.extend(get_all_subclasses(subclass))
            return all_subclasses
            
        return get_all_subclasses(TextExtractorPlugin)

    @classmethod
    def create(cls, filepath: str) -> TextExtractorPlugin:
        """
        Factory method that returns appropriate extractor based on file extension
        
        Parameters:
        - filepath (str): Path to the file to be processed
        
        Returns:
        - TextExtractorPlugin: Appropriate plugin instance for the file type
        
        Raises:
        - ValueError: If file type is not supported
        """
        ext = os.path.splitext(filepath)[1].lower()
        
        # Find plugin that can handle this extension
        for plugin_class in cls._get_all_plugins():
            if plugin_class.can_handle(ext):
                return plugin_class()
                
        raise ValueError(f"No plugin found for file type: {ext}")

    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """Returns list of all supported file extensions"""
        extensions = []
        for plugin in cls._get_all_plugins():
            extensions.extend(plugin.supported_extensions)
        return sorted(extensions) 