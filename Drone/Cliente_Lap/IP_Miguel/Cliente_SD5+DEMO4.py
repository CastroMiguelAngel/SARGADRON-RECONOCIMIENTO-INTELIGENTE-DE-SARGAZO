import os
import cv2
import time
import mysql.connector
from djitellopy import Tello
import socket
import shutil


# Conexión a la base de datos MySQL
db = mysql.connector.connect(
    host="GQSERVER",
    user="root",
    port="3307",
    password="s@rg@drone",
    database="sargadrone"
)
cursor = db.cursor()

#variables para formar la ruta donde se guadaran las fotos
dia = time.strftime('%d')
mes = time.strftime('%m')
anio = time.strftime('%Y')

# Ruta donde se guardaran las fotos
ruta_guardado = os.path.join("//GQSERVER/Sargadrone/Imagenes/Deteccion", anio, mes, dia)
fotos = 2

# playa id de la bd
playa_id = 8  

def funcion_dron(ruta_guarda, num_fotos):
    #numero de fotos que se desean tomar con el dron

    print("ruta de guardado: "+ruta_guarda)
    os.makedirs(ruta_guarda, exist_ok=True)

    # Conecta con el dron
    tello = Tello('192.168.1.71') 
    tello.connect()

    # Activa la transmisión de video
    tello.streamon()
    frame_read = tello.get_frame_read()

    # Inicia el despegue
    tello.takeoff()

    # Alturas a las que tomarás las fotos (en centimetros)
    alturaIni=50
    alturas=[]
    for i in range(fotos):
        alturaIni+=50
        alturas.append(alturaIni)  # en centímetros
    print(alturas)

    # Se toman las fotos dependiendo del arreglo "alturas"
    for idx, altura in enumerate(alturas):
        # Cambia la altura del dron ala siguiente segun el arreglo "alturas"
        tello.move_up(altura - tello.get_height())

        # Espera a que el dron alcance la altura deseada
        while abs(tello.get_height() - altura) > 10:
            time.sleep(0.1)  # Espera en incrementos pequeños para no bloquear el bucle

        # Captura la imagen y guárdala con un nombre único
        frame = tello.get_frame_read().frame
        nombre_foto = f"foto_{altura}.jpg"
        ruta_foto = os.path.join(ruta_guarda, nombre_foto)
        cv2.imwrite(ruta_foto, frame)

        # Insertar datos en la tabla 'imagenes'
        fecha_actual = time.strftime('%Y-%m-%d %H:%M:%S')
        playa_id = 1  # Cambia esto según la playa correspondiente en tu base de datos

        insert_query = "INSERT INTO imagenes (id_playa, nombre, fecha) VALUES (%s, %s, %s)"
        insert_data = (playa_id, nombre_foto, fecha_actual)

        cursor.execute(insert_query, insert_data)
        

    # Aterriza el dron
    tello.land()

    # Detén la transmisión de video
    tello.streamoff()
    
    db.commit()
    # Cerrar la conexión a la base de datos
    db.close()




def funcion_demo(ruta_guarda):
    print(ruta_guarda)
    os.makedirs(ruta_guarda, exist_ok=True)
    
    # Ruta del directorio de origen
    carpeta_origen = "//GQSERVER/Sargadrone/Imagenes/Pruebas"

    # Lista de archivos en el directorio
    archivos = os.listdir(carpeta_origen)

    for nombre_foto in archivos:
        print(f"Procesando {nombre_foto}...")
        ruta_foto = os.path.join(carpeta_origen, nombre_foto)
        
        # Verifica si la imagen existe en el directorio
        if os.path.isfile(ruta_foto):
            # Lee la imagen
            frame = cv2.imread(ruta_foto)
            
            # Insertar datos en la tabla 'imagenes'
            fecha_actual = time.strftime('%Y-%m-%d %H:%M:%S')
            
            insert_query = "INSERT INTO imagenes (id_playa, nombre, fecha) VALUES (%s, %s, %s)"
            insert_data = (playa_id, nombre_foto, fecha_actual)
            
            cursor.execute(insert_query, insert_data)
            db.commit()

            print(f"Imagen {nombre_foto}: Procesada y registrada en la base de datos.")

            # Copiar el archivo a la carpeta de destino
            ruta_destino = os.path.join(ruta_guarda, nombre_foto)
            shutil.copy(ruta_foto, ruta_destino)
            print(f"Imagen {nombre_foto}: Copiada a {ruta_guarda}")

        else:
            print(f"Imagen {nombre_foto}: No se encontró en el directorio.")

    db.commit()
    # Cerrar la conexión a la base de datos
    db.close()



def main():
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('10.147.17.1', 12345))
    
    # variable opcion sera la que se usara para los botones
    opcion = input("Ingrese 1 para ingresar a la funcion dron o 2 para la funcion demo: ")
    
    if opcion == "1":
        funcion_dron(ruta_guardado ,fotos)
    elif opcion == "2":
        funcion_demo(ruta_guardado)

    

    client_socket.send("ProcesamientoCompletado".encode())
    print("Señal de procesamiento completado enviada.")

    client_socket.close()


if __name__ == '__main__':
    main()