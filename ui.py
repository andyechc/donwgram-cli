"""
Módulo de interfaz de usuario usando Rich
Maneja la visualización de datos, tablas y selección interactiva
"""

from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.progress import Progress, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn
from rich.text import Text
from rich.layout import Layout
import os
import time

console = Console()

class UserInterface:
    """Clase para manejar la interfaz de usuario con Rich"""
    
    @staticmethod
    def show_welcome():
        """Muestra el mensaje de bienvenida"""
        welcome_text = """
[bold cyan]🎬 Downgram CLI[/bold cyan]
[yellow]Una herramienta interactiva para filtrar y descargar videos de Telegram[/yellow]

[dim]Usando Telethon + Rich[/dim]
        """
        console.print(Panel(
            welcome_text,
            title="Bienvenido",
            border_style="cyan",
            padding=(1, 2)
        ))
    
    @staticmethod
    def show_channels_table(dialogs: List[Dict[str, Any]]) -> List[int]:
        """Muestra una tabla con los canales/grupos y permite selección múltiple"""
        if not dialogs:
            console.print("[yellow]⚠️  No se encontraron canales o grupos[/yellow]")
            return []
        
        # Crear tabla
        table = Table(title="📺 Canales y Grupos Disponibles")
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Tipo", style="magenta", width=8)
        table.add_column("Nombre", style="white", width=40)
        table.add_column("Participantes", style="green", width=12)
        
        # Agregar filas
        for i, dialog in enumerate(dialogs, 1):
            participants = dialog['participants']
            if participants == 'N/A':
                participants_text = "N/A"
            elif isinstance(participants, int):
                participants_text = f"{participants:,}"
            else:
                participants_text = str(participants)
            
            table.add_row(
                str(i),
                dialog['type'],
                dialog['title'][:37] + "..." if len(dialog['title']) > 37 else dialog['title'],
                participants_text
            )
        
        console.print(table)
        
        # Selección de canales
        console.print("\n[bold]📋 Selección de Canales[/bold]")
        console.print("[dim]Ingresa los números de los canales que deseas incluir en la búsqueda[/dim]")
        console.print("[dim]Ejemplo: 1,3,5-8,10 (separados por comas, rangos con guión)[/dim]")
        
        while True:
            try:
                selection_input = Prompt.ask("🎯 Selecciona canales", default="all")
                
                if selection_input.lower() == "all":
                    return list(range(len(dialogs)))
                
                selected_indices = UserInterface._parse_selection(selection_input, len(dialogs))
                
                if selected_indices:
                    console.print(f"[green]✅ Seleccionados {len(selected_indices)} canales[/green]")
                    return selected_indices
                else:
                    console.print("[red]❌ Selección inválida. Intenta nuevamente[/red]")
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]⚠️  Operación cancelada[/yellow]")
                return []
    
    @staticmethod
    def _parse_selection(selection: str, max_index: int) -> List[int]:
        """Parsea una selección de usuarios (ej: 1,3,5-8,10)"""
        indices = []
        
        try:
            parts = selection.split(',')
            for part in parts:
                part = part.strip()
                
                if '-' in part:
                    # Rango (ej: 5-8)
                    start, end = map(int, part.split('-'))
                    indices.extend(range(start - 1, min(end, max_index)))
                else:
                    # Número individual
                    idx = int(part) - 1
                    if 0 <= idx < max_index:
                        indices.append(idx)
            
            return sorted(list(set(indices)))  # Eliminar duplicados y ordenar
            
        except ValueError:
            return []
    
    @staticmethod
    def get_search_keyword() -> str:
        """Solicita la palabra clave para búsqueda"""
        console.print("\n[bold]🔍 Búsqueda de Videos[/bold]")
        
        while True:
            keyword = Prompt.ask("📝 Ingresa la palabra clave para buscar", default="")
            
            if keyword.strip():
                return keyword.strip()
            else:
                console.print("[red]❌ Debes ingresar una palabra clave[/red]")
    
    @staticmethod
    def show_search_results(videos: List[Dict[str, Any]]) -> List[int]:
        """Muestra los resultados de búsqueda en una tabla y permite selección"""
        if not videos:
            console.print("[yellow]⚠️  No se encontraron videos con esa palabra clave[/yellow]")
            return []
        
        # Crear tabla de resultados
        table = Table(title=f"🎥 Resultados de Búsqueda ({len(videos)} videos)")
        table.add_column("ID", style="cyan", width=4)
        table.add_column("Fecha", style="blue", width=16)
        table.add_column("Canal", style="magenta", width=25)
        table.add_column("Descripción", style="white", width=40)
        table.add_column("Duración", style="green", width=8)
        table.add_column("Tamaño", style="yellow", width=10)
        
        # Agregar filas
        for i, video in enumerate(videos, 1):
            # Formatear duración
            duration = video['duration']
            if duration and duration != 'N/A':
                minutes = duration // 60
                seconds = duration % 60
                duration_text = f"{minutes}:{seconds:02d}"
            else:
                duration_text = "N/A"
            
            # Formatear tamaño
            size = video['file_size']
            if size and size > 0:
                size_text = UserInterface._format_bytes(size)
            else:
                size_text = "N/A"
            
            # Truncar descripción si es muy larga
            description = video['message'][:37] + "..." if len(video['message']) > 37 else video['message']
            
            table.add_row(
                str(i),
                video['date'],
                video['channel_title'][:22] + "..." if len(video['channel_title']) > 22 else video['channel_title'],
                description,
                duration_text,
                size_text
            )
        
        console.print(table)
        
        # Selección de videos
        console.print("\n[bold]📥 Selección de Videos para Descargar[/bold]")
        console.print("[dim]Ingresa los números de los videos que deseas descargar[/dim]")
        console.print("[dim]Ejemplo: 1,3,5 o 'all' para descargar todos[/dim]")
        
        while True:
            try:
                selection_input = Prompt.ask("🎯 Selecciona videos", default="")
                
                if not selection_input:
                    return []
                
                if selection_input.lower() == "all":
                    return list(range(len(videos)))
                
                selected_indices = UserInterface._parse_selection(selection_input, len(videos))
                
                if selected_indices:
                    console.print(f"[green]✅ Seleccionados {len(selected_indices)} videos para descargar[/green]")
                    return selected_indices
                else:
                    console.print("[red]❌ Selección inválida. Intenta nuevamente[/red]")
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]⚠️  Operación cancelada[/yellow]")
                return []
    
    @staticmethod
    def _format_bytes(bytes_value: int) -> str:
        """Formatea bytes a formato legible (KB, MB, GB)"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} TB"
    
    @staticmethod
    def show_download_progress(videos: List[Dict[str, Any]], selected_indices: List[int]) -> None:
        """Muestra el progreso de descarga de videos"""
        selected_videos = [videos[i] for i in selected_indices]
        
        console.print(f"\n[bold]📥 Descargando {len(selected_videos)} videos...[/bold]")
        
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            tasks = {}
            
            for i, video in enumerate(selected_videos):
                # Crear nombre de archivo seguro
                channel_name = video['channel_title'][:30].replace('/', '_').replace('\\', '_')
                filename = f"video_{video['id']}_{channel_name}.mp4"
                
                # Crear tarea de progreso
                task_id = progress.add_task(
                    f"📹 {filename[:40]}...",
                    total=video.get('file_size', 0)
                )
                tasks[task_id] = video
            
            # Simular progreso (esto será reemplazado por el progreso real)
            import time
            for task_id, video in tasks.items():
                for i in range(100):
                    progress.update(task_id, advance=video.get('file_size', 1000000) // 100)
                    time.sleep(0.01)
                progress.update(task_id, completed=video.get('file_size', 0))
    
    @staticmethod
    def show_completion_message(downloaded_count: int, total_count: int):
        """Muestra mensaje de finalización"""
        if downloaded_count > 0:
            console.print(Panel(
                f"[green]✅ Descarga completada[/green]\n"
                f"Videos descargados: {downloaded_count}/{total_count}\n"
                f"Guardados en la carpeta 'downloads/'",
                title="Proceso Finalizado",
                border_style="green"
            ))
        else:
            console.print("[yellow]⚠️  No se descargaron videos[/yellow]")
    
    @staticmethod
    def show_error(message: str, title: str = "Error"):
        """Muestra un mensaje de error"""
        console.print(Panel(
            f"[red]❌ {message}[/red]",
            title=title,
            border_style="red"
        ))
    
    @staticmethod
    def confirm_action(message: str) -> bool:
        """Solicita confirmación al usuario"""
        return Confirm.ask(f"[yellow]⚠️  {message}[/yellow]")
