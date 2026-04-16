# 🎬 Downgram CLI

Una herramienta CLI interactiva desarrollada en Python que permite filtrar y descargar videos de Telegram usando el nombre **Downgram CLI** (Download + Telegram).

## ✨ Características

- 🔍 **Búsqueda inteligente**: Busca videos por palabras clave en múltiples canales
- 📺 **Selección múltiple**: Elige varios canales/grupos para crear un pool de búsqueda
- 🎯 **Selección manual**: Selecciona específicamente qué videos descargar de los resultados
- � **Paginación**: Navega por resultados de búsqueda en múltiples páginas
- 🖱️ **Menús interactivos**: Navegación intuitiva con flechas usando inquirer
- � **Interfaz visual bonita**: Tablas, paneles y barras de progreso con Rich
- 📁 **Organización automática**: Videos organizados por carpetas de canal
- 📂 **Carpeta personalizable**: Selector nativo de carpetas (macOS) o ruta manual
- ⚡ **Descarga con progreso**: Barras de progreso reales con velocidad y tamaño
- 🔄 **Sesión persistente**: No necesitas ingresar código SMS en cada ejecución
- 🛡️ **Manejo de errores**: Gestión de FloodWaitError y otros errores comunes
- ⬅️ **Navegación flexible**: Volver atrás, ir al menú o salir en cualquier paso

## 📋 Requisitos

- Python 3.7 o superior
- Credenciales de API de Telegram (API_ID y API_HASH)
- Número de teléfono con cuenta de Telegram

## 🚀 Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   # Si estás usando estos archivos directamente, asegúrate de tener todos los archivos:
   # - main.py
   # - config.py
   # - telegram_client.py
   # - ui.py
   # - downloader.py
   # - requirements.txt
   # - .env.example
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar credenciales**
   ```bash
   # Copiar el archivo de ejemplo
   cp .env.example .env
   
   # Editar el archivo .env con tus credenciales
   nano .env  # o tu editor preferido
   ```

## ⚙️ Configuración

### Obtener credenciales de Telegram API

