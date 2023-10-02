import os
import cv2
import time
import mysql.connector
import socket

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('10.147.17.1', 12345))

    # Ruta donde deseas guardar las fotos
    dia = time.strftime('%d')
    mes = time.strftime('%m')
    anio = time.strftime('%Y')

    ruta_guardado = os.path.join("//GQSERVER/Sargadrone/Imagenes/Deteccion", anio, mes, dia)
    print(ruta_guardado)
    os.makedirs(ruta_guardado, exist_ok=True)

    # Conexión a la base de datos MySQL
    db = mysql.connector.connect(
        host="GQSERVER",
        user="root",
        port="3307",
        password="s@rg@drone",
        database="sargadrone"
    )
    cursor = db.cursor()

    # Procesa las imágenes desde el directorio
    for idx in range(5):  # Cambia 5 por el número deseado de imágenes
        # Suponemos que las imágenes se encuentran en la carpeta "imagenes_directorio" con nombres como "foto_1.jpg", "foto_2.jpg", ...
        nombre_foto = f"foto_{idx + 1}.jpg"
        ruta_foto = os.path.join("//GQSERVER/Sargadrone/Imagenes/Pruebas", nombre_foto)

        # Verifica si la imagen existe en el directorio
        if os.path.isfile(ruta_foto):
            # Lee la imagen
            frame = cv2.imread(ruta_foto)

            # Insertar datos en la tabla 'imagenes'
            fecha_actual = time.strftime('%Y-%m-%d %H:%M:%S')
            playa_id = 8  # Cambia esto según la playa correspondiente en tu base de datos

            insert_query = "INSERT INTO imagenes (id_playa, nombre, fecha) VALUES (%s, %s, %s)"
            insert_data = (playa_id, nombre_foto, fecha_actual)

            cursor.execute(insert_query, insert_data)
            db.commit()

            print(f"Imagen {idx + 1}: Procesada y registrada en la base de datos.")

        else:
            print(f"Imagen {idx + 1}: No se encontró en el directorio.")

    # Cerrar la conexión a la base de datos
    db.close()

    client_socket.send("ProcesamientoCompletado".encode())
    print("Señal de procesamiento completado enviada.")

    client_socket.close()

if __name__ == '__main__':
    main()