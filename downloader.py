"""
Módulo de descarga de videos con gestión de carpetas y barra de progreso
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
from rich.progress import Progress, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
from rich.console import Console
import re

console = Console()

class VideoDownloader:
    """Clase para manejar la descarga de videos con organización y progreso"""
    
    def __init__(self, downloads_folder: str = "downloads"):
        self.downloads_folder = Path(downloads_folder)
        self.downloaded_count = 0
        self.failed_count = 0
        
    def ensure_downloads_folder(self):
        """Asegura que la carpeta de descargas exista"""
        self.downloads_folder.mkdir(exist_ok=True)
        console.print(f"📁 Carpeta de descargas: {self.downloads_folder.absolute()}")
    
    def sanitize_filename(self, filename: str) -> str:
        """Limpia un nombre de archivo para que sea seguro para el sistema operativo"""
        # Eliminar caracteres no válidos
        invalid_chars = r'[<>:"/\\|?*]'
        filename = re.sub(invalid_chars, '_', filename)
        
        # Limitar longitud
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:200-len(ext)] + ext
        
        return filename
    
    def create_channel_folder(self, channel_name: str) -> Path:
        """Crea una carpeta para el canal si no existe"""
        safe_channel_name = self.sanitize_filename(channel_name)
        channel_folder = self.downloads_folder / safe_channel_name
        channel_folder.mkdir(exist_ok=True)
        return channel_folder
    
    async def download_videos(self, telegram_manager, videos: List[Dict[str, Any]], selected_indices: List[int]) -> Dict[str, int]:
        """Descarga los videos seleccionados con barra de progreso"""
        selected_videos = [videos[i] for i in selected_indices]
        
        if not selected_videos:
            return {'downloaded': 0, 'failed': 0}
        
        console.print(f"\n[bold blue]📥 Iniciando descarga de {len(selected_videos)} videos...[/bold blue]")
        
        # Reiniciar contadores
        self.downloaded_count = 0
        self.failed_count = 0
        
        with Progress(
            TextColumn("[bold blue]{task.description}", justify="right"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=False  # Mantener la barra visible después de completar
        ) as progress:
            
            tasks = {}
            
            # Crear tareas para cada video
            for i, video in enumerate(selected_videos):
                # Crear nombre de archivo
                channel_name = video['channel_title']
                filename = self._generate_filename(video)
                
                # Crear carpeta del canal
                channel_folder = self.create_channel_folder(channel_name)
                file_path = channel_folder / filename
                
                # Verificar si el archivo ya existe
                if file_path.exists():
                    console.print(f"[yellow]⚠️  El archivo ya existe: {filename}[/yellow]")
                    self.downloaded_count += 1
                    continue
                
                # Crear tarea de progreso
                task_id = progress.add_task(
                    f"📹 {filename[:50]}...",
                    total=video.get('file_size', 0)
                )
                tasks[task_id] = {
                    'video': video,
                    'file_path': file_path,
                    'filename': filename
                }
            
            # Descargar videos
            for task_id, video_info in tasks.items():
                await self._download_single_video(
                    telegram_manager,
                    progress,
                    task_id,
                    video_info['video'],
                    video_info['file_path'],
                    video_info['filename']
                )
        
        # Mostrar resumen
        self._show_download_summary(len(selected_videos))
        
        return {
            'downloaded': self.downloaded_count,
            'failed': self.failed_count
        }
    
    async def _download_single_video(self, telegram_manager, progress, task_id: int, video: Dict[str, Any], file_path: Path, filename: str):
        """Descarga un video individual con actualización de progreso"""
        try:
            # Callback para actualizar progreso
            def progress_callback(current: int, total: int):
                if total > 0:
                    progress.update(task_id, completed=current)
            
            # Descargar video usando el cliente de Telegram
            success = await telegram_manager.download_video(
                message=video['message_obj'],
                entity=video['entity'],
                file_path=str(file_path)
            )
            
            if success:
                # Actualizar progreso al 100%
                file_size = video.get('file_size', 0)
                if file_size > 0:
                    progress.update(task_id, completed=file_size)
                else:
                    progress.update(task_id, completed=progress.tasks[task_id].total or 100)
                
                self.downloaded_count += 1
                console.print(f"[green]✅ Descargado: {filename}[/green]")
            else:
                self.failed_count += 1
                console.print(f"[red]❌ Error descargando: {filename}[/red]")
                progress.update(task_id, completed=0)
                
        except Exception as e:
            self.failed_count += 1
            console.print(f"[red]❌ Error descargando {filename}: {str(e)}[/red]")
            progress.update(task_id, completed=0)
    
    def _generate_filename(self, video: Dict[str, Any]) -> str:
        """Genera un nombre de archivo descriptivo para el video"""
        # Obtener información básica
        video_id = video['id']
        channel_name = video['channel_title']
        message_text = video['message'] or "video"
        date = video['date'].replace(':', '-').replace(' ', '_')
        
        # Sanitizar nombres
        safe_channel = self.sanitize_filename(channel_name)[:30]
        safe_message = self.sanitize_filename(message_text)[:40]
        
        # Generar nombre de archivo
        filename = f"{date}_{safe_channel}_{video_id}_{safe_message}.mp4"
        
        return filename
    
    def _show_download_summary(self, total_videos: int):
        """Muestra un resumen de la descarga"""
        console.print(f"\n[bold]📊 Resumen de Descarga[/bold]")
        console.print(f"Total de videos: {total_videos}")
        console.print(f"[green]✅ Descargados exitosamente: {self.downloaded_count}[/green]")
        
        if self.failed_count > 0:
            console.print(f"[red]❌ Fallidos: {self.failed_count}[/red]")
        
        success_rate = (self.downloaded_count / total_videos * 100) if total_videos > 0 else 0
        console.print(f"📈 Tasa de éxito: {success_rate:.1f}%")
        
        if self.downloaded_count > 0:
            console.print(f"\n📁 Los videos se guardaron en: {self.downloads_folder.absolute()}")
    
    def get_downloaded_files_info(self) -> List[Dict[str, Any]]:
        """Obtiene información de los archivos descargados"""
        downloaded_files = []
        
        if not self.downloads_folder.exists():
            return downloaded_files
        
        for channel_folder in self.downloads_folder.iterdir():
            if channel_folder.is_dir():
                for video_file in channel_folder.iterdir():
                    if video_file.is_file() and video_file.suffix.lower() in ['.mp4', '.mov', '.avi']:
                        stat = video_file.stat()
                        downloaded_files.append({
                            'filename': video_file.name,
                            'channel': channel_folder.name,
                            'size': stat.st_size,
                            'path': str(video_file),
                            'modified': stat.st_mtime
                        })
        
        return downloaded_files
