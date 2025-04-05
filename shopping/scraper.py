# este archivo es toda la logica destras del escrapoing , las funciones son por tienda , hay una funcion
# para todos los pruductos y tambien esta la funcion test para probar el scraping antes de hacerlo basicamnete 
# si se corren por terminal , el test seria :
# python manage.py shell 
# from shopping.scraper import test_scraping
# resultados = test_scraping()
# Y para correr el scrapper de todas las tiendas es
# python manage.py shell 
# from shopping.scraper import scrapear_todo
# scrapear_todo()

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from shopping.models import Product
from dotenv import load_dotenv
import openai
import os
import re

# Valores predeterminados para campos faltantes
DEFAULT_IMAGE = "https://via.placeholder.com/150"
DEFAULT_LINK = "https://example.com/product"
DEFAULT_NOMBRE = "Producto sin nombre"
DEFAULT_PRECIO = "0"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
}

# 🔹 Utilidad Selenium mejorada para páginas dinámicas
def get_dynamic_html(url, wait_time=10):
    print(f"⏳ Cargando página: {url}")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'user-agent={headers["User-Agent"]}')
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        
        # Esperar a que la página cargue completamente
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print(f"✅ Página cargada: {url}")
        
        # Esperar un poco más para asegurar que el JS cargue completamente
        time.sleep(3)
        
        html = driver.page_source
        driver.quit()
        return html
    except Exception as e:
        print(f"❌ Error cargando {url}: {e}")
        if 'driver' in locals():
            driver.quit()
        return ""

# Función para validar productos antes de agregarlos
def validar_producto(producto, origen):
    # Verificar campos requeridos y asignar valores predeterminados si faltan
    if 'nombre' not in producto or not producto['nombre']:
        print(f"⚠️ Producto de {origen} sin nombre, asignando valor predeterminado")
        producto['nombre'] = DEFAULT_NOMBRE
        
    if 'precio' not in producto or not producto['precio']:
        print(f"⚠️ Producto '{producto.get('nombre', 'sin nombre')}' de {origen} sin precio, asignando valor predeterminado")
        producto['precio'] = DEFAULT_PRECIO
        
    if 'link' not in producto or not producto['link']:
        print(f"⚠️ Producto '{producto.get('nombre', 'sin nombre')}' de {origen} sin link, asignando valor predeterminado")
        producto['link'] = DEFAULT_LINK
        
    if 'imagen' not in producto or not producto['imagen']:
        print(f"⚠️ Producto '{producto.get('nombre', 'sin nombre')}' de {origen} sin imagen, asignando valor predeterminado")
        producto['imagen'] = DEFAULT_IMAGE
    
    if 'origen' not in producto:
        producto['origen'] = origen
        
    return producto

# 🔸 Tennis
def scrape_tennis():
    print("🏁 Iniciando scraping de Tennis...")
    url = "https://www.tennis.com.co/"
    html = get_dynamic_html(url)
    
    if not html:
        print("❌ No se pudo obtener HTML de Tennis")
        return []
        
    soup = BeautifulSoup(html, 'html.parser')
    productos = []

    # Detectar los contenedores de productos
    product_containers = soup.select('div.vtex-product-summary-2-x-container')
    print(f"📦 Encontrados {len(product_containers)} contenedores de productos en Tennis")

    if not product_containers:
        # Intentar con otros selectores si el primero falla
        product_containers = soup.select('div[class*="product-summary"]')
        print(f"📦 Segundo intento: {len(product_containers)} contenedores encontrados")

    for idx, producto_container in enumerate(product_containers):
        try:
            print(f"Procesando producto Tennis #{idx+1}")
            nombre_elem = producto_container.select_one('span.vtex-product-summary-2-x-productBrandName') or \
                        producto_container.select_one('span[class*="productBrandName"]') or \
                        producto_container.select_one('h3')
            
            precio_elem = producto_container.select_one('span.vtex-product-price-1-x-sellingPriceValue') or \
                        producto_container.select_one('span[class*="sellingPriceValue"]') or \
                        producto_container.select_one('span[class*="price"]')
            
            link_elem = producto_container.select_one('a')
            imagen_elem = producto_container.select_one('img')
            
            producto = {}
            
            if nombre_elem:
                producto['nombre'] = nombre_elem.text.strip()
            
            if precio_elem:
                producto['precio'] = precio_elem.text.strip()
            
            if link_elem and 'href' in link_elem.attrs:
                link = link_elem['href']
                if not link.startswith('http'):
                    link = 'https://www.tennis.com.co' + link
                producto['link'] = link
            
            if imagen_elem and 'src' in imagen_elem.attrs:
                producto['imagen'] = imagen_elem['src']
            
            producto['origen'] = 'Tennis'
            
            # Validar y completar campos faltantes
            producto = validar_producto(producto, 'Tennis')
            
            productos.append(producto)
            print(f"✅ Producto Tennis encontrado: {producto['nombre']}")
        except Exception as e:
            print(f"⚠️ Error procesando producto Tennis #{idx+1}: {e}")
            continue
            
    print(f"🏁 Scraping Tennis completado. Productos encontrados: {len(productos)}")
    return productos

