from google_images_search import GoogleImagesSearch

def descargar_imagen(palabra_clave, nombre_archivo, ruta_busqueda_fotos):
    # Reemplaza "TU_CLAVE_DE_API" y "TU_ID_DE_BUSQUEDA_PERSONALIZADO" con tus propios valores
    api_key = "670632543653-7e20nr8ip0a6p8hos05maktgv18g54j1.apps.googleusercontent.com"
    cx_id = "descarga-de-imagenes"
    gis = GoogleImagesSearch(api_key, cx_id)

    _search_params = {
        'q': palabra_clave,
        'num': 100,
        'fileType': 'png',
    }

    gis.search(search_params=_search_params, path_to_dir=ruta_busqueda_fotos, custom_image_name=nombre_archivo)

if __name__ == "__main__":
    palabra_clave = input("Ingresa la palabra clave de búsqueda: ")
    nombre_archivo = input("Ingresa el nombre del archivo descargado: ")
    ruta_busqueda_fotos = "busquedaFotos"
    descargar_imagen(palabra_clave, nombre_archivo, ruta_busqueda_fotos)
