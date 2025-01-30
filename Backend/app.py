from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from cifrado import (
    cifrar_archivo,
    descifrar_archivo,
    generar_claves_rsa,
    cifrar_clave_aes,
    descifrar_clave_aes,
    guardar_clave,
    cargar_clave
)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Habilitar CORS
UPLOAD_FOLDER = "uploads"
FORO_FILE = "foro.txt"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Resto del código...

# Ruta para cifrar un archivo
@app.route("/cifrar", methods=["POST"])
def cifrar():
    if "file" not in request.files:
        return jsonify({"error": "No se proporcionó ningún archivo"}), 400

    file = request.files["file"]
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Generar clave AES y cifrar el archivo
    clave_aes = os.urandom(32)
    archivo_cifrado = file_path + ".enc"
    cifrar_archivo(file_path, archivo_cifrado, clave_aes)

    # Cifrar la clave AES con RSA
    clave_publica = cargar_clave("public_key.pem", es_privada=False)
    clave_aes_cifrada = cifrar_clave_aes(clave_aes, clave_publica)

    # Guardar la clave AES cifrada
    clave_aes_cifrada_path = archivo_cifrado + ".key"
    with open(clave_aes_cifrada_path, "wb") as f:
        f.write(clave_aes_cifrada)

    return jsonify({
        "archivo_cifrado": archivo_cifrado,
        "clave_aes_cifrada": clave_aes_cifrada_path
    })

# Ruta para descifrar un archivo
@app.route("/descifrar", methods=["POST"])
def descifrar():
    if "file" not in request.files or "key" not in request.files:
        return jsonify({"error": "Faltan archivos"}), 400

    file = request.files["file"]
    key = request.files["key"]

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    key_path = os.path.join(UPLOAD_FOLDER, key.filename)

    file.save(file_path)
    key.save(key_path)

    # Descifrar la clave AES con RSA
    clave_privada = cargar_clave("private_key.pem", es_privada=True)
    with open(key_path, "rb") as f:
        clave_aes_cifrada = f.read()
    clave_aes = descifrar_clave_aes(clave_aes_cifrada, clave_privada)

    # Descifrar el archivo
    archivo_descifrado = file_path.replace(".enc", "")
    descifrar_archivo(file_path, archivo_descifrado, clave_aes)

    return send_file(archivo_descifrado, as_attachment=True)

# Ruta para el foro
@app.route("/foro", methods=["GET", "POST"])
def foro():
    if request.method == "POST":
        data = request.json
        with open(FORO_FILE, "a") as f:
            f.write(f"{data['nickname']}: {data['message']}\n")
        return jsonify({"success": True})
    else:
        if not os.path.exists(FORO_FILE):
            return jsonify([])
        
        messages = []
        with open(FORO_FILE, "r") as f:
            for line in f.readlines():
                line = line.strip()
                if not line:
                    continue  # Saltar líneas vacías
                try:
                    nickname, message = line.split(": ", 1)  # Dividir solo en la primera ocurrencia
                    messages.append({"nickname": nickname, "message": message})
                except ValueError:
                    continue  # Saltar líneas mal formateadas
        
        return jsonify(messages)

# Iniciar el servidor
if __name__ == "__main__":
    # Generar claves RSA si no existen
    if not os.path.exists("private_key.pem") or not os.path.exists("public_key.pem"):
        private_key, public_key = generar_claves_rsa()
        guardar_clave(private_key, "private_key.pem", es_privada=True)
        guardar_clave(public_key, "public_key.pem", es_privada=False)
    app.run(debug=True)