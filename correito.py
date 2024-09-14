import re
import smtplib
import dns.resolver

# Lista de dominios de correos temporales conocidos
correos_temporales = [
    "10minutemail.com", "guerrillamail.com", "mailinator.com", "tempmail.com", "trashmail.com",
    "yopmail.com", "dispostable.com", "getnada.com"
]

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
        print(f"Conectando con el servidor MX: {servidor_mx}")

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

# Función principal
def main():
    correo = input("Introduce el correo electrónico: ")

    # Validar el formato del correo
    if not validar_correo(correo):
        print("El formato del correo no es válido.")
        return
    
    # Comprobar si es correo temporal
    dominio = correo.split('@')[1]
    if es_correo_temporal(dominio):
        print("El correo pertenece a un dominio de correo temporal.")
        return

    # Verificar si el correo existe
    resultado = verificar_correo(correo)
    if resultado is True:
        print("El correo existe.")
    elif resultado is False:
        print("El correo no existe.")
    else:
        print("No se pudo verificar la existencia del correo.")

if __name__ == "__main__":
    main()
