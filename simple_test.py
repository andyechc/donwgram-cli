#!/usr/bin/env python3
"""
Test simple para validar el funcionamiento básico del proyecto Downgram CLI
"""

import os
import sys
from pathlib import Path

def test_basic_functionality():
    """Test básico sin manipular archivos .env"""
    print("🧪 Test básico de funcionalidad...")
    
    # Test 1: Importaciones
    try:
        from rich.console import Console
        from telethon import TelegramClient
        from dotenv import load_dotenv
        print("✅ Librerías principales importadas correctamente")
    except Exception as e:
        print(f"❌ Error importando librerías: {e}")
        return False
    
    # Test 2: Funcionalidad de Rich
    try:
        console = Console()
        console.print("[green]✅ Test de Rich[/green]")
        print("✅ Rich funciona correctamente")
    except Exception as e:
        print(f"❌ Error con Rich: {e}")
        return False
    
    # Test 3: Creación de carpetas
    try:
        test_folder = Path("test_uploads")
        test_folder.mkdir(exist_ok=True)
        print(f"✅ Carpeta de prueba creada: {test_folder}")
        
        # Limpiar
        if test_folder.exists():
            test_folder.rmdir()
        print("✅ Carpeta de prueba eliminada")
    except Exception as e:
        print(f"❌ Error con carpetas: {e}")
        return False
    
    # Test 4: Sanitización de nombres
    try:
        import re
        unsafe_name = "test<>:file|name?.mp4"
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', unsafe_name)
        print(f"✅ Sanitización: '{unsafe_name}' -> '{safe_name}'")
    except Exception as e:
        print(f"❌ Error con sanitización: {e}")
        return False
    
    return True

def show_project_info():
    """Muestra información del proyecto"""
    print("\n📊 Información del Proyecto:")
    print("=" * 40)
    
    # Listar archivos principales
    main_files = [
        'main.py',
        'config.py', 
        'telegram_client.py',
        'ui.py',
        'downloader.py'
    ]
    
    for file in main_files:
        if Path(file).exists():
            size = Path(file).stat().st_size
            print(f"✅ {file} ({size:,} bytes)")
        else:
            print(f"❌ {file} (no encontrado)")
    
    # Verificar entorno virtual
    venv_path = Path("venv")
    if venv_path.exists():
        print(f"✅ Entorno virtual activo en: {venv_path}")
    else:
        print("❌ Entorno virtual no encontrado")
    
    # Verificar requirements
    if Path("requirements.txt").exists():
        with open("requirements.txt", "r") as f:
            deps = f.read().strip().split('\n')
            print(f"✅ Dependencias configuradas: {len(deps)} paquetes")
            for dep in deps:
                if dep.strip():
                    print(f"  📦 {dep}")
    
    print("\n🎯 Para usar el proyecto:")
    print("1. Configura tus credenciales en .env")
    print("2. Activa el entorno: source venv/bin/activate")
    print("3. Ejecuta: python main.py")

def main():
    print("🚀 Test Simple - Downgram CLI")
    print("=" * 50)
    
    # Mostrar información del proyecto
    show_project_info()
    
    # Ejecutar test básico
    print("\n🧪 Ejecutando test de funcionalidad básica...")
    print("=" * 50)
    
    if test_basic_functionality():
        print("\n🎉 ¡Test exitoso! El proyecto está listo para configurar.")
        print("\n📝 Próximos pasos:")
        print("1. Obtén tus credenciales en https://my.telegram.org/apps")
        print("2. Configúralas en el archivo .env")
        print("3. Ejecuta: python main.py")
        return True
    else:
        print("\n❌ Test falló. Revisa los errores arriba.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
