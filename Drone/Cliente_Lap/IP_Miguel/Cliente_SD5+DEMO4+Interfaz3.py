import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import cv2
import time
import mysql.connector
from djitellopy import Tello
import socket
import shutil
import threading

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
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('10.147.17.1', 12345))

cursor.execute("SELECT id, nombre FROM playas")
resultados = cursor.fetchall()
valores_playa = [row[0] for row in resultados]
id_a_nombre = {row[0]: row[1] for row in resultados}

def funcion_dron(ruta_guarda, fotos):
    
    # Actualizar el mensaje
    mensaje.config(text="Iniciando proceso...", font=("Helvetica", 22))
    mensaje.place(x=680, y=300)
    #numero de fotos que se desean tomar con el dron
    
    print("ruta de guardado: "+ruta_guarda)
    os.makedirs(ruta_guarda, exist_ok=True)

    # Conecta con el dron
    tello = Tello('192.168.1.71') 
    tello.connect()

    # Activa la transmisión de video
    tello.streamon()
    frame_read = tello.get_frame_read()
    
    # Actualizar el mensaje
    mensaje.config(text="El dron esta despegando...", font=("Helvetica", 22))
    mensaje.place(x=680, y=300)
    
    # Inicia el despegue
    tello.takeoff()
    
    # Alturas a las que tomarás las fotos (en centimetros)
    alturaIni=50
    alturas=[]
    for i in range(int(fotos)):
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
        playa_id = int(seleccion_playa.get())  # Cambia esto según la playa correspondiente en tu base de datos

        insert_query = "INSERT INTO imagenes (id_playa, nombre, fecha) VALUES (%s, %s, %s)"
        insert_data = (playa_id, nombre_foto, fecha_actual)

        cursor.execute(insert_query, insert_data)
        
        mensaje.config(text="Tomando foto...", font=("Helvetica", 22))
        mensaje.place(x=680, y=300)

    # Aterriza el dron
    tello.land()

    # Detén la transmisión de video
    tello.streamoff()
    mensaje.config(text="El dron aterrizo...", font=("Helvetica", 22))
    mensaje.place(x=680, y=300)
    
    db.commit()
    # Cerrar la conexión a la base de datos
    db.close()
    mensaje.config(text="Imagenes enviadas al servidor...", font=("Helvetica", 22))
    mensaje.place(x=680, y=300)
    client_socket.send("ProcesamientoCompletado".encode())
    client_socket.close()



def funcion_demo(ruta_guarda):
    
    print(ruta_guarda)
    ruta_corregida = ruta_guarda.replace("\\", "/")
    os.makedirs(ruta_corregida, exist_ok=True)
    
    # Ruta del directorio de origen
    carpeta_origen = "//GQSERVER/Sargadrone/Imagenes/Pruebas"

    # Lista de archivos en el directorio
    archivos = os.listdir(carpeta_origen)

    for nombre_foto in archivos:
        if nombre_foto != "Thumbs.db":
            print(f"Procesando {nombre_foto}...")
            
            # Actualizar el mensaje
            mensaje.config(text=f"Procesando {nombre_foto}...", font=("Helvetica", 22))
            mensaje.place(x=680, y=300)
            playa_id = seleccion.get()
            ruta_foto = os.path.join(carpeta_origen, nombre_foto)
        # Verifica si la imagen existe en el directorio
        if os.path.isfile(ruta_foto):
            if nombre_foto != "Thumbs.db":
                # Lee la imagen
                frame = cv2.imread(ruta_foto)
            
                # Insertar datos en la tabla 'imagenes'
                fecha_actual = time.strftime('%Y-%m-%d %H:%M:%S')
            
                insert_query = "INSERT INTO imagenes (id_playa, nombre, fecha) VALUES (%s, %s, %s)"
                insert_data = (playa_id, nombre_foto, fecha_actual)
            
                cursor.execute(insert_query, insert_data)
                db.commit()

                print(f"Imagen {nombre_foto}: Procesada y registrada en la base de datos.")
                mensaje.config(text=f"Imagen {nombre_foto}: Procesada y registrada en la base de datos.", font=("Helvetica", 22))
                mensaje.place(x=680, y=300)
            
                # Copiar el archivo a la carpeta de destino
                ruta_destino = os.path.join(ruta_guarda, nombre_foto)
                shutil.copy(ruta_foto, ruta_destino)
                print(f"Imagen {nombre_foto}: Copiada a {ruta_guarda}")
                mensaje.config(text=f"Imagen {nombre_foto}: Copiada a {ruta_guarda}.", font=("Helvetica", 22))
                mensaje.place(x=680, y=300)

        else:
            mensaje.config(text=f"Imagen {nombre_foto}: No se encontró en el directorio.", font=("Helvetica", 22))
            mensaje.place(x=680, y=300)
            print(f"Imagen {nombre_foto}: No se encontró en el directorio.")

    db.commit()
    # Cerrar la conexión a la base de datos
    db.close()
    client_socket.send("ProcesamientoCompletado".encode())
    client_socket.close()
    mensaje.config(text="Imagenes enviadas al servidor con exito.", font=("Helvetica", 22))
    mensaje.place(x=680, y=300)


