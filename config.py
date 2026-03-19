"""
Módulo de configuración para la aplicación Telegram Video Downloader
Maneja la carga de variables de entorno y configuración inicial
"""

import os
from dotenv import load_dotenv
from typing import Optional

class Config:
    """Clase para manejar la configuración de la aplicación"""
    
    def __init__(self):
        # Cargar variables de entorno desde archivo .env
        load_dotenv()
        
        # Obtener credenciales de Telegram
        self.api_id = self._get_required_env("API_ID")
        self.api_hash = self._get_required_env("API_HASH")
        self.phone = self._get_required_env("PHONE")
        
        # Configuración adicional
        self.session_name = "telegram_session"
        self.downloads_folder = "downloads"
        self.max_search_results = 20
        
    def _get_required_env(self, key: str) -> str:
        """Obtiene una variable de entorno requerida, lanza excepción si no existe"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"La variable de entorno '{key}' es requerida. "
                           f"Por favor, configúrala en el archivo .env")
        return value
    
    def get_api_credentials(self) -> tuple[int, str, str]:
        """Retorna las credenciales de la API como una tupla"""
        return int(self.api_id), self.api_hash, self.phone
    
    def create_downloads_folder(self):
        """Crea la carpeta de descargas si no existe"""
        if not os.path.exists(self.downloads_folder):
            os.makedirs(self.downloads_folder)
            print(f"✅ Carpeta '{self.downloads_folder}' creada exitosamente")
    
    def validate_credentials(self) -> bool:
        """Valida que las credenciales básicas estén configuradas"""
        try:
            int(self.api_id)
            return True
        except ValueError:
            return False
