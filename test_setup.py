#!/usr/bin/env python3
"""
Script de testing para validar la configuración del proyecto
sin conectar realmente a Telegram
"""

import os
import sys
from pathlib import Path

# Agregar el directorio actual al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Prueba que todos los módulos se importen correctamente"""
    print("🔍 Testeando importaciones de módulos...")
    
    try:
        import config
        print("✅ config.py importado correctamente")
    except Exception as e:
        print(f"❌ Error importando config.py: {e}")
        return False
    
    try:
        import telegram_client
        print("✅ telegram_client.py importado correctamente")
    except Exception as e:
        print(f"❌ Error importando telegram_client.py: {e}")
        return False
    
    try:
        import ui
        print("✅ ui.py importado correctamente")
    except Exception as e:
        print(f"❌ Error importando ui.py: {e}")
        return False
    
    try:
        import downloader
        print("✅ downloader.py importado correctamente")
    except Exception as e:
        print(f"❌ Error importando downloader.py: {e}")
        return False
    
    try:
        import main
        print("✅ main.py importado correctamente")
    except Exception as e:
        print(f"❌ Error importando main.py: {e}")
        return False
    
    return True

def test_rich_functionality():
    """Prueba la funcionalidad básica de Rich"""
    print("\n🎨 Testeando funcionalidad de Rich...")
    
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        
        console = Console()
        
        # Test de tabla
        table = Table(title="Test Table")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_row("1", "Test Item")
        
        # Test de panel
        panel = Panel("Test Panel", title="Test")
        
        print("✅ Funcionalidad de Rich funciona correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error con Rich: {e}")
        return False

def test_telethon_import():
    """Prueba la importación de Telethon"""
    print("\n📱 Testeando importación de Telethon...")
    
    try:
        from telethon import TelegramClient
        from telethon.errors import FloodWaitError, RPCError
        
        print("✅ Telethon importado correctamente")
        print("✅ Clases de error importadas correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error importando Telethon: {e}")
        return False

def test_config_loading():
    """Prueba la carga de configuración"""
    print("\n⚙️ Testeando carga de configuración...")
    
    try:
        # Copiar el archivo de prueba temporalmente como .env
        import shutil
        if Path('.env').exists():
            shutil.copy('.env', '.env.backup')
        
        shutil.copy('.env.test', '.env')
        
        # Importar y crear configuración (cargará .env automáticamente)
        from importlib import reload
        import config
        reload(config)  # Forzar recarga con nuevo .env
        
        from config import Config
        config_instance = Config()
        
        # Verificar que las variables se cargaron
        assert config_instance.api_id == 12345678
        assert config_instance.api_hash == "abcdef1234567890abcdef1234567890"
        assert config_instance.phone == "+5491122334455"
        
        print("✅ Configuración cargada correctamente")
        print(f"✅ API ID: {config_instance.api_id}")
        print(f"✅ API Hash: {config_instance.api_hash[:10]}...")
        print(f"✅ Phone: {config_instance.phone}")
        
        # Restaurar .env original si existía
        if Path('.env.backup').exists():
            shutil.move('.env.backup', '.env')
        else:
            if Path('.env').exists():
                Path('.env').unlink()
            
        return True
        
    except Exception as e:
        print(f"❌ Error con configuración: {e}")
        # Restaurar .env original en caso de error
        if Path('.env.backup').exists():
            shutil.move('.env.backup', '.env')
        return False

def test_file_structure():
    """Verifica que todos los archivos necesarios existan"""
    print("\n📁 Testeando estructura de archivos...")
    
    required_files = [
        'main.py',
        'config.py',
        'telegram_client.py',
        'ui.py',
        'downloader.py',
        'requirements.txt',
        '.env.example',
        '.env.test',
        'README.md',
        '.gitignore'
    ]
    
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Archivos faltantes: {missing_files}")
        return False
    else:
        print("✅ Todos los archivos necesarios existen")
        return True

def test_downloader_functionality():
    """Prueba la funcionalidad básica del downloader"""
    print("\n📥 Testeando funcionalidad de descarga...")
    
    try:
        from downloader import VideoDownloader
        
        # Crear instancia
        downloader = VideoDownloader("test_downloads")
        
        # Test de sanitización de nombre de archivo
        safe_name = downloader.sanitize_filename("test<>:file|name?.mp4")
        print(f"✅ Sanitización de nombre: 'test<>:file|name?.mp4' -> '{safe_name}'")
        
        # Test de creación de carpeta
        downloader.ensure_downloads_folder()
        test_folder = Path("test_downloads")
        if test_folder.exists():
            print("✅ Carpeta de descargas creada correctamente")
            # Limpiar después del test
            import shutil
            shutil.rmtree(test_folder)
        else:
            print("❌ No se pudo crear la carpeta de descargas")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error con downloader: {e}")
        return False

def main():
    """Ejecuta todos los tests"""
    print("🚀 Iniciando tests del proyecto Telegram Video Downloader\n")
    
    tests = [
        ("Importaciones", test_imports),
        ("Estructura de archivos", test_file_structure),
        ("Rich", test_rich_functionality),
        ("Telethon", test_telethon_import),
        ("Configuración", test_config_loading),
        ("Downloader", test_downloader_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 Test: {test_name}")
        print(f"{'='*50}")
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n{'='*50}")
    print(f"📊 RESUMEN DE TESTS")
    print(f"{'='*50}")
    print(f"✅ Pasados: {passed}/{total}")
    print(f"❌ Fallidos: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ¡Todos los tests pasaron! El proyecto está listo para uso.")
        return True
    else:
        print(f"\n⚠️ {total - passed} tests fallaron. Revisa los errores arriba.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