1. Ve a [https://my.telegram.org/apps](https://my.telegram.org/apps)
2. Inicia sesión con tu número de teléfono
3. Crea una nueva aplicación:
   - **App title**: Telegram Video Downloader
   - **Short name**: tg-video-downloader
   - **Platform**: Desktop
   - Los demás campos puedes dejarlos en blanco
4. Copia el `api_id` y `api_hash`

### Configurar archivo .env

Edita tu archivo `.env` con tus credenciales:

```env
# Telegram API Configuration
API_ID=tu_api_id_aqui
API_HASH=tu_api_hash_aqui
PHONE=tu_numero_telefono_con_codigo_pais

# Ejemplo:
# API_ID=12345678
# API_HASH=abc123def456ghi789
# PHONE=+5491122334455
```

## 🎮 Uso

### Ejecutar la aplicación

```bash
python main.py
```

### Flujo de uso

1. **Conexión inicial**: La primera vez te pedirá el código SMS de Telegram
2. **Selección de canales**: Menú interactivo con tus canales/grupos recientes
   - Navega con las **flechas** y presiona **Enter** para seleccionar
   - Selecciona múltiples canales marcándolos con **Espacio**
   - Presiona **Enter** para continuar
   - Opciones: `Volver atrás` o `Salir`
3. **Búsqueda**: Ingresa una palabra clave para buscar videos
   - Opciones: `Volver atrás` (cambiar canales) o `Salir`
4. **Resultados**: Tabla de videos encontrados con paginación
   - Navega entre páginas con opciones interactivas
   - Selecciona videos específicos o todos los de la página
   - **Acumula selecciones** de múltiples páginas
   - Opciones: `Siguiente página`, `Página anterior`, `Ir a página específica`
5. **Selección de descarga**: Elige la carpeta de destino
   - **macOS**: Selector nativo de carpetas del Finder
   - **Otras plataformas**: Ingresa la ruta manualmente
   - Por defecto: `~/Downloads/Downgram/`
6. **Descarga**: Observa el progreso de descarga en tiempo real
7. **Organización**: Los videos se guardan en `carpeta_seleccionada/nombre_del_canal/`
8. **Menú post-descarga**: Volver al menú, nueva búsqueda o salir

## 📁 Estructura del Proyecto

```
downgram-cli/
├── main.py              # Script principal y punto de entrada
├── config.py            # Gestión de configuración y variables de entorno
├── telegram_client.py   # Conexión y operaciones con Telegram (Telethon)
├── ui.py                # Interfaz de usuario (Rich + inquirer)
├── downloader.py        # Gestión de descargas y organización de archivos
├── requirements.txt     # Dependencias de Python
├── .env.example        # Plantilla de configuración
├── .env                # Tu configuración personal (no compartir)
├── telegram_session.session   # Sesión de Telegram (creada automáticamente)
└── ~/Downloads/Downgram/      # Carpeta de descargas por defecto (creada automáticamente)
    └── nombre_del_canal/      # Videos organizados por canal
```

## 🔧 Características Técnicas

### Arquitectura Modular

- **config.py**: Maneja variables de entorno y configuración inicial
- **telegram_client.py**: Encapsula toda la interacción con la API de Telegram
- **ui.py**: Interfaz rica con tablas, menús interactivos con inquirer y selector nativo de carpetas
- **downloader.py**: Gestiona descargas con progreso, organización por canal y carpetas personalizadas
- **main.py**: Orquesta el flujo completo con navegación entre pasos

### Manejo de Errores

- **FloodWaitError**: Espera automática cuando Telegram limita las peticiones
- **Conexión**: Reintentos automáticos y manejo de caídas de conexión
- **Validación**: Verificación de credenciales y parámetros
- **Archivos**: Manejo de nombres de archivo inválidos y duplicados

### Optimizaciones

- **Sesión persistente**: Archivo de sesión para evitar autenticación repetida
- **Paginación**: Resultados de búsqueda paginados para mejor rendimiento
- **Selección múltiple de páginas**: Acumula videos de diferentes páginas antes de descargar
- **Límites de API**: Distribución inteligente de límites entre múltiples canales
- **Concurrencia**: Operaciones asíncronas para mejor rendimiento
- **Memoria**: Gestión eficiente de resultados de búsqueda
- **Navegación intuitiva**: Menús con flechas (inquirer) en lugar de input de texto

## 🎯 Ejemplos de Uso

### Iniciar la aplicación
```bash
python main.py
```

### Navegación con menús interactivos
```
? ¿Qué deseas hacer? (Use arrow keys)
 ❯ 🔍 Realizar otra búsqueda
   🏠 Volver al menú principal
   ❌ Salir de la aplicación
```

### Selección de canales (con flechas)
```
? Selecciona los canales/grupos a buscar: (Press <space> to select, <a> to toggle all, <i> to invert selection)
 ❯◉ Canal de Tutoriales Python
  ◉ Grupo de Videos Musicales
  ○ Canal de Noticias Tech
  ◉ Grupo de Memes
```

### Búsqueda con paginación
```
Página 2/5 - Mostrando videos 11-20 de 47

? ¿Qué deseas hacer? (Use arrow keys)
 ❯ 📄 Seleccionar más archivos de otras páginas
   ✅ Finalizar selección e ir a descargar
   🔍 Volver a buscar (descartar selección)
   ❌ Salir
```

### Selección de carpeta de descarga (macOS)
```
? ¿Dónde deseas guardar los videos? (Use arrow keys)
 ❯ 📂 Usar carpeta por defecto: ~/Downloads/Downgram
   📁 Seleccionar otra carpeta (abrir Finder)
   ⬅️  Volver atrás
```

## 🛠️ Solución de Problemas

### Problemas Comunes

1. **Error de autenticación**
   - Verifica que `API_ID` y `API_HASH` sean correctos
   - Asegúrate de incluir el código de país en `PHONE` (ej: +549...)

2. **Error de FloodWait**
   - La aplicación esperará automáticamente
   - Si ocurre frecuentemente, reduce la cantidad de canales seleccionados

3. **No se encuentran videos**
   - Intenta con palabras clave más simples
   - Verifica que los canales seleccionados contengan videos

4. **Error de permisos**
   - Asegúrate de tener permisos para acceder a los canales
   - Algunos canales privados pueden requerir membresía

### Logs y Depuración

La aplicación muestra mensajes detallados en consola:
- ✅ Operaciones exitosas
- ⚠️ Advertencias y esperas
- ❌ Errores y fallos
- 📊 Progreso y estadísticas

## 🔐 Seguridad y Privacidad

- **Credenciales locales**: Nunca se comparten tus credenciales
- **Sesión cifrada**: La sesión de Telegram se almacena localmente
- **Sin datos externos**: La aplicación no envía datos a servidores externos
- **Código abierto**: Puedes revisar todo el código fuente

## 📝 Licencia

Este proyecto es para uso educativo y personal. Respeta siempre los términos de servicio de Telegram y los derechos de autor del contenido que descargas.

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Puedes:
- Reportar bugs
- Sugerir mejoras
- Enviar pull requests

## 📞 Soporte

Si encounteras problemas:
1. Revisa esta documentación
2. Verifica tus credenciales
3. Asegúrate de tener las dependencias actualizadas
4. Revisa los mensajes de error en consola

---

**Desarrollado con ❤️ usando Python, Telethon, Rich e Inquirer** | **Downgram CLI**
