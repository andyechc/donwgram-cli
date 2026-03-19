"""
Módulo de conexión a Telegram usando Telethon
Maneja la conexión, autenticación y operaciones básicas
"""

import asyncio
from typing import List, Dict, Any, Optional
from telethon import TelegramClient
from telethon.errors import FloodWaitError, RPCError
from telethon.tl.types import InputPeerChannel, InputPeerChat
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class TelegramManager:
    """Clase para manejar la conexión y operaciones con Telegram"""
    
    def __init__(self, api_id: int, api_hash: str, phone: str, session_name: str = "telegram_session"):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.session_name = session_name
        self.client: Optional[TelegramClient] = None
        self.is_connected = False
    
    async def connect(self) -> bool:
        """Establece conexión con Telegram"""
        try:
            console.print("[bold blue]🔐 Conectando a Telegram...[/bold blue]")
            
            # Crear cliente con sesión persistente
            self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
            
            # Iniciar conexión
            await self.client.start(phone=self.phone)
            self.is_connected = True
            
            # Verificar si estamos autenticados
            if await self.client.is_user_authorized():
                me = await self.client.get_me()
                console.print(Panel(
                    f"[green]✅ Conexión exitosa[/green]\n"
                    f"Usuario: {me.first_name} {me.last_name or ''}\n"
                    f"ID: {me.id}",
                    title="Telegram Conectado",
                    border_style="green"
                ))
                return True
            else:
                console.print("[red]❌ Error de autenticación[/red]")
                return False
                
        except FloodWaitError as e:
            console.print(f"[red]⏰ Límite de Telegram: espera {e.seconds} segundos[/red]")
            return False
        except RPCError as e:
            console.print(f"[red]❌ Error de RPC: {e}[/red]")
            return False
        except Exception as e:
            console.print(f"[red]❌ Error de conexión: {e}[/red]")
            return False
    
    async def get_recent_dialogs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtiene los diálogos recientes (canales y grupos)"""
        if not self.is_connected or not self.client:
            raise RuntimeError("No hay conexión activa con Telegram")
        
        try:
            dialogs = []
            async for dialog in self.client.iter_dialogs(limit=limit):
                # Filtrar solo canales y grupos
                if dialog.is_channel or dialog.is_group:
                    entity = dialog.entity
                    
                    # Obtener información adicional
                    participants_count = getattr(entity, 'participants_count', 'N/A')
                    
                    dialogs.append({
                        'id': dialog.id,
                        'title': dialog.title,
                        'type': 'Canal' if dialog.is_channel else 'Grupo',
                        'participants': participants_count,
                        'entity': entity
                    })
            
            return dialogs
            
        except FloodWaitError as e:
            console.print(f"[red]⏰ Límite de Telegram: espera {e.seconds} segundos[/red]")
            return []
        except Exception as e:
            console.print(f"[red]❌ Error obteniendo diálogos: {e}[/red]")
            return []
    
    async def search_videos(self, entities: List[Any], keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Busca videos en las entidades especificadas"""
        if not self.is_connected or not self.client:
            raise RuntimeError("No hay conexión activa con Telegram")
        
        videos = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"🔍 Buscando videos con '{keyword}'...", total=len(entities))
            
            for entity in entities:
                try:
                    # Buscar mensajes en la entidad
                    async for message in self.client.iter_messages(
                        entity=entity,
                        search=keyword,
                        limit=limit // len(entities),  # Distribuir límite entre entidades
                        filter=None
                    ):
                        # Verificar si el mensaje contiene video
                        if message.video:
                            # Obtener información del video
                            video = message.video
                            
                            videos.append({
                                'id': message.id,
                                'date': message.date.strftime('%Y-%m-%d %H:%M'),
                                'channel_title': getattr(entity, 'title', 'Desconocido'),
                                'message': message.message or 'Sin descripción',
                                'duration': getattr(video, 'duration', 'N/A'),
                                'file_size': getattr(video, 'file_size', 0),
                                'width': getattr(video, 'width', 0),
                                'height': getattr(video, 'height', 0),
                                'message_obj': message,
                                'entity': entity
                            })
                
                except FloodWaitError as e:
                    console.print(f"[yellow]⏰ Esperando {e.seconds} segundos por límite de API...[/yellow]")
                    await asyncio.sleep(e.seconds)
                except Exception as e:
                    console.print(f"[red]❌ Error buscando en {getattr(entity, 'title', 'entidad')}: {e}[/red]")
                
                progress.advance(task)
        
        return videos[:limit]  # Limitar resultados
    
    async def download_video(self, message: Any, entity: Any, file_path: str) -> bool:
        """Descarga un video específico"""
        if not self.is_connected or not self.client:
            raise RuntimeError("No hay conexión activa con Telegram")
        
        try:
            # Descargar el video con progreso
            await self.client.download_media(
                message=message,
                file=file_path,
                progress_callback=self._download_progress_callback
            )
            return True
            
        except FloodWaitError as e:
            console.print(f"[red]⏰ Límite de descarga: espera {e.seconds} segundos[/red]")
            return False
        except Exception as e:
            console.print(f"[red]❌ Error descargando video: {e}[/red]")
            return False
    
    def _download_progress_callback(self, current: int, total: int):
        """Callback para mostrar progreso de descarga"""
        if total > 0:
            percentage = (current / total) * 100
            # Usar carriage return para actualizar la misma línea
            print(f"\r📥 Descargando: {percentage:.1f}% ({current:,}/{total:,} bytes)", end='', flush=True)
    
    async def disconnect(self):
        """Cierra la conexión con Telegram"""
        if self.client and self.is_connected:
            await self.client.disconnect()
            self.is_connected = False
            console.print("[yellow]🔌 Conexión cerrada[/yellow]")
