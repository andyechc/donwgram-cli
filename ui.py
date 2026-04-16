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
import sys
import platform
import asyncio
from datetime import datetime, timedelta
import inquirer

console = Console()

class UserInterface:
    """Clase para manejar la interfaz de usuario con Rich"""
    
    @staticmethod
    def select_folder_macos(initial_dir: str = None) -> Optional[str]:
        """Abre selector de carpetas nativo en macOS usando AppleScript."""
        try:
            import subprocess
            
            # Script AppleScript para abrir Finder y seleccionar carpeta
            script = '''
            tell application "Finder"
                activate
                set selectedFolder to choose folder with prompt "Seleccionar carpeta de descarga"
                return POSIX path of selectedFolder
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            if result.returncode == 0:
                folder_path = result.stdout.strip()
                # Remover la barra final que AppleScript añade
                if folder_path.endswith('/'):
                    folder_path = folder_path[:-1]
                if folder_path and os.path.isdir(folder_path):
                    return folder_path
            
            return None
            
        except subprocess.TimeoutExpired:
            console.print("[yellow]⚠️  El selector de carpetas expiró[/yellow]")
            return None
        except Exception as e:
            console.print(f"[yellow]⚠️  Error con AppleScript: {e}[/yellow]")
            return None
    
    @staticmethod
    def select_folder_native(initial_dir: str = None) -> Optional[str]:
        """
        Abre un selector de carpetas nativo del sistema operativo.
        Retorna la ruta seleccionada o None si se cancela.
        """
        system = platform.system()
        
        # En macOS, intentar AppleScript primero
        if system == "Darwin":
            result = UserInterface.select_folder_macos(initial_dir)
            if result:
                return result
        
        # Intentar usar tkinter (incluido con Python)
        try:
            if initial_dir is None:
                initial_dir = os.path.expanduser("~")
            
            import tkinter as tk
            from tkinter import filedialog
            
            # Crear ventana raíz oculta
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)  # Mantener en primer plano
            
            # Abrir diálogo de selección de carpeta
            folder_path = filedialog.askdirectory(
                title="Seleccionar carpeta de descarga",
                initialdir=initial_dir
            )
            
            root.destroy()
            
            if folder_path and os.path.isdir(folder_path):
                return folder_path
            return None
            
        except Exception as e:
            console.print(f"[yellow]⚠️  No se pudo abrir el selector nativo: {e}[/yellow]")
            return None
    
    @staticmethod
    def select_with_arrows(
        message: str, 
        choices: List[str], 
        default: str = None,
        allow_exit: bool = True
    ) -> str:
        """
        Muestra un selector interactivo con flechas del teclado.
        Retorna la opción seleccionada o 'exit' para salir.
        """
        # Agregar opción de salir si está habilitado
        all_choices = choices.copy()
        if allow_exit and "❌ Salir" not in all_choices and "❌ Cancelar" not in all_choices:
            all_choices.append("❌ Salir")
        
        try:
            questions = [
                inquirer.List(
                    'selection',
                    message=message,
                    choices=all_choices,
                    default=default if default else None,
                    carousel=True
                ),
            ]
            answers = inquirer.prompt(questions)
            
            if answers is None:  # Ctrl+C
                return "exit"
            
            result = answers['selection']
            
            if result in ["❌ Salir", "❌ Cancelar"]:
                return "exit"
            
            return result
            
        except KeyboardInterrupt:
            return "exit"
        except Exception as e:
            console.print(f"[red]❌ Error en selección: {e}[/red]")
            return "exit"
    
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
    def show_channels_table(dialogs: List[Dict[str, Any]]) -> tuple[List[int], str]:
        """Muestra una tabla con los canales/grupos y permite selección múltiple con flechas. Retorna (indices, action)."""
        if not dialogs:
            console.print("[yellow]⚠️  No se encontraron canales o grupos[/yellow]")
            return [], 'exit'
        
        # Crear tabla
        table = Table(title="📺 Canales y Grupos Disponibles")
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Tipo", style="magenta", width=8)
        table.add_column("Nombre", style="white", width=40)
        table.add_column("Participantes", style="green", width=12)
        
        # Crear lista de opciones para inquirer
        channel_choices = []
        for i, dialog in enumerate(dialogs, 1):
            participants = dialog['participants']
            if participants == 'N/A':
                participants_text = "N/A"
            elif isinstance(participants, int):
                participants_text = f"{participants:,}"
            else:
                participants_text = str(participants)
            
            display_text = f"[{dialog['type']}] {dialog['title'][:37]} ({participants_text} miembros)"
            table.add_row(str(i), dialog['type'], display_text, participants_text)
            channel_choices.append((display_text, i - 1))  # (texto mostrado, índice real)
        
        console.print(table)
        console.print("\n[dim]Usa flechas ↑↓ para navegar, Espacio para seleccionar, Enter para confirmar[/dim]")
        
        # Opciones de menú con flechas
        menu_choices = [
            "✅ Seleccionar todos los canales",
            "🎯 Seleccionar canales específicos",
            "❌ Salir"
        ]
        
        action = UserInterface.select_with_arrows(
            "¿Qué deseas hacer?",
            menu_choices,
            allow_exit=False
        )
        
        if action == "exit" or action == "❌ Salir":
            return [], 'exit'
        
        if action == "✅ Seleccionar todos los canales":
            console.print(f"[green]✅ Seleccionados todos los canales ({len(dialogs)})[/green]")
            return list(range(len(dialogs))), 'continue'
        
        if action == "🎯 Seleccionar canales específicos":
            # Usar checkbox para selección múltiple
            try:
                # Crear opciones para checkbox
                checkbox_choices = [text for text, idx in channel_choices]
                checkbox_choices.append("❌ Cancelar selección")
                
                questions = [
                    inquirer.Checkbox(
                        'channels',
                        message="Selecciona los canales (Espacio para seleccionar, Enter para confirmar)",
                        choices=checkbox_choices,
                    ),
                ]
                answers = inquirer.prompt(questions)
                
                if answers is None:
                    return [], 'back'
                
                selected_texts = answers['channels']
                
                if "❌ Cancelar selección" in selected_texts:
                    return [], 'back'
                
                # Convertir textos seleccionados a índices
                text_to_idx = {text: idx for text, idx in channel_choices}
                selected_indices = [text_to_idx[text] for text in selected_texts if text in text_to_idx]
                
                if selected_indices:
                    console.print(f"[green]✅ Seleccionados {len(selected_indices)} canales[/green]")
                    return selected_indices, 'continue'
                else:
                    console.print("[yellow]⚠️  No seleccionaste ningún canal[/yellow]")
                    return [], 'back'
                    
            except KeyboardInterrupt:
                return [], 'back'
        
        return [], 'back'
    
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
    def get_search_keyword() -> tuple[str, str]:
        """Solicita la palabra clave para búsqueda con opciones de navegación. Retorna (keyword, action)."""
        console.print("\n[bold]🔍 Búsqueda de Videos[/bold]")
        
        # Opciones de menú con flechas
        menu_choices = [
            "✏️  Ingresar palabra clave",
            "⬅️  Volver a canales",
            "❌ Salir"
        ]
        
        action = UserInterface.select_with_arrows(
            "¿Qué deseas hacer?",
            menu_choices,
            default="✏️  Ingresar palabra clave",
            allow_exit=False
        )
        
        if action == "exit" or action == "❌ Salir":
            return '', 'exit'
        
        if action == "⬅️  Volver a canales":
            return '', 'back'
        
        if action == "✏️  Ingresar palabra clave":
            while True:
                try:
                    questions = [
                        inquirer.Text(
                            'keyword',
                            message="📝 Escribe la palabra clave para buscar",
                        ),
                    ]
                    answers = inquirer.prompt(questions)
                    
                    if answers is None:  # Ctrl+C
                        return '', 'back'
                    
                    keyword = answers['keyword'].strip()
                    
                    if keyword:
                        return keyword, 'continue'
                    else:
                        console.print("[red]❌ Debes ingresar una palabra clave[/red]")
                        
                except KeyboardInterrupt:
                    return '', 'back'
        
        return '', 'back'
    
    @staticmethod
    def show_search_results(search_result: Dict[str, Any]) -> tuple[List[int], bool]:
        """Muestra los resultados de búsqueda con paginación y permite selección con flechas"""
        media = search_result['media']
        current_page = search_result['current_page']
        total_pages = search_result['total_pages']
        total_found = search_result['total_found']
        has_more = search_result['has_more']
        
        if not media:
            console.print("[yellow]⚠️  No se encontraron archivos con esa palabra clave[/yellow]")
            return [], False
        
        # Crear tabla de resultados con información de paginación
        table = Table(title=f"📄 Resultados de Búsqueda - Página {current_page}/{total_pages} (Total: {total_found} archivos)")
        table.add_column("ID", style="cyan", width=4)
        table.add_column("Tipo", style="green", width=6)
        table.add_column("Fecha", style="blue", width=12)
        table.add_column("Canal", style="magenta", width=15)
        table.add_column("Descripción", style="white", overflow="fold")
        table.add_column("Tamaño", style="yellow", width=10)
        
        # Crear lista de opciones para inquirer
        media_choices = []
        for i, item in enumerate(media, 1):
            # Formatear tamaño
            size = item['file_size']
            if size and isinstance(size, (int, float)) and size > 0:
                size_text = UserInterface._format_bytes(int(size))
            else:
                size_text = "N/A"
            
            # Formatear fecha a lenguaje humano
            date_text = UserInterface._format_human_date(item['date'])
            
            # Mostrar descripción: para audio usar título si está disponible, sino usar mensaje
            media_type = item.get('media_type', 'video')
            if media_type == 'audio' and item.get('title'):
                description = item['title']
            else:
                description = item['message'] or 'Sin descripción'
            
            # Truncar canal si es muy largo
            channel_name = item['channel_title']
            if len(channel_name) > 18:
                channel_name = channel_name[:18] + "..."
            
            # Determinar tipo de media
            if media_type == 'video':
                type_icon = "🎥 Vid"
            elif media_type == 'audio':
                type_icon = "🎵 Aud"
            elif media_type == 'voice':
                type_icon = "🎤 Voz"
            else:
                type_icon = "📁"
            
            table.add_row(str(i), type_icon, date_text, channel_name, description, size_text)
            
            # Crear texto para checkbox
            display_text = f"[{type_icon}] {date_text} | {channel_name} | {description[:40]} ({size_text})"
            media_choices.append(display_text)
        
        console.print(table)
        
        # Mostrar información de paginación
        console.print(f"\n[bold]📄 Información de Página[/bold]")
        console.print(f"Página actual: {current_page}/{total_pages}")
        console.print(f"Archivos en esta página: {len(media)}")
        console.print(f"Total de archivos encontrados: {total_found}")
        
        # Construir opciones de menú
        menu_choices = [
            "☑️  Seleccionar archivos específicos"
        ]
        
        if len(media) > 0:
            menu_choices.append("✅ Seleccionar todos los de esta página")
        
        if has_more:
            menu_choices.append("➡️  Siguiente página")
        
        if current_page > 1:
            menu_choices.append("⬅️  Página anterior")
        
        if total_pages > 1:
            menu_choices.append(f"📄 Ir a página (1-{total_pages})")
        
        menu_choices.extend([
            "🔍 Volver a buscar (nueva palabra clave)",
            "❌ Salir"
        ])
        
        action = UserInterface.select_with_arrows(
            "¿Qué deseas hacer?",
            menu_choices,
            allow_exit=False
        )
        
        if action == "exit" or action == "❌ Salir":
            return [], 'exit'
        
        if action == "🔍 Volver a buscar (nueva palabra clave)":
            return [], 'back'
        
        if action == "➡️  Siguiente página" and has_more:
            return [], 'next'
        
        if action == "⬅️  Página anterior" and current_page > 1:
            return [], 'prev'
        
        if action == f"📄 Ir a página (1-{total_pages})":
            try:
                questions = [
                    inquirer.Text(
                        'page',
                        message=f"Número de página (1-{total_pages})",
                        validate=lambda _, x: x.isdigit() and 1 <= int(x) <= total_pages
                    ),
                ]
                answers = inquirer.prompt(questions)
                
                if answers and answers['page']:
                    return [], f'page_{int(answers["page"])}'
            except:
                pass
            return [], False
        
        if action == "✅ Seleccionar todos los de esta página":
            console.print(f"[green]✅ Seleccionados {len(media)} archivos[/green]")
            return list(range(len(media))), False
        
        if action == "☑️  Seleccionar archivos específicos":
            try:
                # Agregar opción de cancelar
                media_choices.append("❌ Cancelar selección")
                
                questions = [
                    inquirer.Checkbox(
                        'files',
                        message="Selecciona los archivos (Espacio para seleccionar, Enter para confirmar)",
                        choices=media_choices,
                    ),
                ]
                answers = inquirer.prompt(questions)
                
                if answers is None:
                    return [], False
                
                selected_texts = answers['files']
                
                if "❌ Cancelar selección" in selected_texts:
                    return [], False
                
                # Mapear textos a índices
                selected_indices = []
                for i, item in enumerate(media):
                    size = item['file_size']
                    if size and isinstance(size, (int, float)) and size > 0:
                        size_text = UserInterface._format_bytes(int(size))
                    else:
                        size_text = "N/A"
                    date_text = UserInterface._format_human_date(item['date'])
                    media_type = item.get('media_type', 'video')
                    if media_type == 'audio' and item.get('title'):
                        description = item['title']
                    else:
                        description = item['message'] or 'Sin descripción'
                    channel_name = item['channel_title']
                    if len(channel_name) > 18:
                        channel_name = channel_name[:18] + "..."
                    if media_type == 'video':
                        type_icon = "🎥 Vid"
                    elif media_type == 'audio':
                        type_icon = "🎵 Aud"
                    elif media_type == 'voice':
                        type_icon = "🎤 Voz"
                    else:
                        type_icon = "📁"
                    display_text = f"[{type_icon}] {date_text} | {channel_name} | {description[:40]} ({size_text})"
                    if display_text in selected_texts:
                        selected_indices.append(i)
                
                if selected_indices:
                    console.print(f"[green]✅ Seleccionados {len(selected_indices)} archivos para descargar[/green]")
                    return selected_indices, False
                else:
                    console.print("[yellow]⚠️  No seleccionaste ningún archivo[/yellow]")
                    return [], False
                    
            except KeyboardInterrupt:
                return [], False
        
        return [], False
    
    @staticmethod
    def _format_human_date(date_str: str) -> str:
        """Formatea fecha a lenguaje humano (hace 2 horas, ayer, etc.)"""
        try:
            # Parsear la fecha del formato YYYY-MM-DD HH:MM
            video_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
            now = datetime.now()
            
            # Calcular diferencia
            diff = now - video_date
            
            if diff < timedelta(minutes=1):
                return "Ahora"
            elif diff < timedelta(hours=1):
                minutes = int(diff.total_seconds() / 60)
                return f"Hace {minutes} min"
            elif diff < timedelta(hours=24):
                hours = int(diff.total_seconds() / 3600)
                return f"Hace {hours} h"
            elif diff < timedelta(days=2):
                if video_date.date() == now.date():
                    return "Hoy"
                else:
                    return "Ayer"
            elif diff < timedelta(days=7):
                days = diff.days
                return f"Hace {days} días"
            elif diff < timedelta(days=30):
                weeks = diff.days // 7
                return f"Hace {weeks} sem"
            elif diff < timedelta(days=365):
                months = diff.days // 30
                return f"Hace {months} mes"
            else:
                years = diff.days // 365
                return f"Hace {years} año" if years == 1 else f"Hace {years} años"
                
        except Exception:
            return date_str  # Si hay error, mostrar fecha original
    
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
    def show_completion_message(downloaded_count: int, total_count: int, folder_path: str = ""):
        """Muestra mensaje de finalización"""
        if downloaded_count > 0:
            folder_msg = f"\n📁 Guardados en: {folder_path}" if folder_path else ""
            console.print(Panel(
                f"[green]✅ Descarga completada[/green]\n"
                f"Archivos descargados: {downloaded_count}/{total_count}"
                f"{folder_msg}",
                title="Proceso Finalizado",
                border_style="green"
            ))
        else:
            console.print("[yellow]⚠️  No se descargaron archivos[/yellow]")
    
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
    
    @staticmethod
    def select_download_folder(default_folder: str) -> str:
        """
        Permite al usuario seleccionar una carpeta de descarga usando selector nativo.
        Retorna la ruta de la carpeta seleccionada o None para usar la por defecto.
        """
        console.print(f"\n[bold]📁 Carpeta de Descarga[/bold]")
        console.print(f"[dim]Carpeta por defecto: {default_folder}[/dim]")
        
        # Opciones de menú con flechas
        menu_choices = [
            "📂 Usar carpeta por defecto",
            "📁 Abrir selector de carpetas (Finder/Explorer)",
            "✏️  Escribir ruta manualmente",
            "❌ Salir"
        ]
        
        action = UserInterface.select_with_arrows(
            "¿Cómo deseas seleccionar la carpeta?",
            menu_choices,
            default="📂 Usar carpeta por defecto",
            allow_exit=False
        )
        
        if action == "exit" or action == "❌ Salir":
            return "exit"
        
        if action == "📂 Usar carpeta por defecto":
            console.print(f"[green]✅ Usando carpeta por defecto: {default_folder}[/green]")
            return None
        
        if action == "📁 Abrir selector de carpetas (Finder/Explorer)":
            console.print("[dim]Abriendo selector de carpetas nativo...[/dim]")
            
            # Abrir selector nativo
            selected_folder = UserInterface.select_folder_native(default_folder)
            
            if selected_folder:
                console.print(f"[green]✅ Carpeta seleccionada: {selected_folder}[/green]")
                return selected_folder
            else:
                console.print("[yellow]⚠️  No se seleccionó ninguna carpeta[/yellow]")
                return None
        
        if action == "✏️  Escribir ruta manualmente":
            try:
                questions = [
                    inquirer.Text(
                        'path',
                        message="📝 Escribe la ruta de la carpeta (soporta ~ y rutas relativas)",
                    ),
                ]
                answers = inquirer.prompt(questions)
                
                if answers is None or not answers['path'].strip():
                    console.print("[yellow]⚠️  No se proporcionó ruta. Usando carpeta por defecto.[/yellow]")
                    return None
                
                folder_path = answers['path'].strip()
                
                # Expandir ~ a la carpeta home del usuario
                if folder_path.startswith('~'):
                    folder_path = os.path.expanduser(folder_path)
                
                # Convertir a ruta absoluta
                folder_path = os.path.abspath(folder_path)
                
                # Verificar si la ruta es válida
                try:
                    # Crear la carpeta si no existe
                    os.makedirs(folder_path, exist_ok=True)
                    console.print(f"[green]✅ Carpeta seleccionada: {folder_path}[/green]")
                    return folder_path
                except Exception as e:
                    console.print(f"[red]❌ Error con la ruta proporcionada: {e}[/red]")
                    console.print(f"[yellow]⚠️  Se usará la carpeta por defecto: {default_folder}[/yellow]")
                    return None
                    
            except KeyboardInterrupt:
                return None
        
        return None