# 🔸 Falabella (Mujer / Hombre)
def scrape_falabella(url):
    categoria = "Mujer" if "Mujer" in url else "Hombre"
    print(f"🏁 Iniciando scraping de Falabella {categoria}...")
    html = get_dynamic_html(url, wait_time=15)  # Más tiempo para Falabella
    
    if not html:
        print(f"❌ No se pudo obtener HTML de Falabella {categoria}")
        return []
        
    soup = BeautifulSoup(html, 'html.parser')
    productos = []

    # Detectar los contenedores de productos
    product_containers = soup.select('li.grid-pod')
    print(f"📦 Encontrados {len(product_containers)} contenedores de productos en Falabella {categoria}")

    if not product_containers:
        # Intentar con otros selectores si el primero falla
        product_containers = soup.select('div[class*="pod"]') or soup.select('div[class*="product"]')
        print(f"📦 Segundo intento: {len(product_containers)} contenedores encontrados")

    for idx, producto_container in enumerate(product_containers):
        try:
            print(f"Procesando producto Falabella {categoria} #{idx+1}")
            
            nombre_elem = producto_container.select_one('b.pod-subTitle') or \
                        producto_container.select_one('div[class*="title"]') or \
                        producto_container.select_one('h3')
            
            precio_elem = producto_container.select_one('span.copy10') or \
                        producto_container.select_one('span[class*="price"]') or \
                        producto_container.select_one('div[class*="price"]')
            
            link_elem = producto_container.select_one('a')
            imagen_elem = producto_container.select_one('img')
            
            producto = {}
            
            if nombre_elem:
                producto['nombre'] = nombre_elem.text.strip()
            
            if precio_elem:
                producto['precio'] = precio_elem.text.strip()
            
            if link_elem and 'href' in link_elem.attrs:
                link = link_elem['href']
                if not link.startswith('http'):
                    link = 'https://www.falabella.com.co' + link
                producto['link'] = link
            
            if imagen_elem and 'src' in imagen_elem.attrs:
                producto['imagen'] = imagen_elem['src']
            
            producto['origen'] = f'Falabella {categoria}'
            
            # Validar y completar campos faltantes
            producto = validar_producto(producto, f'Falabella {categoria}')
            
            productos.append(producto)
            print(f"✅ Producto Falabella {categoria} encontrado: {producto['nombre']}")
        except Exception as e:
            print(f"⚠️ Error procesando producto Falabella {categoria} #{idx+1}: {e}")
            continue
            
    print(f"🏁 Scraping Falabella {categoria} completado. Productos encontrados: {len(productos)}")
    return productos

# 🔸 AE
def scrape_ae():
    print("🏁 Iniciando scraping de AE...")
    url = "https://www.ae.com.co/"
    html = get_dynamic_html(url)
    
    if not html:
        print("❌ No se pudo obtener HTML de AE")
        return []
        
    soup = BeautifulSoup(html, 'html.parser')
    productos = []

    # Detectar los contenedores de productos
    product_containers = soup.select('div.vtex-product-summary-2-x-container')
    print(f"📦 Encontrados {len(product_containers)} contenedores de productos en AE")

    if not product_containers:
        # Intentar con otros selectores si el primero falla
        product_containers = soup.select('div[class*="product-summary"]') or soup.select('div[class*="product"]')
        print(f"📦 Segundo intento: {len(product_containers)} contenedores encontrados")

    for idx, producto_container in enumerate(product_containers):
        try:
            print(f"Procesando producto AE #{idx+1}")
            
            nombre_elem = producto_container.select_one('span.vtex-product-summary-2-x-productBrandName') or \
                        producto_container.select_one('span[class*="productBrandName"]') or \
                        producto_container.select_one('h3')
            
            precio_elem = producto_container.select_one('span.vtex-product-price-1-x-sellingPriceValue') or \
                        producto_container.select_one('span[class*="sellingPriceValue"]') or \
                        producto_container.select_one('span[class*="price"]')
            
            link_elem = producto_container.select_one('a')
            imagen_elem = producto_container.select_one('img')
            
            producto = {}
            
            if nombre_elem:
                producto['nombre'] = nombre_elem.text.strip()
            
            if precio_elem:
                producto['precio'] = precio_elem.text.strip()
            
            if link_elem and 'href' in link_elem.attrs:
                link = link_elem['href']
                if not link.startswith('http'):
                    link = 'https://www.ae.com.co' + link
                producto['link'] = link
            
            if imagen_elem and 'src' in imagen_elem.attrs:
                producto['imagen'] = imagen_elem['src']
            
            producto['origen'] = 'AE'
            
            # Validar y completar campos faltantes
            producto = validar_producto(producto, 'AE')
            
            productos.append(producto)
            print(f"✅ Producto AE encontrado: {producto['nombre']}")
        except Exception as e:
            print(f"⚠️ Error procesando producto AE #{idx+1}: {e}")
            continue
            
    print(f"🏁 Scraping AE completado. Productos encontrados: {len(productos)}")
    return productos

