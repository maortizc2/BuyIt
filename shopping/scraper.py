from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from shopping.models import Product
from dotenv import load_dotenv
import openai,time,os,re,requests,random,uuid

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
}

# Funciones para generar valores dinámicos
def generate_default_image():
    return f"https://via.placeholder.com/200x200.png?text=Producto+{uuid.uuid4().hex[:100]}"

def generate_default_link():
    links = ["https://www.americanino.com/","https://www.mercedescampuzano.com/","https://www.arturocalle.com","https://www.ae.com.co/", "https://www.tennis.com.co/" ]
    return random.choice(links)

def generate_default_nombre():
    nombres_genericos = ["Camisa", "Buso", "Chaqueta", "Pantalon", "Jean"]
    colores = ["color blanco", "color negro", "color rojo", "Tela suave", " de cuero", "con estampado"]
    return f"{random.choice(nombres_genericos)} {random.choice(colores)}"

def generate_default_precio():
    return f"{random.randint(50000, 500000):,.0f}".replace(",", ".")


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
    if 'nombre' not in producto or not producto['nombre']:
        producto['nombre'] = generate_default_nombre()
        print(f"⚠️ Producto de {origen} sin nombre, asignando valor: {producto['nombre']}")

    if 'precio' not in producto or not producto['precio']:
        producto['precio'] = generate_default_precio()
        print(f"⚠️ Producto '{producto['nombre']}' de {origen} sin precio, asignando valor: {producto['precio']}")

    if 'link' not in producto or not producto['link']:
        producto['link'] = generate_default_link()
        print(f"⚠️ Producto '{producto['nombre']}' de {origen} sin link, asignando valor: {producto['link']}")

    if 'imagen' not in producto or not producto['imagen']:
        producto['imagen'] = generate_default_image()
        print(f"⚠️ Producto '{producto['nombre']}' de {origen} sin imagen, asignando valor: {producto['imagen']}")

    if 'origen' not in producto:
        producto['origen'] = origen

    return producto

# 🔸 Mercedes Campuzano
def scrape_mercedes_campuzano():
    print("🏁 Iniciando scraping de Mercedes Campuzano...")
    url = "https://www.mercedescampuzano.com/"
    html = get_dynamic_html(url, wait_time=15)  # Aumentar tiempo de espera para cargar todos los elementos dinámicos
    
    if not html:
        print("❌ No se pudo obtener HTML de Mercedes Campuzano")
        return []
        
    soup = BeautifulSoup(html, 'html.parser')
    productos = []

    # Mercedes Campuzano usa VTEX como plataforma, similar a Tennis y AE
    product_containers = soup.select('div.vtex-product-summary-2-x-container, div.product-summary')
    print(f"📦 Encontrados {len(product_containers)} contenedores de productos en Mercedes Campuzano")

    if not product_containers:
        # Intentar con otros selectores más genéricos
        product_containers = soup.select('div[class*="product-summary"], div[class*="productSummary"], div.vtex-shelf-components-0-x-slide')
        print(f"📦 Segundo intento: {len(product_containers)} contenedores encontrados")

    for idx, producto_container in enumerate(product_containers):
        try:
            print(f"Procesando producto Mercedes Campuzano #{idx+1}")
            
            # Selectores más específicos para Mercedes Campuzano
            nombre_elem = producto_container.select_one('span.vtex-product-summary-2-x-productBrandName, h3.vtex-product-summary-2-x-productNameContainer') or \
                        producto_container.select_one('h1, h2, h3, span[class*="productName"], div[class*="productName"]')
            
            precio_elem = producto_container.select_one('span.vtex-product-price-1-x-sellingPriceValue, span.price-new') or \
                        producto_container.select_one('span[class*="sellingPrice"], span[class*="price"], div[class*="price"]')
            
            link_elem = producto_container.select_one('a[class*="product"], a')
            imagen_elem = producto_container.select_one('img[class*="image"], img.vtex-product-summary-2-x-image, img')
            
            producto = {}
            
            if nombre_elem:
                producto['nombre'] = re.sub(r'\s+', ' ', nombre_elem.text).strip()
            
            if precio_elem:
                producto['precio'] = precio_elem.text.strip()
            
            if link_elem and 'href' in link_elem.attrs:
                link = link_elem['href']
                if not link.startswith('http'):
                    link = 'https://www.mercedescampuzano.com' + link
                producto['link'] = link
            
            if imagen_elem:
                if 'src' in imagen_elem.attrs:
                    producto['imagen'] = imagen_elem['src']
                elif 'data-src' in imagen_elem.attrs:  # Algunas páginas usan carga perezosa
                    producto['imagen'] = imagen_elem['data-src']
            
            producto['origen'] = 'Mercedes Campuzano'
            
            # Validar y completar campos faltantes
            producto = validar_producto(producto, 'Mercedes Campuzano')
            
            productos.append(producto)
            print(f"✅ Producto Mercedes Campuzano encontrado: {producto['nombre']}")
        except Exception as e:
            print(f"⚠️ Error procesando producto Mercedes Campuzano #{idx+1}: {e}")
            continue
            
    print(f"🏁 Scraping Mercedes Campuzano completado. Productos encontrados: {len(productos)}")
    return productos

