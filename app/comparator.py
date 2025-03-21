# comparator.py
import logging
import google.generativeai as genai
from config import GEMINI_API_KEY, SUMMARY_TEMPERATURE, COMPARATIVE_MAX_TOKENS

class APILimitError(Exception):
    """Error personalizado para límites de API y otros errores de Gemini"""
    pass

def compare_insurance_companies(resumen1, resumen2, nombre_cia1, nombre_cia2):
    """
    Compara dos compañías de seguros basándose en sus resúmenes.
    
    Args:
        resumen1: Resumen de la primera compañía
        resumen2: Resumen de la segunda compañía
        nombre_cia1: Nombre de la primera compañía
        nombre_cia2: Nombre de la segunda compañía
        
    Returns:
        Análisis comparativo en formato markdown
        
    Raises:
        APILimitError: Si hay problemas con la API de Gemini
    """
    logging.info(f"Iniciando comparación entre {nombre_cia1} y {nombre_cia2}")
    
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY no encontrada en variables de entorno")
        
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Configurar modelo
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config={
            "temperature": SUMMARY_TEMPERATURE,
            "max_output_tokens": COMPARATIVE_MAX_TOKENS,
        }
    )
    
    # Crear prompt para la comparación
    prompt = f"""
    Necesito un análisis comparativo detallado entre dos compañías de seguros argentinas: {nombre_cia1} y {nombre_cia2}.
    
    IMPORTANTE: Este análisis debe basarse EXCLUSIVAMENTE en la información extraída de los sitios web oficiales de ambas compañías. No debes incorporar conocimiento externo sobre estas aseguradoras que no aparezca en los resúmenes proporcionados.
    
    A continuación te proporciono los resúmenes extraídos de sus sitios web:
    
    ## {nombre_cia1}:
    {resumen1}
    
    ## {nombre_cia2}:
    {resumen2}
    
    Por favor, realiza un análisis comparativo completo que incluya:
    
    1. TABLA COMPARATIVA: Crea una tabla markdown comparando ambas compañías en las siguientes categorías:
       - Variedad de productos y coberturas
       - Servicios digitales y app
       - Proceso de siniestros
       - Canales de atención al cliente
       - Propuesta de valor única
    
    2. FORTALEZAS Y DEBILIDADES: Analiza las principales fortalezas y debilidades de cada compañía respecto a su competidora.
    
    3. RECOMENDACIONES: En qué casos conviene elegir una u otra compañía según:
       - Perfil del cliente (particular, empresa, profesional)
       - Tipo de cobertura necesitada
       - Preferencias de servicio (digital vs tradicional)
    
    4. CONCLUSIONES: Síntesis final de la comparativa con los puntos más relevantes.
    
    5. LIMITACIONES DEL ANÁLISIS: Incluye un párrafo explicando que este análisis está limitado a la información disponible en los sitios web oficiales, y puede no reflejar la experiencia real de los clientes o todas las características y coberturas de cada compañía.
    
    Responde en formato markdown bien estructurado, usando tablas, negritas, y listas para facilitar la lectura.
    Sé objetivo y equilibrado en tu análisis, basándote ESTRICTAMENTE en la información proporcionada en los resúmenes extraídos de los sitios web.
    """
    
    # Generar respuesta
    logging.info("Generando análisis comparativo")
    try:
        response = model.generate_content(prompt)
        logging.info("Análisis comparativo generado con éxito")
        return response.text
    except Exception as e:
        logging.error(f"Error al generar análisis comparativo con Gemini API: {e}")
        raise APILimitError("Error al comunicarse con la API de Gemini. Posiblemente se alcanzó el límite de uso.")