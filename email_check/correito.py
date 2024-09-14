import os
import re
import smtplib
import dns.resolver
import readline
import sys  # Para salir del programa
from colorama import init, Fore, Style
import pyfiglet

# Inicializar colorama
init(autoreset=True)

# Función para cargar la lista de correos temporales desde el archivo
def cargar_correos_temporales(archivo):
    try:
        with open(archivo, 'r') as f:
            # Leer líneas y quitar espacios en blanco alrededor
            correos_temporales = [linea.strip() for linea in f.readlines() if linea.strip()]
        return correos_temporales
    except FileNotFoundError:
        print(Fore.RED + f"\nError: El archivo '{archivo}' no se encontró.\n")
        sys.exit(1)  # Salir del programa con un código de error
    except Exception as e:
        print(Fore.RED + f"\nError al leer el archivo '{archivo}': {e}\n")
        sys.exit(1)  # Salir del programa con un código de error

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
def es_correo_temporal(dominio, correos_temporales):
    return dominio in correos_temporales

# Función para obtener los registros MX del dominio
def obtener_registros_mx(dominio):
    try:
        registros_mx = dns.resolver.resolve(dominio, 'MX')
        return registros_mx
    except Exception as e:
        print(Fore.RED + f"\nError al obtener registros MX para {dominio}: {e}")
        return None

# Función para verificar si el correo existe usando SMTP
def verificar_correo(correo):
    dominio = correo.split('@')[1]
    registros_mx = obtener_registros_mx(dominio)
    
    if registros_mx:
        servidor_mx = str(registros_mx[0].exchange)  # Tomamos el servidor MX con la mayor prioridad

        print(Fore.BLUE + f"\nConectando con el servidor MX: {servidor_mx}\n")

        try:
            servidor = smtplib.SMTP(servidor_mx)
            servidor.set_debuglevel(0)

            servidor.helo("kali.local")  # El comando EHLO o HELO identifica nuestro cliente
            servidor.mail('test@kali.local')  # Indicamos un correo falso como remitente
            codigo, mensaje = servidor.rcpt(correo)  # Comprobamos si acepta el correo destinatario

            servidor.quit()

            if codigo == 250:
                return True  # El correo existe
            elif codigo == 550:
                return False  # El correo no existe
            else:
                print(Fore.RED + f"Respuesta desconocida del servidor: {codigo} {mensaje}\n")
                return False
        except Exception as e:
            print(Fore.RED + f"\nError al conectar con el servidor SMTP: {e}\n")
            return None
    else:
        # Si no se pueden obtener registros MX, se asume que el correo no existe
        return False

# Función para procesar un solo correo
def procesar_correo(correo, correos_temporales):
    # Validar el formato del correo
    if not validar_correo(correo):
        print(Fore.RED + f"\nEl formato del correo '{correo}' no es válido.\n")
        return
    
    # Comprobar si es correo temporal
    dominio = correo.split('@')[1]
    if es_correo_temporal(dominio, correos_temporales):
        print(Fore.YELLOW + f"\nEl correo '{correo}' pertenece a un dominio de correo temporal.\n")
        return

    # Verificar si el correo existe
    resultado = verificar_correo(correo)
    if resultado is True:
        print(Fore.GREEN + f"\nEl correo '{correo}' existe.\n")
    elif resultado is False:
        print(Fore.RED + f"\nEl correo '{correo}' no existe.\n")
    else:
        print(Fore.RED + f"\nNo se pudo verificar la existencia del correo '{correo}'.\n")

# Función para procesar un archivo de correos (sin guardar)
def procesar_archivo(ruta_archivo, correos_temporales):
    try:
        with open(ruta_archivo, 'r') as archivo:
            correos = archivo.readlines()
            for correo in correos:
                correo = correo.strip()
                procesar_correo(correo, correos_temporales)
    except FileNotFoundError:
        print(Fore.RED + f"\nEl archivo {ruta_archivo} no se encontró.\n")
    except Exception as e:
        print(Fore.RED + f"\nError al procesar el archivo: {e}\n")

# Función para procesar un archivo de correos y guardar resultados
def procesar_archivo_con_guardado(ruta_archivo, ruta_guardado, correos_temporales):
    try:
        with open(ruta_archivo, 'r') as archivo, open(ruta_guardado, 'w') as archivo_salida:
            correos = archivo.readlines()
            for correo in correos:
                correo = correo.strip()
                resultado = verificar_correo(correo)
                if resultado is True:
                    archivo_salida.write(f"El correo '{correo}' existe.\n")
                elif resultado is False:
                    archivo_salida.write(f"El correo '{correo}' no existe.\n")
                else:
                    archivo_salida.write(f"No se pudo verificar la existencia del correo '{correo}'.\n")
            print(Fore.GREEN + f"\nResultados guardados en {ruta_guardado}\n")
    except FileNotFoundError:
        print(Fore.RED + f"\nEl archivo {ruta_archivo} no se encontró.\n")
    except Exception as e:
        print(Fore.RED + f"\nError al procesar el archivo: {e}\n")

# Función para mostrar las opciones del menú
def mostrar_menu():
    print(Fore.MAGENTA + "Selecciona una opción:")
    print(Fore.CYAN + "  0: Introducir un correo manualmente")
    print(Fore.CYAN + "  1: Cargar un archivo .txt con una lista de correos")
    print(Fore.CYAN + "  2: Cargar un archivo .txt con una lista de correos y guardar resultados")
    print(Fore.RED + "  3: Salir del programa\n")

# Función para pausar y esperar a que el usuario presione Enter
def esperar_para_continuar():
    input(Fore.YELLOW + "\nPresione [Enter] para continuar...")
    os.system('clear')

# Función principal
def main():
    os.system('clear')  # Limpia la pantalla al inicio

    # Pixel art inicial
    arte = pyfiglet.figlet_format("CORREITOS", font="slant")
    print(Fore.CYAN + arte)

    # Cargar la lista de correos temporales desde el archivo
    correos_temporales = cargar_correos_temporales('disposable_email_blocklist.txt')

    if not correos_temporales:
        sys.exit(1)  # Si la lista está vacía, salir del programa

    try:
        while True:
            mostrar_menu()
            
            opcion = input(Fore.YELLOW + "Ingresa 0, 1, 2 o 3: ")

            if opcion == "0":
                correo = input(Fore.YELLOW + "\nIntroduce el correo electrónico: ")
                procesar_correo(correo, correos_temporales)
                esperar_para_continuar()
            elif opcion == "1":
                ruta_archivo = input(Fore.YELLOW + "\nIntroduce la ruta del archivo .txt: ")
                procesar_archivo(ruta_archivo, correos_temporales)
                esperar_para_continuar()
            elif opcion == "2":
                ruta_archivo = input(Fore.YELLOW + "\nIntroduce la ruta del archivo .txt: ")
                ruta_guardado = input(Fore.YELLOW + "\nIntroduce la ruta para guardar los resultados: ")
                procesar_archivo_con_guardado(ruta_archivo, ruta_guardado, correos_temporales)
                esperar_para_continuar()
            elif opcion == "3":
                print(Fore.GREEN + "\nSaliendo del programa... ¡Adiós!\n")
                break
            else:
                print(Fore.RED + "\nOpción no válida. Intenta de nuevo.\n")
                esperar_para_continuar()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\nInterrupción detectada. Saliendo del programa...\n")

if __name__ == "__main__":
    main()