# 🔸 Arturo Calle
def scrape_arturo_calle():
    print("🏁 Iniciando scraping de Arturo Calle...")
    url = "https://www.arturocalle.com/"
    html = get_dynamic_html(url, wait_time=15)  # Aumentar tiempo de espera para sitios con mucho JS
    
    if not html:
        print("❌ No se pudo obtener HTML de Arturo Calle")
        return []
        
    soup = BeautifulSoup(html, 'html.parser')
    productos = []

    # Arturo Calle usa tecnología diferente, probar con varios selectores
    product_containers = soup.select('.product-item-info, .products-grid .item')
    print(f"📦 Encontrados {len(product_containers)} contenedores de productos en Arturo Calle")

    if not product_containers:
        # Intentar con otros selectores más genéricos
        product_containers = soup.select('div[class*="product"], li[class*="product-item"], div.product-item')
        print(f"📦 Segundo intento: {len(product_containers)} contenedores encontrados")
    
    for idx, producto_container in enumerate(product_containers):
        try:
            print(f"Procesando producto Arturo Calle #{idx+1}")
            
            # Selectores específicos para Arturo Calle (Magento)
            nombre_elem = producto_container.select_one('a.product-item-link, .product-name a, .product-name') or \
                            producto_container.select_one('h2.product-name, h3.product-name')
            
            precio_elem = producto_container.select_one('span.price, span.regular-price, span.special-price') or \
                        producto_container.select_one('div[class*="price"]')
            
            link_elem = producto_container.select_one('a.product-item-link, a.product-image, a.product') or \
                        producto_container.select_one('a')
            
            imagen_elem = producto_container.select_one('img.product-image-photo, img.product-thumb, img')

            
            producto = {}
            
            if nombre_elem:
                producto['nombre'] = re.sub(r'\s+', ' ', nombre_elem.text).strip()
            
            if precio_elem:
                precio_texto = precio_elem.text.strip()
                producto['precio'] = precio_texto
            
            if link_elem and 'href' in link_elem.attrs:
                link = link_elem['href']
                if not link.startswith('http'):
                    link = 'https://www.arturocalle.com' + link
                producto['link'] = link
            
            if imagen_elem:
                if 'src' in imagen_elem.attrs:
                    producto['imagen'] = imagen_elem['src']
                elif 'data-src' in imagen_elem.attrs:  # Imágenes con carga perezosa
                    producto['imagen'] = imagen_elem['data-src']
            
            producto['origen'] = 'Arturo Calle'
            
            # Validar y completar campos faltantes
            producto = validar_producto(producto, 'Arturo Calle')
            
            productos.append(producto)
            print(f"✅ Producto Arturo Calle encontrado: {producto['nombre']}")
        except Exception as e:
            print(f"⚠️ Error procesando producto Arturo Calle #{idx+1}: {e}")
            continue
            
    print(f"🏁 Scraping Arturo Calle completado. Productos encontrados: {len(productos)}")
    return productos

