# summarizer.py
import logging
import google.generativeai as genai
from config import (
    GEMINI_API_KEY, SUMMARY_MAX_TOKENS, SUMMARY_TEMPERATURE,
    SUMMARY_TOP_P, SUMMARY_TOP_K
)

class APILimitError(Exception):
    """Error personalizado para límites de API y otros errores de Gemini"""
    pass

def summarize_with_gemini(content, max_tokens=SUMMARY_MAX_TOKENS):
    """
    Use Gemini Pro 1.5 to summarize extensive content.
    
    Args:
        content: Text to summarize
        max_tokens: Maximum length of the summary
    
    Returns:
        Generated summary
    
    Raises:
        APILimitError: Si hay problemas con la API de Gemini
    """
    logging.info("Starting content summarization with Gemini API")
    
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
        
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Configure model
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config={
            "temperature": SUMMARY_TEMPERATURE,
            "top_p": SUMMARY_TOP_P,
            "top_k": SUMMARY_TOP_K,
            "max_output_tokens": max_tokens,
        }
    )
    
    # Create prompt
    prompt = f"""
    Por favor, genera un resumen conciso pero completo del siguiente texto sobre una webpage de seguros de Argentina
    Incluye información clave sobre los productos, servicios, formas de contacto, siniestros y propuestas de valor.
    Responde en formato markdown.
    
    TEXTO:
    {content}
    
    RESUMEN:
    """
    
    logging.info(f"Sending {len(content)} characters to summarize")
    
    # Generate response
    try:
        response = model.generate_content(prompt)
        logging.info("Summary generated successfully")
        return response.text
    except Exception as e:
        logging.error(f"Error al generar resumen con Gemini API: {e}")
        raise APILimitError("Error al comunicarse con la API de Gemini. Posiblemente se alcanzó el límite de uso.")