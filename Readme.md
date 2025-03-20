# Comparador de Aseguradoras

Aplicación para extraer, resumir y comparar información de sitios web de compañías de seguros argentinas.

## Características

- Extracción automática de información de sitios web
- Resumen de contenido usando Gemini API
- Análisis comparativo entre dos aseguradoras
- Interfaz web intuitiva con Streamlit

## Requisitos

- Python 3.11+
- Gemini API Key

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/diegonf84/llms_insurance_resume_page.git
cd llms_insurance_resume_page
```

2. Instalar dependencias:
```bash
conda env create -f environment.yml
```

3. Configurar variables de entorno:
```bash
# Crear archivo .env con el siguiente contenido
# (reemplazar con tu clave de API real)
GEMINI_API_KEY=your_gemini_api_key_here
```

## Uso local

```bash
streamlit run app/main.py
```

## Estructura de datos
- Los resúmenes de las aseguradoras se guardan en `app/data/summaries/`
- Las comparativas no se guardan como archivos, solo se muestran en la interfaz y se pueden descargar

## Despliegue en Streamlit Cloud

1. **Preparación del repositorio**:
   - Asegúrate de tener el proyecto en un repositorio GitHub público o privado
   - Verifica que los archivos `.streamlit/config.toml`, `requirements.txt` y `app/main.py` estén en las ubicaciones correctas

2. **Configuración en Streamlit Cloud**:
   - Visita [https://share.streamlit.io/](https://share.streamlit.io/) y regístrate/inicia sesión
   - Haz clic en "New app"
   - Selecciona el repositorio, la rama y la ruta al archivo principal (`app/main.py`)
   - En la sección "Advanced settings", agrega la variable de entorno `GEMINI_API_KEY`
   - Haz clic en "Deploy!"

3. **Mantenimiento**:
   - La aplicación se actualizará automáticamente cuando hagas push a la rama conectada
   - Puedes monitorear logs y reiniciar la aplicación desde el dashboard de Streamlit Cloud

## Estructura del proyecto

```
comparador-aseguradoras/
│
├── app/                        # Código principal
│   ├── main.py                 # Aplicación Streamlit
│   ├── website_extractor.py    # Extractor web
│   ├── content_processor.py    # Procesador de contenido
│   ├── summarizer.py           # Generador de resúmenes
│   ├── comparator.py           # Comparador de aseguradoras
│   ├── config.py               # Configuración
│   └── data/                   # Directorio para datos generados
│       ├── aseguradoras.json   # Lista de aseguradoras
│       └── summaries/          # Resúmenes generados
│
├── .gitignore                  # Archivos a ignorar en Git
├── requirements.txt            # Dependencias
├── .streamlit/                 # Configuración de Streamlit
│   └── config.toml             # Tema y comportamiento
├── .env                        # Variables de entorno (no se sube al repositorio)
├── code_example.py             # Ejemplo de uso para probar en terminal
└── README.md                   # Documentación
```

## TODO
* Ampliar la cantidad de compañias de seguros
* Ejecutar los resumenes completos, debido a que actualmente se utilizan pocos caracteres por el tamaño de la ventana de contexto de los modelos