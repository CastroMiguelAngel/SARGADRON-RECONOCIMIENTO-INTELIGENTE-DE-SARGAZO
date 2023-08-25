"""import os
import cv2
import numpy as np
from tensorflow.keras.models import load_model

carpetaImagenes = '..\..\Imagenes\Deteccion'
inputShape = (224, 224, 3)
model = load_model('modelo_sargazo.keras')

def predecirImagenesEnCarpeta(carpeta):
    listaImagenes = [imagen for imagen in os.listdir(carpeta) if imagen.endswith('.jpg')]
    
    for imagen in listaImagenes:
        rutaImagen = os.path.join(carpeta, imagen)
        img = cv2.imread(rutaImagen)
        img = cv2.resize(img, (inputShape[0], inputShape[1]))
        img = np.expand_dims(img, axis=0)
        img = img.astype('float32') / 255.0
        prediccion = model.predict(img)
        
        if prediccion[0][0] >= 0.5:
            print(f"La imagen {imagen} contiene sargazo.")
        else:
            print(f"La imagen {imagen} no contiene sargazo.")

predecirImagenesEnCarpeta(carpetaImagenes)
"""


import os
import cv2
import numpy as np
from tensorflow.keras.models import load_model
import mysql.connector
import socket

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('10.147.17.1', 12345))
    server_socket.listen(1)
    
    print("Esperando conexión del cliente...")
    client_socket, client_address = server_socket.accept()
    print("Cliente conectado desde:", client_address)
    
    data = client_socket.recv(1024)
    if data.decode() == "ProcesamientoCompletado":
        print("Señal de procesamiento completado recibida.")


    # Configuración de la base de datos
    db_config = {
        'host': '127.0.0.1',
        'user': 'root',
        'port': '3307',
        'password': 's@rg@drone',
        'database': 'sargadrone'
    }

    carpetaImagenes = '..\..\Imagenes\Deteccion'
    inputShape = (224, 224, 3)
    model = load_model('modelo_sargazo.keras')

    def predecirImagenesEnCarpeta(carpeta):
        listaImagenes = [imagen for imagen in os.listdir(carpeta) if imagen.endswith('.jpg')]

        # Establecer la conexión con la base de datos
        conexion = mysql.connector.connect(**db_config)
        cursor = conexion.cursor()

        for imagen in listaImagenes:
            rutaImagen = os.path.join(carpeta, imagen)
            img = cv2.imread(rutaImagen)
            img = cv2.resize(img, (inputShape[0], inputShape[1]))
            img = np.expand_dims(img, axis=0)
            img = img.astype('float32') / 255.0
            prediccion = model.predict(img)
            
            sargazo_valor = int(prediccion[0][0] >= 0.5)  # Convertir a 0 o 1

            # Actualizar la columna 'sargazo' en la base de datos
            try:
                update_query = "UPDATE imagenes SET sargazo = %s WHERE nombre = %s"
                update_values = (sargazo_valor, imagen)
                cursor.execute(update_query, update_values)
                conexion.commit()
                print(f"Actualización exitosa para {imagen}")
            except mysql.connector.Error as error:
                print(f"Error al actualizar {imagen}:", error)
                conexion.rollback()

        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()

    predecirImagenesEnCarpeta(carpetaImagenes)

    client_socket.close()
    server_socket.close()

if __name__ == '__main__':
    main()

