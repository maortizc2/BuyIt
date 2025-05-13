import openai
from openai import OpenAI
from dotenv import load_dotenv
import os

# Carga .env solo si no está cargado (opcional seguridad extra)
load_dotenv(dotenv_path='openai.env')

def comparar_dos_productos_ai(producto_a, producto_b):
    """
    Compara dos productos usando GPT-3.5-Turbo y devuelve un análisis profesional estructurado
    con descripciones visuales animadas, emojis e insignias destacadas.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No se encontró la API key. Asegúrate de tener openai.env bien configurado.")
        return "⚠️ Error: Falta la clave de API de OpenAI."

    client = OpenAI(api_key=api_key)

    prompt = f"""
Eres un experto en análisis comparativo de productos de moda.
Quiero que compares estos dos productos de forma profesional y visualmente atractiva.
Usa emojis para representar atributos clave, usa insignias visuales como 🔥 Más Popular, ⭐ Alta Calidad, 🛍️ Mejor Oferta, etc.

1. Presenta una tabla comparativa con los siguientes campos:
    🏷️ Nombre | 💰 Precio | 📂 Categoría | 🌍 Origen | 🔗 Enlace

2. Luego, haz un análisis profesional con estilo editorial visual:
    - Incluye fortalezas y debilidades de cada producto.
    - Describe sus usos ideales, tipo de usuario que los disfrutaría más.
    - Usa frases elegantes y expresivas, añade reacciones del tipo "✨ Ideal para...", "🔥 Brilla en...", "💎 Destaca por...".

3. Finaliza con una conclusión comparativa clara y que incluya una recomendación según el perfil del comprador.

Producto A:
🏷️ Nombre: {producto_a.productName}
💰 Precio: {producto_a.productPrice}
📂 Categoría: {producto_a.productCategory}
🌍 Origen: {producto_a.productOrigin}
🔗 Enlace: {producto_a.productLink}

Producto B:
🏷️ Nombre: {producto_b.productName}
💰 Precio: {producto_b.productPrice}
📂 Categoría: {producto_b.productCategory}
🌍 Origen: {producto_b.productOrigin}
🔗 Enlace: {producto_b.productLink}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asesor experto en productos de moda y tecnología, tu misión es presentar comparaciones elegantes y visuales."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Error en comparación AI: \n\n{e}")
        return "⚠️ Error al generar el análisis comparativo con IA."