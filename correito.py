import os
import re
import smtplib
import dns.resolver
import readline
from colorama import init, Fore, Style

# Inicializar colorama
init(autoreset=True)

# Lista ampliada de dominios de correos temporales conocidos
correos_temporales = [
    "10minutemail.com", "guerrillamail.com", "mailinator.com", "tempmail.com", "trashmail.com",
    "yopmail.com", "dispostable.com", "getnada.com", "temp-mail.org", "mohmal.com",
    "maildrop.cc", "fakeinbox.com", "mytemp.email", "throwawaymail.com", "sharklasers.com",
    "guerillamail.net", "mailcatch.com", "emailondeck.com", "spambog.com", "getairmail.com",
    "inboxkitten.com", "mintemail.com", "putmail.net", "wegwerfmail.de", "meltmail.com"
]

# Función para autocompletado de archivos
def completar(texto, estado):
    opciones = [archivo for archivo in os.listdir('.') if archivo.startswith(texto)]
    try:
        return opciones[estado]
    except IndexError:
        return None

# Configurar el autocompletado de readline
readline.set_completer(completar)
readline.parse_and_bind("tab: complete")

# Función para validar el formato del correo
def validar_correo(correo):
    patron = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(patron, correo) is not None

# Función para comprobar si el dominio es de correo temporal
def es_correo_temporal(dominio):
    return dominio in correos_temporales

# Función para obtener los registros MX del dominio
def obtener_registros_mx(dominio):
    try:
        registros_mx = dns.resolver.resolve(dominio, 'MX')
        return registros_mx
    except Exception as e:
        print(f"Error al obtener registros MX para {dominio}: {e}")
        return None

# Función para verificar si el correo existe usando SMTP
def verificar_correo(correo):
    dominio = correo.split('@')[1]
    registros_mx = obtener_registros_mx(dominio)
    
    if registros_mx:
        servidor_mx = str(registros_mx[0].exchange)  # Tomamos el servidor MX con la mayor prioridad
        print(Fore.BLUE + f"Conectando con el servidor MX: {servidor_mx}")

        # Conectarse al servidor de correo usando el puerto 25 (SMTP)
        try:
            servidor = smtplib.SMTP(servidor_mx)
            servidor.set_debuglevel(0)  # Ajustar a 1 para depuración

            # Comprobar si el servidor está respondiendo correctamente
            servidor.helo("kali.local")  # El comando EHLO o HELO identifica nuestro cliente
            servidor.mail('test@kali.local')  # Indicamos un correo falso como remitente
            codigo, mensaje = servidor.rcpt(correo)  # Comprobamos si acepta el correo destinatario

            servidor.quit()

            # Verificar la respuesta del servidor
            if codigo == 250:
                return True  # El correo existe
            elif codigo == 550:
                return False  # El correo no existe
            else:
                print(f"Respuesta desconocida del servidor: {codigo} {mensaje}")
                return False
        except Exception as e:
            print(f"Error al conectar con el servidor SMTP: {e}")
            return None
    else:
        return None

# Función para procesar un solo correo
def procesar_correo(correo):
    # Validar el formato del correo
    if not validar_correo(correo):
        print(f"El formato del correo '{correo}' no es válido.")
        return
    
    # Comprobar si es correo temporal
    dominio = correo.split('@')[1]
    if es_correo_temporal(dominio):
        print(Fore.YELLOW + f"El correo '{correo}' pertenece a un dominio de correo temporal.")
        return

    # Verificar si el correo existe
    resultado = verificar_correo(correo)
    if resultado is True:
        print(Fore.GREEN + f"El correo '{correo}' existe.")
    elif resultado is False:
        print(Fore.RED + f"El correo '{correo}' no existe.")
    else:
        print(f"No se pudo verificar la existencia del correo '{correo}'.")

# Función para procesar un archivo de correos
def procesar_archivo(ruta_archivo):
    try:
        with open(ruta_archivo, 'r') as archivo:
            correos = archivo.readlines()
            for correo in correos:
                correo = correo.strip()  # Eliminar espacios en blanco o saltos de línea
                procesar_correo(correo)
    except FileNotFoundError:
        print(f"El archivo {ruta_archivo} no se encontró.")
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")

# Función principal
def main():
    print("Selecciona una opción:")
    print("0: Introducir un correo manualmente")
    print("1: Cargar un archivo .txt con una lista de correos")
    
    opcion = input("Ingresa 0 o 1: ")

    if opcion == "0":
        correo = input("Introduce el correo electrónico: ")
        procesar_correo(correo)
    elif opcion == "1":
        ruta_archivo = input("Introduce la ruta del archivo .txt: ")
        procesar_archivo(ruta_archivo)
    else:
        print("Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    main()