# 🔸 Americanino
def scrape_americanino():
    print("🏁 Iniciando scraping de Americanino...")
    url = "https://www.americanino.com/"
    html = get_dynamic_html(url, wait_time=15)
    
    if not html:
        print("❌ No se pudo obtener HTML de Americanino")
        return []
        
    soup = BeautifulSoup(html, 'html.parser')
    productos = []

    # Americanino parece usar VTEX como plataforma, similar a Tennis
    product_containers = soup.select('div.vtex-product-summary-2-x-container, article.vtex-product-summary-2-x-element')
    print(f"📦 Encontrados {len(product_containers)} contenedores de productos en Americanino")

    if not product_containers:
        # Intentar con otros selectores típicos de VTEX
        product_containers = soup.select('div[class*="productSummary"], div[class*="product-summary"], section[class*="shelf"]')
        print(f"📦 Segundo intento: {len(product_containers)} contenedores encontrados")
    
    # Tercer intento - buscar en los sliders/carruseles de productos destacados
    if not product_containers:
        product_containers = soup.select('div.shelf-slider div[class*="slide"], div[class*="carousel"] div[class*="product"]')
        print(f"📦 Tercer intento: {len(product_containers)} contenedores encontrados")

    for idx, producto_container in enumerate(product_containers):
        try:
            print(f"Procesando producto Americanino #{idx+1}")
            
            # Selectores específicos para Americanino (parece usar VTEX)
            nombre_elem = producto_container.select_one('span.vtex-product-summary-2-x-productBrandName, h3.vtex-product-summary-2-x-productNameContainer') or \
                        producto_container.select_one('h1, h2, h3, span[class*="productName"], div[class*="productName"]')
            
            precio_elem = producto_container.select_one('span.vtex-product-price-1-x-sellingPriceValue, div.vtex-product-price-1-x-sellingPrice') or \
                        producto_container.select_one('span[class*="sellingPrice"], span[class*="price"], div[class*="price"]')
            
            link_elem = producto_container.select_one('a.vtex-product-summary-2-x-clearLink, a[class*="product"], a')
            imagen_elem = producto_container.select_one('img.vtex-product-summary-2-x-image, img[class*="image"], img')
                        

            
            producto = {}
            
            if nombre_elem:
                producto['nombre'] = re.sub(r'\s+', ' ', nombre_elem.text).strip()
            
            if precio_elem:
                producto['precio'] = precio_elem.text.strip()
            
            if link_elem and 'href' in link_elem.attrs:
                link = link_elem['href']
                if not link.startswith('http'):
                    link = 'https://www.americanino.com' + link
                producto['link'] = link
            
            if imagen_elem:
                if 'src' in imagen_elem.attrs:
                    producto['imagen'] = imagen_elem['src']
                elif 'data-src' in imagen_elem.attrs:  # Imágenes con carga perezosa
                    producto['imagen'] = imagen_elem['data-src']
            
            producto['origen'] = 'Americanino'
            
            # Validar y completar campos faltantes
            producto = validar_producto(producto, 'Americanino')
            
            productos.append(producto)
            print(f"✅ Producto Americanino encontrado: {producto['nombre']}")
        except Exception as e:
            print(f"⚠️ Error procesando producto Americanino #{idx+1}: {e}")
            continue
            
    print(f"🏁 Scraping Americanino completado. Productos encontrados: {len(productos)}")
    return productos

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
            
            link_elem = producto_container.select_one('a') or\
                        producto_container.select_one('a[href]')
            imagen_elem = producto_container.select_one('img') or\
                        producto_container.select_one('img[src]')

            
            producto = {}
            
            if nombre_elem:
                producto['nombre'] = re.sub(r'\s+', ' ', nombre_elem.text).strip()
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
            imagen_elem = producto_container.select_one('img') or\
                            producto_container.select_one('img[src]')

            
            producto = {}
            
            if nombre_elem:
                producto['nombre'] = re.sub(r'\s+', ' ', nombre_elem.text).strip()
            
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
        mercedes_products = scrape_mercedes_campuzano()
        print(f"Mercedes Campuzano products: {len(mercedes_products)}")
        if mercedes_products:  # Solo añadir si hay productos
            productos += mercedes_products
    except Exception as e:
        print(f"❌ Error en scrape_mercedes_campuzano: {e}")
        
    try:
        arturo_products = scrape_arturo_calle()
        print(f"Arturo Calle products: {len(arturo_products)}")
        if arturo_products:  # Solo añadir si hay productos
            productos += arturo_products
    except Exception as e:
        print(f"❌ Error en scrape_arturo_calle: {e}")
        
    try:
        americanino_products = scrape_americanino()
        print(f"Americanino products: {len(americanino_products)}")
        if americanino_products:  # Solo añadir si hay productos
            productos += americanino_products
    except Exception as e:
        print(f"❌ Error en scrape_americanino: {e}")
    try:
        tennis_products = scrape_tennis()
        print(f"Tennis products: {len(tennis_products)}")
        if tennis_products:  # Solo añadir si hay productos
            productos += tennis_products
    except Exception as e:
        print(f"❌ Error en scrape_tennis: {e}")
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
    
    # Probar cada scraper individualmente'
    print("\n==== Mercedes Campuzano ====")
    mercedes_products = []
    try:
        mercedes_products = scrape_mercedes_campuzano()
        print(f"Mercedes Campuzano devolvió {len(mercedes_products)} productos")
        if mercedes_products:
            print("Ejemplo de producto Mercedes Campuzano:")
            print(mercedes_products[0])
    except Exception as e:
        print(f"❌ Error en scrape_mercedes_campuzano: {e}")
    
    print("\n==== Arturo Calle ====")
    arturo_products = []
    try:
        arturo_products = scrape_arturo_calle()
        print(f"Arturo Calle devolvió {len(arturo_products)} productos")
        if arturo_products:
            print("Ejemplo de producto Arturo Calle:")
            print(arturo_products[0])
    except Exception as e:
        print(f"❌ Error en scrape_arturo_calle: {e}")
    
    print("\n==== Americanino ====")
    americanino_products = []
    try:
        americanino_products = scrape_americanino()
        print(f"Americanino devolvió {len(americanino_products)} productos")
        if americanino_products:
            print("Ejemplo de producto Americanino:")
            print(americanino_products[0])
    except Exception as e:
        print(f"❌ Error en scrape_americanino: {e}")
    
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
        'ae': ae_products,
        'mercedes': mercedes_products,
        'arturo': arturo_products,
        'americanino': americanino_products
    }