import streamlit as st
import json
import os
import logging
from website_extractor import WebsiteExtractor
from content_processor import get_all_pages_content
from summarizer import summarize_with_gemini
from comparator import compare_insurance_companies
from config import MAX_PAGES, MAX_CHARS_FOR_ANALYSIS, COMPARATIVE_MAX_TOKENS

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def cargar_aseguradoras():
    """Carga la lista de aseguradoras desde el archivo JSON"""
    try:
        with open("app/data/aseguradoras.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error al cargar aseguradoras: {e}")
        return []

def procesar_aseguradora(aseguradora, max_chars):
    """Procesa una aseguradora extrayendo y resumiendo su contenido"""
    nombre = aseguradora["id"]
    url = aseguradora["url"]
    
    # Verificar si ya existe un resumen guardado
    archivo_resumen = f"app/data/summaries/resumen_{nombre}.md"
    if os.path.exists(archivo_resumen):
        st.info(f"Resumen de {aseguradora['nombre']} ya existente, cargando...")
        with open(archivo_resumen, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Mostrar progreso
    progress_placeholder = st.empty()
    status_text = st.empty()
    
    # Extraer y procesar
    status_text.text(f"Extrayendo enlaces de {aseguradora['nombre']}...")
    extractor = WebsiteExtractor(url)
    extractor.extract_links()
    progress_placeholder.progress(20)
    
    status_text.text(f"Filtrando enlaces de {aseguradora['nombre']}...")
    filtered_links = extractor.filter_links()
    progress_placeholder.progress(30)
    
    status_text.text(f"Extrayendo contenido de {aseguradora['nombre']}...")
    content = get_all_pages_content(filtered_links, max_pages=MAX_PAGES)
    progress_placeholder.progress(70)
    
    status_text.text(f"Generando resumen de {aseguradora['nombre']}...")
    summary = summarize_with_gemini(content[:max_chars])
    progress_placeholder.progress(100)
    
    # Guardar resumen
    with open(archivo_resumen, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    status_text.text(f"Procesamiento de {aseguradora['nombre']} completado.")
    
    return summary

def main():
    st.set_page_config(
        page_title="Comparador de Aseguradoras",
        page_icon="🔍",
        layout="wide"
    )
    
    # Título en la página principal
    st.title("Web Insurance Analyzer")
    st.markdown("Herramienta para comparar información de sitios web de 2 aseguradoras del mercado en Argentina")
    
    # Cargar aseguradoras
    aseguradoras = cargar_aseguradoras()
    if not aseguradoras:
        st.error("No se pudieron cargar las aseguradoras.")
        return
    
    # Crear opciones para los selectores
    opciones = {aseg["id"]: aseg["nombre"] for aseg in aseguradoras}
    
    # Panel lateral para selección
    with st.sidebar:
        st.header("Parámetros de comparación")
        
        # Seleccionar primera aseguradora
        cia1_id = st.selectbox(
            "Primera aseguradora",
            options=list(opciones.keys()),
            format_func=lambda x: opciones[x]
        )
        
        # Filtrar la primera opción para la segunda selección
        opciones_filtradas = {k: v for k, v in opciones.items() if k != cia1_id}
        cia2_id = st.selectbox(
            "Segunda aseguradora",
            options=list(opciones_filtradas.keys()),
            format_func=lambda x: opciones[x]
        )
        
        # Slider para el máximo de caracteres
        max_chars = st.slider(
            "Máximo de caracteres para análisis", 
            min_value=10000, 
            max_value=60000, 
            value=MAX_CHARS_FOR_ANALYSIS,
            step=1000,
            help="Mayor cantidad de caracteres puede resultar en un análisis más completo pero aumenta el tiempo de procesamiento."
        )
        
        st.markdown("---")
        
        # Botones de acción
        comparar_btn = st.button("Comparar Aseguradoras", use_container_width=True)
        reset_btn = st.button("Nuevo Análisis", type="secondary", use_container_width=True)
    
    # Lógica para resetear archivos de comparación
    if reset_btn:
        # Obtener las compañías seleccionadas
        cia1 = next((a for a in aseguradoras if a["id"] == cia1_id), None)
        cia2 = next((a for a in aseguradoras if a["id"] == cia2_id), None)
        
        if cia1 and cia2:
            # Eliminar archivo de comparativa si existe
            archivo_comparativa = f"comparativa_{cia1_id}_{cia2_id}.md"
            if os.path.exists(archivo_comparativa):
                try:
                    os.remove(archivo_comparativa)
                    st.success(f"Comparativa entre {cia1['nombre']} y {cia2['nombre']} eliminada. Puedes generar una nueva.")
                except Exception as e:
                    st.error(f"Error al eliminar comparativa: {e}")
    
    # Iniciar comparación
    if comparar_btn:
        # Encontrar las aseguradoras seleccionadas
        cia1 = next((a for a in aseguradoras if a["id"] == cia1_id), None)
        cia2 = next((a for a in aseguradoras if a["id"] == cia2_id), None)
        
        if not cia1 or not cia2:
            st.error("Error al seleccionar aseguradoras.")
            return
        
        st.subheader("Procesando información")
        
        # Procesar aseguradoras
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"Procesando {cia1['nombre']}...")
            resumen1 = procesar_aseguradora(cia1, max_chars)
        
        with col2:
            st.write(f"Procesando {cia2['nombre']}...")
            resumen2 = procesar_aseguradora(cia2, max_chars)
        
        # Comparar
        st.subheader("Generando comparativa...")
        archivo_comparativa = f"comparativa_{cia1_id}_{cia2_id}.md"
        
        # Verificar si ya existe la comparativa
        if os.path.exists(archivo_comparativa):
            st.info("Cargando comparativa existente...")
            with open(archivo_comparativa, 'r', encoding='utf-8') as f:
                comparativa = f.read()
        else:
            with st.spinner("Generando nuevo análisis comparativo..."):
                comparativa = compare_insurance_companies(
                    resumen1, resumen2, cia1["nombre"], cia2["nombre"]
                )
        
        # Mostrar resultados
        st.markdown("---")
        st.markdown("<h2 style='text-align: center;'>Análisis Comparativo</h2>", unsafe_allow_html=True)
        st.markdown(comparativa)
        
        # Opción para descargar
        st.download_button(
            label="Descargar Comparativa",
            data=comparativa,
            file_name=f"comparativa_{cia1_id}_{cia2_id}.md",
            mime="text/markdown"
        )

if __name__ == "__main__":
    main()