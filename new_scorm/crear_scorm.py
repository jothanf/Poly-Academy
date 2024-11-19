import os
import zipfile

def crear_scorm_zip(carpeta_base, nombre_zip):
    """
    Crea un archivo ZIP compatible con SCORM.
    
    :param carpeta_base: Ruta de la carpeta que contiene los archivos SCORM.
    :param nombre_zip: Nombre del archivo ZIP de salida.
    """
    if not os.path.exists(carpeta_base):
        print(f"La carpeta {carpeta_base} no existe.")
        return
    
    # Crear archivo ZIP
    zip_path = f"{nombre_zip}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as scorm_zip:
        for root, _, files in os.walk(carpeta_base):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, carpeta_base)  # Ruta relativa dentro del ZIP
                scorm_zip.write(file_path, arcname)
    
    print(f"Archivo SCORM empaquetado como: {zip_path}")

# Ruta de la carpeta SCORM y nombre del archivo ZIP
ruta_carpeta = r"C:\Users\24\Desktop\plataforma_aprendizaje\code\new_scorm\SCORM_Package"

nombre_archivo_zip = "Clase_SCORM"

crear_scorm_zip(ruta_carpeta, nombre_archivo_zip)
