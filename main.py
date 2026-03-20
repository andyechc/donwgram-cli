#!/usr/bin/env python3
"""
Downgram CLI - Script Principal
Una herramienta CLI interactiva para filtrar y descargar videos de Telegram
"""

import asyncio
import sys
import signal
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.prompt import Prompt

# Importar módulos personalizados
from config import Config
from telegram_client import TelegramManager
from ui import UserInterface
from downloader import VideoDownloader

console = Console()

class DowngramCLI:
    """Clase principal que coordina toda la aplicación"""
    
    def __init__(self):
        self.config = Config()
        self.telegram_manager: Optional[TelegramManager] = None
        self.ui = UserInterface()
        self.downloader = VideoDownloader(self.config.downloads_folder)
        self.is_running = False
    
    def setup_signal_handlers(self):
        """Configura manejadores de señales para cierre elegante"""
        def signal_handler(signum, frame):
            print("\n🛑 Cerrando aplicación...")
            self.is_running = False
            if self.telegram_manager:
                asyncio.create_task(self.telegram_manager.disconnect())
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run(self):
        """Ejecuta la aplicación principal"""
        self.is_running = True
        self.setup_signal_handlers()
        
        try:
            # 1. Mostrar bienvenida
            self.ui.show_welcome()
            
            # 2. Validar configuración
            if not self.config.validate_credentials():
                self.ui.show_error("Credenciales inválidas. Verifica tu archivo .env")
                return
            
            # 3. Crear carpeta de descargas
            self.downloader.ensure_downloads_folder()
            
            # 4. Conectar a Telegram
            if not await self._connect_to_telegram():
                return
            
            # 5. Ejecutar flujo principal
            await self._run_main_flow()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️  Aplicación interrumpida por el usuario[/yellow]")
        except Exception as e:
            self.ui.show_error(f"Error inesperado: {str(e)}", "Error Crítico")
        finally:
            # 6. Desconectar de Telegram
            await self._cleanup()
    
    async def _connect_to_telegram(self) -> bool:
        """Establece conexión con Telegram"""
        try:
            api_id, api_hash, phone = self.config.get_api_credentials()
            self.telegram_manager = TelegramManager(api_id, api_hash, phone, self.config.session_name)
            
            connected = await self.telegram_manager.connect()
            
            if not connected:
                self.ui.show_error("No se pudo conectar a Telegram. Verifica tus credenciales.")
                return False
            
            return True
            
        except ValueError as e:
            self.ui.show_error(str(e))
            return False
        except Exception as e:
            self.ui.show_error(f"Error de conexión: {str(e)}")
            return False
    
    async def _run_main_flow(self):
        """Ejecuta el flujo principal de la aplicación"""
        while self.is_running:
            try:
                # 1. Obtener y mostrar canales
                dialogs = await self.telegram_manager.get_recent_dialogs(limit=50)
                
                if not dialogs:
                    self.ui.show_error("No se encontraron canales o grupos disponibles")
                    return
                
                # 2. Selección de canales
                selected_channel_indices = self.ui.show_channels_table(dialogs)
                
                if not selected_channel_indices:
                    if not self.ui.confirm_action("¿Deseas salir de la aplicación?"):
                        continue
                    else:
                        break
                
                # 3. Obtener entidades seleccionadas
                selected_entities = [dialogs[i]['entity'] for i in selected_channel_indices]
                selected_channel_names = [dialogs[i]['title'] for i in selected_channel_indices]
                
                console.print(f"[green]✅ Canales seleccionados: {len(selected_entities)}[/green]")
                for name in selected_channel_names:
                    console.print(f"  📺 {name}")
                
                # 4. Búsqueda de videos
                keyword = self.ui.get_search_keyword()
                
                # 5. Realizar búsqueda con paginación
                current_page = 0
                all_selected_videos = []
                current_search_result = None
                
                while True:
                    # Realizar búsqueda para la página actual
                    search_result = await self.telegram_manager.search_videos(
                        entities=selected_entities,
                        keyword=keyword,
                        limit=self.config.max_search_results,
                        offset=current_page
                    )
                    
                    current_search_result = search_result
                    
                    # 6. Mostrar resultados y selección
                    selected_video_indices, navigation_action = self.ui.show_search_results(search_result)
                    
                    # Manejar navegación
                    if navigation_action == 'next':
                        current_page += 1
                        continue
                    elif navigation_action == 'prev':
                        current_page = max(0, current_page - 1)
                        continue
                    elif navigation_action and navigation_action.startswith('page_'):
                        target_page = int(navigation_action.split('_')[1]) - 1
                        current_page = target_page
                        continue
                    
                    # Si hay videos seleccionados, agregarlos a la lista
                    if selected_video_indices:
                        # Convertir índices locales a videos completos
                        page_videos = search_result['videos']
                        for idx in selected_video_indices:
                            all_selected_videos.append(page_videos[idx])
                        
                        # Preguntar si desea seleccionar más videos de otras páginas
                        if search_result['total_pages'] > 1:
                            if self.ui.confirm_action("¿Deseas seleccionar videos de otras páginas?"):
                                # Permitir navegar a otras páginas
                                nav_choice = Prompt.ask(
                                    "📍 Navegar a: [next/prev/page N/finish]", 
                                    default="finish"
                                ).lower().strip()
                                
                                if nav_choice == 'next' and current_page < search_result['total_pages'] - 1:
                                    current_page += 1
                                    continue
                                elif nav_choice == 'prev' and current_page > 0:
                                    current_page -= 1
                                    continue
                                elif nav_choice.startswith('page '):
                                    try:
                                        page_num = int(nav_choice.split(' ')[1]) - 1
                                        if 0 <= page_num < search_result['total_pages']:
                                            current_page = page_num
                                            continue
                                    except (ValueError, IndexError):
                                        console.print("[red]❌ Página inválida[/red]")
                                # Si no quiere navegar más, salir del bucle
                    
                    # Salir del bucle de paginación
                    break
                
                if not all_selected_videos:
                    if not self.ui.confirm_action("¿Deseas realizar otra búsqueda?"):
                        break
                    else:
                        continue
                
                # Descargar videos seleccionados
                download_results = await self.downloader.download_videos(
                    self.telegram_manager,
                    all_selected_videos,
                    list(range(len(all_selected_videos)))  # Todos los videos seleccionados
                )
                
                # Mostrar resumen final
                self.ui.show_completion_message(
                    download_results['downloaded'],
                    len(all_selected_videos)
                )
                
                # Preguntar si desea continuar
                if not self.ui.confirm_action("¿Deseas realizar otra búsqueda?"):
                    break
                    
            except Exception as e:
                self.ui.show_error(f"Error en el flujo principal: {str(e)}")
                if not self.ui.confirm_action("¿Deseas intentar nuevamente?"):
                    break
    
    async def _cleanup(self):
        """Limpieza y cierre de recursos"""
        if self.telegram_manager:
            await self.telegram_manager.disconnect()
        
        console.print("\n[bold green]👋 ¡Hasta luego![/bold green]")

def main():
    """Función principal de entrada"""
    try:
        # Verificar versión de Python
        if sys.version_info < (3, 7):
            print("❌ Esta aplicación requiere Python 3.7 o superior")
            sys.exit(1)
        
        # Crear y ejecutar la aplicación
        app = DowngramCLI()
        asyncio.run(app.run())
        
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
