#!/usr/bin/env python3
"""
Script para configurar fuente Nerd Font en VS Code
"""

import json
import os
from pathlib import Path

def setup_vscode_font():
    """Configura fuente Nerd Font en los settings de VS Code"""
    
    # Rutas posibles para settings de VS Code
    possible_paths = [
        Path.home() / "Library" / "Application Support" / "Code" / "User" / "settings.json",
        Path.home() / ".vscode" / "settings.json"
    ]
    
    settings_path = None
    for path in possible_paths:
        if path.exists():
            settings_path = path
            break
    
    if not settings_path:
        print("❌ No se encontró el archivo settings.json de VS Code")
        print("💡 Intenta configurar manualmente:")
        print("   1. Abre VS Code")
        print("   2. Presiona Cmd+Shift+P")
        print("   3. Busca 'Open Settings (JSON)'")
        print("   4. Agrega las siguientes líneas:")
        print("   ```json")
        print('   "terminal.integrated.fontFamily": "MesloLGL Nerd Font",')
        print('   "terminal.integrated.fontSize": 14,')
        print('   "terminal.integrated.lineHeight": 1.2')
        print("   ```")
        return False
    
    try:
        # Leer settings existentes
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        
        # Configurar fuente Nerd Font
        settings.update({
            "terminal.integrated.fontFamily": "MesloLGL Nerd Font",
            "terminal.integrated.fontSize": 14,
            "terminal.integrated.lineHeight": 1.2,
            "editor.fontFamily": "JetBrains Mono, Monaco, 'Courier New', monospace",
            "editor.fontSize": 14,
            "editor.lineHeight": 1.5
        })
        
        # Guardar settings
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=2)
        
        print(f"✅ Fuente Nerd Font configurada en: {settings_path}")
        print("🔄 Reinicia VS Code para que los cambios surtan efecto")
        return True
        
    except Exception as e:
        print(f"❌ Error configurando fuente: {e}")
        return False

def show_available_fonts():
    """Muestra las fuentes Nerd Font disponibles"""
    print("🎨 Fuentes Nerd Font disponibles en tu sistema:")
    
    import subprocess
    try:
        result = subprocess.run([
            "fc-list", ":family", "|", "grep", "-i", "nerd"
        ], capture_output=True, text=True, shell=True)
        
        fonts = set()
        for line in result.stdout.split('\n'):
            if 'nerd' in line.lower():
                # Extraer nombre de la fuente
                parts = line.split(':')
                if len(parts) >= 2:
                    font_name = parts[1].strip().split(',')[0]
                    if font_name and font_name not in fonts:
                        fonts.add(font_name)
        
        for font in sorted(fonts):
            print(f"  📝 {font}")
            
    except Exception as e:
        print(f"❌ Error obteniendo fuentes: {e}")

def main():
    print("🔧 Configurando fuente Nerd Font para VS Code")
    print("=" * 50)
    
    # Mostrar fuentes disponibles
    show_available_fonts()
    
    print("\n" + "=" * 50)
    
    # Configurar fuente
    if setup_vscode_font():
        print("\n🎉 ¡Configuración completada!")
        print("\n📝 Pasos finales:")
        print("1. Cierra y vuelve a abrir VS Code")
        print("2. Abre un nuevo terminal (Cmd+J)")
        print("3. Verifica que los iconos se muestren correctamente:")
        print("   📁 📂 🎬 🎥 📱 ⚙️ ✅ ❌")
    else:
        print("\n💡 Configuración manual:")
        print("1. Abre VS Code")
        print("2. Cmd+Shift+P → 'Open Settings (JSON)'")
        print("3. Agrega:")
        print('   "terminal.integrated.fontFamily": "MesloLGL Nerd Font"')

if __name__ == "__main__":
    main()