# Cargar variables de entorno
try:
    load_dotenv(dotenv_path='openai.env')
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        openai.api_key = api_key
        print("✅ API key de OpenAI cargada correctamente")
    else:
        print("⚠️ No se encontró API key de OpenAI")
except Exception as e:
    print(f"⚠️ Error cargando variables de entorno: {e}")
    api_key = None

# 🧠 Clasificador usando ChatGPT con manejo de errores
def clasificar_producto(nombre, descripcion):
    if not api_key:
        print("⚠️ Sin API key de OpenAI. Clasificando como 'Otros'.")
        return 'Otros'
        
    prompt = f"""
    Clasifica el siguiente producto en las siguientes categorías: Camisetas, Pantalones, Zapatos, Chaquetas, Accesorios u Otros.
    Nombre: {nombre}
    Descripción: {descripcion}
    Responde solo con una de las categorías.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        categoria = response.choices[0].message.content.strip()
        if categoria not in ['Camisetas', 'Pantalones', 'Zapatos', 'Chaquetas', 'Accesorios', 'Otros']:
            return 'Otros'
        return categoria
    except Exception as e:
        print(f"⚠️ Error al clasificar con OpenAI: {e}")
        
        # Clasificación básica basada en palabras clave
        nombre_lower = nombre.lower()
        if any(keyword in nombre_lower for keyword in ['camiseta', 'blusa', 'top', 'polo', 't-shirt']):
            return 'Camisetas'
        elif any(keyword in nombre_lower for keyword in ['pantalon', 'jean', 'bermuda', 'short']):
            return 'Pantalones'
        elif any(keyword in nombre_lower for keyword in ['zapato', 'tenis', 'bota', 'sandalia']):
            return 'Zapatos'
        elif any(keyword in nombre_lower for keyword in ['chaqueta', 'abrigo', 'chamarra', 'cardigan']):
            return 'Chaquetas'
        elif any(keyword in nombre_lower for keyword in ['collar', 'anillo', 'pulsera', 'bolso', 'gorro']):
            return 'Accesorios'
        else:
            return 'Otros'

# 🔢 Convertidor de precio en texto a decimal mejorado
def extraer_precio(precio_texto):
    try:
        # Eliminar símbolos de moneda y separadores
        precio_limpio = re.sub(r'[^\d.,]', '', precio_texto)
        # Manejar diferentes formatos de números
        if ',' in precio_limpio and '.' in precio_limpio:
            if precio_limpio.find(',') > precio_limpio.find('.'):
                precio_limpio = precio_limpio.replace('.', '').replace(',', '.')
            else:
                precio_limpio = precio_limpio.replace(',', '')
        elif ',' in precio_limpio:
            precio_limpio = precio_limpio.replace(',', '.')
            
        # Convertir a float
        return float(precio_limpio)
    except Exception as e:
        print(f"⚠️ Error convirtiendo precio '{precio_texto}': {e}")
        return 0.0
    
def scrapear_todo():
    print("🚀 Iniciando scraping...")

    productos = []
    
    # Intentar scraping de cada sitio y capturar cualquier error
    try:
        tennis_products = scrape_tennis()
        print(f"Tennis products: {len(tennis_products)}")
        if tennis_products:  # Solo añadir si hay productos
            productos += tennis_products
    except Exception as e:
        print(f"❌ Error en scrape_tennis: {e}")
    
    try:
        falabella_mujer = scrape_falabella("https://www.falabella.com.co/falabella-co/category/cat2321031/Mujer")
        print(f"Falabella mujer products: {len(falabella_mujer)}")
        if falabella_mujer:  # Solo añadir si hay productos
            productos += falabella_mujer
    except Exception as e:
        print(f"❌ Error en scrape_falabella mujer: {e}")
    
    try:
        falabella_hombre = scrape_falabella("https://www.falabella.com.co/falabella-co/category/cat5521012/Hombre")
        print(f"Falabella hombre products: {len(falabella_hombre)}")
        if falabella_hombre:  # Solo añadir si hay productos
            productos += falabella_hombre
    except Exception as e:
        print(f"❌ Error en scrape_falabella hombre: {e}")
    
    try:
        ae_products = scrape_ae()
        print(f"AE products: {len(ae_products)}")
        if ae_products:  # Solo añadir si hay productos
            productos += ae_products
    except Exception as e:
        print(f"❌ Error en scrape_ae: {e}")
    
    print(f"🔢 Total productos encontrados: {len(productos)}")

    if not productos:
        print("⚠️ No se encontraron productos para procesar")
        return

    productos_guardados = 0
    
    for idx, p in enumerate(productos):
        try:
            print(f"Procesando producto {idx+1}/{len(productos)}: {p.get('nombre', 'Sin nombre')}")
            
            # Verificar que todos los campos necesarios existan
            if not all(key in p for key in ['nombre', 'precio', 'link', 'imagen', 'origen']):
                print(f"⚠️ Producto {idx+1} incompleto. Campos disponibles: {list(p.keys())}")
                # Completar campos faltantes
                p = validar_producto(p, p.get('origen', 'Desconocido'))
            
            descripcion = f"Producto de la tienda {p['origen']}"
            categoria = clasificar_producto(p['nombre'], descripcion)
            precio = extraer_precio(p['precio'])

            print(f"Guardando producto: Nombre={p['nombre']}, Precio={precio}, Categoría={categoria}")
            
            product, created = Product.objects.get_or_create(
                productLink=p['link'],  # Clave única
                defaults={
                    'productName': p['nombre'],
                    'productDescription': descripcion,
                    'productPicture': p['imagen'],
                    'productPrice': precio,
                    'productCategory': categoria,
                    'productBrand': p['origen'],
                    'productBuyLink': p['link'],
                    'productStock': 10,
                    'productOrigin': p['origen'],
                }
            )
            
            if created:
                productos_guardados += 1
                print(f"✅ Nuevo producto guardado: {p['nombre']}")
            else:
                print(f"ℹ️ Producto ya existe: {p['nombre']}")
                
        except Exception as e:
            print(f"❌ Error al guardar producto {idx+1}: {e}")
            print(f"Datos del producto problemático: {p}")

    print(f"✅ Scraping completado. {productos_guardados} nuevos productos guardados de {len(productos)} encontrados.")

# Función de prueba para identificar dónde está el error
def test_scraping():
    print("🧪 Iniciando prueba de scraping...")
    
    # Probar cada scraper individualmente
    print("\n==== Tennis ====")
    tennis_products = []
    try:
        tennis_products = scrape_tennis()
        print(f"Tennis devolvió {len(tennis_products)} productos")
        if tennis_products:
            print("Ejemplo de producto Tennis:")
            print(tennis_products[0])
    except Exception as e:
        print(f"❌ Error en scrape_tennis: {e}")
    
    print("\n==== Falabella Mujer ====")
    falabella_mujer = []
    try:
        falabella_mujer = scrape_falabella("https://www.falabella.com.co/falabella-co/category/cat2321031/Mujer")
        print(f"Falabella Mujer devolvió {len(falabella_mujer)} productos")
        if falabella_mujer:
            print("Ejemplo de producto Falabella Mujer:")
            print(falabella_mujer[0])
    except Exception as e:
        print(f"❌ Error en scrape_falabella mujer: {e}")
    
    print("\n==== Falabella Hombre ====")
    falabella_hombre = []
    try:
        falabella_hombre = scrape_falabella("https://www.falabella.com.co/falabella-co/category/cat5521012/Hombre")
        print(f"Falabella Hombre devolvió {len(falabella_hombre)} productos")
        if falabella_hombre:
            print("Ejemplo de producto Falabella Hombre:")
            print(falabella_hombre[0])
    except Exception as e:
        print(f"❌ Error en scrape_falabella hombre: {e}")
    
    print("\n==== AE ====")
    ae_products = []
    try:
        ae_products = scrape_ae()
        print(f"AE devolvió {len(ae_products)} productos")
        if ae_products:
            print("Ejemplo de producto AE:")
            print(ae_products[0])
    except Exception as e:
        print(f"❌ Error en scrape_ae: {e}")
    
    print("\n🧪 Prueba de scraping completada")
    return {
        'tennis': tennis_products,
        'falabella_mujer': falabella_mujer, 
        'falabella_hombre': falabella_hombre,
        'ae': ae_products
    }