def iniciar_oficial():
    
    # Ocultar los widgets principales
    titulo.place_forget()
    etiqueta_select.place_forget()
    etiqueta_playa.place_forget()
    select.place_forget()
    select_playa.place_forget()
    boton_comenzar.place_forget()
    boton_comenzar_prueba.place_forget()
    
    fotos = seleccion.get()
    
    t = threading.Thread(target=lambda: funcion_dron(ruta_guardado, fotos))
    t.start()  

   
     
def iniciar_prueba():
    
    
    # Ocultar los widgets principales
    titulo.place_forget()
    etiqueta_select.place_forget()
    etiqueta_playa.place_forget()
    select.place_forget()
    select_playa.place_forget()
    boton_comenzar.place_forget()
    boton_comenzar_prueba.place_forget()
     
    t = threading.Thread(target=lambda:  funcion_demo(ruta_guardado))
    t.start() 
   

    #client_socket.send("ProcesamientoCompletado".encode())
    print("Señal de procesamiento completado enviada.")
    
    mensaje.config(text="Señal de procesamiento completado enviada y socket cerrado con exito", font=("Helvetica", 22))
    mensaje.place(x=680, y=300)


# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Volemos el dron")

# Obtener el ancho y alto de la pantalla o ventana principal
ancho_pantalla = ventana.winfo_screenwidth()
alto_pantalla = ventana.winfo_screenheight()

# Cargar la imagen de fondo y ajustar su tamaño
imagen_fondo = Image.open("C:/Users/migue/Desktop/imagenes/imagen_fondo.png")
imagen_fondo = imagen_fondo.resize((ancho_pantalla, alto_pantalla), Image.ANTIALIAS)
imagen_fondo = ImageTk.PhotoImage(imagen_fondo) 

# Crear un cuadro centrado con la imagen de fondo
cuadro = ttk.Frame(ventana)
cuadro.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
fondo_label = tk.Label(cuadro, image=imagen_fondo)
fondo_label.place(relwidth=1, relheight=1)

# Etiqueta con el título
titulo = ttk.Label(cuadro, text="Volemos el dron", font=("Helvetica", 36))
titulo.place(x=750, y=200)  # Ajusta de coordenadas 

etiqueta_select = ttk.Label(cuadro, text="¿Cuántas imágenes vamos a tomar?", font=("Helvetica", 22))
etiqueta_select.place(x=680, y=300)  # Ajusta de coordenadas

# Crear un select con valores
valores = [1, 2, 3, 4, 5]
seleccion = tk.StringVar()

# Select de numero de fotos
select = ttk.Combobox(cuadro, textvariable=seleccion, values=valores, state="readonly")
select.place(x=840, y=380)  # Ajusta de coordenadas 

# Establecer un valor predeterminado para el select
select.set(valores[0])

# Estilo del select
select.configure(font=("Helvetica", 12), width=20, background="white")

#Etiqueta de input playa
etiqueta_playa = ttk.Label(cuadro, text="¿En que playa estas?", font=("Helvetica", 22))
etiqueta_playa.place(x=800, y=430)

# Crear un select con valores
#valores_playa = [1, 2, 3, 4, 5, 6]
seleccion_playa = tk.StringVar()

# Select de playa
select_playa = ttk.Combobox(cuadro, textvariable=seleccion_playa, values=list(id_a_nombre.values()), state="readonly")
select_playa.place(x=840, y=480)  # Ajusta de coordenadas 

# Establecer un valor predeterminado para el select
seleccion_playa.set(list(id_a_nombre.values())[0])

# Estilo del select
select_playa.configure(font=("Helvetica", 12), width=20, background="white")

# Botón "Comenzar"
boton_comenzar = ttk.Button(cuadro, text="Comenzar oficial", command=iniciar_oficial, width=15, style='My.TButton')
boton_comenzar.place(x=750, y=550)  # Ajusta de coordenadas

# Botón "Comenzar"
boton_comenzar_prueba = ttk.Button(cuadro, text="Comenzar prueba", command=iniciar_prueba, width=15, style='My.TButton')
boton_comenzar_prueba.place(x=950, y=550)  # Ajusta de coordenadas

# Etiqueta para mostrar el mensaje (inicialmente oculta)
mensaje = ttk.Label(cuadro, text="", font=("Helvetica", 22))
mensaje.pack(pady=20)
mensaje.pack_forget()  # Oculta el mensaje al inicio

# Definir un estilo personalizado para el botón
style = ttk.Style()
style.configure('My.TButton', font=('Helvetica', 16), padding=5)

# Configurar el cuadro para expandirse y llenar la ventana
ventana.grid_rowconfigure(0, weight=1)
ventana.columnconfigure(0, weight=1)

# Iniciar el bucle principal de la aplicación
ventana.mainloop()

