import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin

def descargar_assets(url, carpeta_destino):
    # Create an instance of BeautifulSoup to parse the page content
    soup = obtener_soup(url)

    # Print URL currently page
    print(f"Downloading from: {url}")

    # Obtener el nombre de la página sin extensiones ni caracteres especiales
    nombre_pagina = obtener_nombre_pagina(url)

    # Create the folder structure to store the assets
    carpeta_pagina = os.path.join(carpeta_destino, nombre_pagina)
    carpeta_imagenes = os.path.join(carpeta_pagina, "Imagenes")
    carpeta_videos = os.path.join(carpeta_pagina, "Videos")
    carpeta_js = os.path.join(carpeta_pagina, "JS")

    # Create the folders if they don't exist
    os.makedirs(carpeta_imagenes, exist_ok=True)
    os.makedirs(carpeta_videos, exist_ok=True)
    os.makedirs(carpeta_js, exist_ok=True)

    # Download and save the assets of images, videos and JavaScript files
    descargar_assets_pagina(url, soup, carpeta_imagenes, carpeta_videos, carpeta_js)

    # Find related links on home page
    enlaces_relacionados = obtener_enlaces_relacionados(url, soup)
    for enlace in enlaces_relacionados:
        # Check if the link has already been visited
        if enlace not in visitados:
            # Download and save the assets of each related link
            soup_enlace = obtener_soup(enlace)
            if soup_enlace:
                # Print the URL of the related link
                print(f"Después de: {enlace}")
                descargar_assets_pagina(enlace, soup_enlace, carpeta_imagenes, carpeta_videos, carpeta_js)
                # Add the link to the visited list
                visitados.add(enlace)

    print("Asset download completed.")

def obtener_soup(url):
    # Make the HTTP request to get the content of the page
    response = requests.get(url)
    if response.status_code == 200:
        # Create an instance of BeautifulSoup to parse the page content
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    else:
        print(f"Error al descargar la página: {response.status_code}")
        return None

def descargar_assets_pagina(url, soup, carpeta_imagenes, carpeta_videos, carpeta_js):
    # Download and save the assets of images, videos and JavaScript files
    for tag in soup.find_all(["img", {"source": "video/mp4"}, "script"]):
        if "src" not in tag.attrs:
            continue

        asset_url = urljoin(url, tag["src"])
        if not is_valid_url(asset_url):
            continue

        extension = os.path.splitext(asset_url)[1]
        if extension in [".jpg", ".jpeg", ".png"]:
            asset_type = "Imagen"
            carpeta_destino = carpeta_imagenes
        elif extension == ".mp4":
            asset_type = "Video"
            carpeta_destino = carpeta_videos
        elif extension == ".js":
            asset_type = "Archivo JavaScript"
            carpeta_destino = carpeta_js
        else:
            continue

        asset_name = asset_url.split("/")[-1]
        asset_name = clean_filename(asset_name)  # Limpiar el nombre del archivo

        asset_path = os.path.join(carpeta_destino, asset_name)

        # Download the asset
        asset_response = requests.get(asset_url)
        with open(asset_path, "wb") as f:
            f.write(asset_response.content)

        print(f"{asset_type} descargado: {asset_name}")

def obtener_enlaces_relacionados(url, soup):
    enlaces_relacionados = set()
    dominio_base = obtener_dominio_base(url)

    for a in soup.find_all('a'):
        if 'href' in a.attrs:
            href = a['href']
            if not href.startswith('#') and not href.startswith('http') and not href.startswith('mailto'):
                enlace_completo = urljoin(dominio_base, href)
                enlaces_relacionados.add(enlace_completo)

    return enlaces_relacionados

def descargar_asset(url, carpeta_destino):
    nombre_archivo = url.split("/")[-1]  # Obtener el nombre del archivo desde la URL
    ruta_guardado = os.path.join(carpeta_destino, nombre_archivo)

    # Download the file
    response = requests.get(url)
    if response.status_code == 200:
        with open(ruta_guardado, "wb") as archivo:
            archivo.write(response.content)
        print(f"Archivo descargado correctamente: {ruta_guardado}")
    else:
        print(f"Error al descargar el archivo: {response.status_code}")

def obtener_nombre_pagina(url):
    # Remove disallowed characters for folder names
    caracteres_no_permitidos = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    nombre_pagina = url

    for caracter in caracteres_no_permitidos:
        nombre_pagina = nombre_pagina.replace(caracter, '')

    return nombre_pagina

def obtener_dominio_base(url):
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    dominio_base = parsed_url.scheme + "://" + parsed_url.netloc
    return dominio_base

def is_valid_url(url):
    """
    Check if a URL is valid.
    """
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def clean_filename(filename):
    """
    Clears a file name by removing illegal characters.
    """
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename

# Set to store the visited pages
visitados = set()

# Use
url_pagina = input("URL: ")
carpeta_destino = "Assets"

descargar_assets(url_pagina, carpeta_destino)