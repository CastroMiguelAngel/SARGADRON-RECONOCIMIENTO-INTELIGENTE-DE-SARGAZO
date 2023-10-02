import os
import cv2
import time
import mysql.connector
from djitellopy import Tello
import socket

def main(cantidad_fotos):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('10.147.17.1', 12345))

    # Ruta donde deseas guardar las fotos
    dia = time.strftime('%d')
    mes = time.strftime('%m')
    anio = time.strftime('%Y')

    ruta_guardado = os.path.join("//GQSERVER/Sargadrone/Imagenes/Deteccion", anio, mes, dia)
    print(ruta_guardado)
    os.makedirs(ruta_guardado, exist_ok=True)

    # Conecta con el dron
    tello = Tello('192.168.1.71') 
    tello.connect()

    # Activa la transmisión de video
    tello.streamon()
    frame_read = tello.get_frame_read()

    # Inicia el despegue
    tello.takeoff()

    # Altura inicial
    altura_actual = 50  # Altura inicial en centímetros

    # Conexión a la base de datos MySQL
    db = mysql.connector.connect(
        host="GQSERVER",
        user="root",
        port="3307",
        password="s@rg@drone",
        database="sargadrone"
    )
    cursor = db.cursor()

    # Toma la cantidad especificada de fotos
    for idx in range(cantidad_fotos):
        # Cambia la altura del dron
        tello.move_up(altura_actual - tello.get_height())

        # Espera a que el dron alcance la altura deseada
        while abs(tello.get_height() - altura_actual) > 10:
            time.sleep(0.1)  # Espera en incrementos pequeños para no bloquear el bucle

        # Captura la imagen y guárdala con un nombre único
        frame = tello.get_frame_read().frame
        nombre_foto = f"foto_{idx + 1}.jpg"  # Usa un índice en lugar de la altura para el nombre
        ruta_foto = os.path.join(ruta_guardado, nombre_foto)
        cv2.imwrite(ruta_foto, frame)

        # Insertar datos en la tabla 'imagenes'
        fecha_actual = time.strftime('%Y-%m-%d %H:%M:%S')
        playa_id = 7  # Cambia esto según la playa correspondiente en tu base de datos

        insert_query = "INSERT INTO imagenes (id_playa, nombre, fecha) VALUES (%s, %s, %s)"
        insert_data = (playa_id, nombre_foto, fecha_actual)

        cursor.execute(insert_query, insert_data)
        db.commit()

        # Incrementa la altura actual en 50 centímetros
        altura_actual += 50

    # Aterriza el dron
    tello.land()

    # Detén la transmisión de video
    tello.streamoff()

    # Cerrar la conexión a la base de datos
    db.close()

    client_socket.send("ProcesamientoCompletado".encode())
    print("Señal de procesamiento completado enviada.")

    client_socket.close()

if __name__ == '__main__':
    cantidad_fotos = int(input("Ingrese la cantidad de fotos que desea tomar: "))
    main(cantidad_fotos)