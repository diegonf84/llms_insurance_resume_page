# main.py
import logging
import os
from app.website_extractor import WebsiteExtractor
from app.content_processor import get_all_pages_content
from app.summarizer import summarize_with_gemini
from app.comparator import compare_insurance_companies
from app.config import MAX_PAGES

def setup_logging():
    """Configurar el sistema de logs"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('website_summary.log')
        ]
    )

def procesar_aseguradora(url, nombre_cia):
    """Procesa una aseguradora extrayendo y resumiendo su contenido"""
    logging.info(f"Iniciando proceso para {nombre_cia}: {url}")
    
    # Crear extractor para el sitio web
    extractor = WebsiteExtractor(url)
    
    # Extraer enlaces
    logging.info(f"Extrayendo enlaces de {nombre_cia}")
    extractor.extract_links()
    
    # Filtrar enlaces
    logging.info(f"Filtrando enlaces de {nombre_cia}")
    filtered_links = extractor.filter_links()
    
    # Obtener contenido de las páginas
    logging.info(f"Obteniendo contenido de hasta {MAX_PAGES} páginas de {nombre_cia}")
    content = get_all_pages_content(filtered_links, max_pages=MAX_PAGES)
    
    # Resumir contenido (limitado a 100K caracteres para evitar limitaciones de la API)
    logging.info(f"Resumiendo contenido de {nombre_cia}")
    summary = summarize_with_gemini(content[:50_000])
    
    # Guardar en archivo
    output_file = f"resumen_{nombre_cia}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    logging.info(f"Resumen de {nombre_cia} guardado en {output_file}")
    return summary

def main():
    """Función principal para extraer, resumir y comparar aseguradoras"""
    setup_logging()
    
    # Definir las aseguradoras a analizar
    aseguradoras = [
        {"nombre": "fedpat", "url": "https://www.fedpat.com.ar/"},
        {"nombre": "sancor", "url": "https://www.sancorseguros.com.ar/"}
    ]
    
    resumenes = {}
    
    # Procesar cada aseguradora
    for aseguradora in aseguradoras:
        nombre = aseguradora["nombre"]
        url = aseguradora["url"]
        
        # Verificar si ya existe un resumen guardado
        archivo_resumen = f"resumen_{nombre}.md"
        if os.path.exists(archivo_resumen):
            logging.info(f"Usando resumen existente para {nombre}")
            with open(archivo_resumen, 'r', encoding='utf-8') as f:
                resumenes[nombre] = f.read()
        else:
            # Procesar la aseguradora
            resumenes[nombre] = procesar_aseguradora(url, nombre)
    
    # Comparar las aseguradoras
    if len(resumenes) >= 2:
        logging.info("Generando comparativa entre aseguradoras")
        nombres = list(resumenes.keys())
        comparativa = compare_insurance_companies(
            resumenes[nombres[0]], 
            resumenes[nombres[1]], 
            nombres[0], 
            nombres[1]
        )
        
        # Guardar comparativa
        archivo_comparativa = f"comparativa_{nombres[0]}_{nombres[1]}.md"
        with open(archivo_comparativa, 'w', encoding='utf-8') as f:
            f.write(comparativa)
        
        # Mostrar comparativa en consola
        print("\n" + "="*80 + "\n")
        print("COMPARATIVA DE ASEGURADORAS:")
        print("="*80)
        print(comparativa)
        print("="*80 + "\n")
        
        logging.info(f"Comparativa guardada en {archivo_comparativa}")
    
    logging.info("Proceso finalizado con éxito")

if __name__ == "__main__":
    main()