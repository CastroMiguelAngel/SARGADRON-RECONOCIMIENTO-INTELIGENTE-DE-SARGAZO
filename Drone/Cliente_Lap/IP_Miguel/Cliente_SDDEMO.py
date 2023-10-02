import os
import cv2
import time
import mysql.connector
import socket

def main():
    # Ruta donde deseas guardar las fotos
    dia = time.strftime('%d')
    mes = time.strftime('%m')
    anio = time.strftime('%Y')

    ruta_guardado = os.path.join("//GQSERVER/Sargadrone/Imagenes/Deteccion", anio, mes, dia)
    print(ruta_guardado)
    os.makedirs(ruta_guardado, exist_ok=True)

    # Ruta donde se encuentran las imágenes de comparación
    directorio_comparacion = "//GQSERVER/Sargadrone/Imagenes/Pruebas"
    imagenes_comparacion = []

    for filename in os.listdir(directorio_comparacion):
        if filename.endswith('.jpg'):
            img = cv2.imread(os.path.join(directorio_comparacion, filename))
            imagenes_comparacion.append(img)

    # Cargar todas las imágenes capturadas desde el directorio de comparación
    imagenes_capturadas = []
    for filename in os.listdir(ruta_guardado):
        if filename.endswith('.jpg'):
            img_capturada = cv2.imread(os.path.join(ruta_guardado, filename))
            imagenes_capturadas.append(img_capturada)

    # Comparar cada imagen capturada con las imágenes de comparación
    for idx, img_comp in enumerate(imagenes_comparacion):
        for i, img_capturada in enumerate(imagenes_capturadas):
            diferencia = cv2.absdiff(img_comp, img_capturada)
            porcentaje_diferencia = (diferencia.sum() / img_capturada.size) * 100

            if porcentaje_diferencia < 5.0:
                print(f"La imagen {idx + 1} coincide con la imagen {i + 1} del directorio de comparación.")

if __name__ == '__main__':
    main()