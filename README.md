# 🎬 Downgram CLI

Una herramienta CLI interactiva desarrollada en Python que permite filtrar y descargar videos de Telegram usando el nombre **Downgram CLI** (Download + Telegram).

## ✨ Características

- 🔍 **Búsqueda inteligente**: Busca videos por palabras clave en múltiples canales
- 📺 **Selección múltiple**: Elige varios canales/grupos para crear un pool de búsqueda
- 🎯 **Selección manual**: Selecciona específicamente qué videos descargar de los resultados
- 📊 **Interfaz visual bonita**: Tablas, paneles y barras de progreso con Rich
- 📁 **Organización automática**: Videos organizados por carpetas de canal
- ⚡ **Descarga con progreso**: Barras de progreso reales con velocidad y tamaño
- 🔄 **Sesión persistente**: No necesitas ingresar código SMS en cada ejecución
- 🛡️ **Manejo de errores**: Gestión de FloodWaitError y otros errores comunes

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
2. **Selección de canales**: Se mostrará una tabla con tus canales/grupos recientes
   - Usa números individuales: `1,3,5`
   - Usa rangos: `5-8`
   - Selecciona todos: `all`
3. **Búsqueda**: Ingresa una palabra clave para buscar videos
4. **Resultados**: Revisa la tabla de videos encontrados
5. **Selección de videos**: Elige qué videos específicos descargar
6. **Descarga**: Observa el progreso de descarga en tiempo real
7. **Organización**: Los videos se guardarán en `downloads/nombre_del_canal/`

## 📁 Estructura del Proyecto

```
downgram-cli/
├── main.py              # Script principal y punto de entrada
├── config.py            # Gestión de configuración y variables de entorno
├── telegram_client.py   # Conexión y operaciones con Telegram (Telethon)
├── ui.py               # Interfaz de usuario (Rich)
├── downloader.py       # Gestión de descargas y organización de archivos
├── requirements.txt    # Dependencias de Python
├── .env.example       # Plantilla de configuración
├── .env               # Tu configuración personal (no compartir)
├── downloads/         # Carpeta donde se guardan los videos (creada automáticamente)
└── telegram_session.session  # Sesión de Telegram (creada automáticamente)
```

## 🔧 Características Técnicas

### Arquitectura Modular

- **config.py**: Maneja variables de entorno y configuración inicial
- **telegram_client.py**: Encapsula toda la interacción con la API de Telegram
- **ui.py**: Proporciona una interfaz rica con tablas y selección interactiva
- **downloader.py**: Gestiona descargas con progreso y organización de archivos
- **main.py**: Orquesta el flujo completo de la aplicación

### Manejo de Errores

- **FloodWaitError**: Espera automática cuando Telegram limita las peticiones
- **Conexión**: Reintentos automáticos y manejo de caídas de conexión
- **Validación**: Verificación de credenciales y parámetros
- **Archivos**: Manejo de nombres de archivo inválidos y duplicados

### Optimizaciones

- **Sesión persistente**: Archivo de sesión para evitar autenticación repetida
- **Límites de API**: Distribución inteligente de límites entre múltiples canales
- **Concurrencia**: Operaciones asíncronas para mejor rendimiento
- **Memoria**: Gestión eficiente de resultados de búsqueda

## 🎯 Ejemplos de Uso

### Búsqueda básica
```
📝 Ingresa la palabra clave para buscar: tutorial
```

### Selección de canales
```
🎯 Selecciona canales: 1,3,5-8
```

### Selección de videos
```
🎯 Selecciona videos: 2,5,7
```

### Descargar todos los videos
```
🎯 Selecciona videos: all
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

**Desarrollado con ❤️ usando Python, Telethon y Rich** | **Downgram CLI**
