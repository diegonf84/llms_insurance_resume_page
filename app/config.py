# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Web Scraping Settings
DEFAULT_USER_AGENT = 'Mozilla/5.0'
REQUEST_TIMEOUT = 10
MAX_PAGES = 100
MAX_WORKERS = 2
CONTENT_SEPARATOR = "\n\n"

# Link Filtering
EXCLUDE_PATTERNS = [
    # Archivos multimedia y documentos
    '.pdf', '.jpg', '.png', '.mp4', '.avi', '.svg', '.jpeg', '.gif', '.webp',
    # Archivos de recursos web
    '.js', '.css', '.min.js', '.map',
    # Rutas de recursos
    '/wp-content/', '/wp-includes/', '/plugins/', '/themes/',
    # Bibliotecas comunes
    'jquery', 'bootstrap', 'fontawesome',
    # Páginas legales
    '/terminos', '/condiciones', '/cookies', '/privacidad',
    # Otros no relevantes
    'cdn.', '/wp-json/', '/feed/', '/embed/'
]

PRIORITY_PATTERNS = ["/productos", "/seguros", "/coberturas", "/siniestros", "/contacto"]

# Summarization Settings
SUMMARY_MAX_TOKENS = 1024
SUMMARY_TEMPERATURE = 0.2
SUMMARY_TOP_P = 0.95
SUMMARY_TOP_K = 40

# Comparison Settings
COMPARATIVE_MAX_TOKENS = 4096
MAX_CHARS_FOR_ANALYSIS = 70000