from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId 
from flask_login import current_user
import bcrypt

app = Flask(__name__)   

app.config['MONGO_URI'] = "mongodb+srv://admin123:admin123@Obelisk.lkhnesk.mongodb.net/Obelisk"
mongo = PyMongo(app)
db = mongo.db

@app.route('/')
def index():
    return render_template('index.html')

# encriptación de contrasenña
def encriptar(password):
    #sal aleatoria
    salt = bcrypt.gensalt()
    #encriptando la contraseña con sal
    contrasena_encriptada = bcrypt.hashpw(password.encode('utf-8'), salt)
    return contrasena_encriptada
def validar_contrasena(password, contrasena_encriptada):
    return bcrypt.checkpw(password.encode('utf-8'), contrasena_encriptada)
    
#registro de usuarios
@app.route('/procesar_registro', methods=['POST'])
def registrar():
    if request.method == "POST":
        nombre = request.form['nombre'] 
        correo = request.form['correo']
        password = request.form['password']
        usuario_id = ObjectId()
        password_encriptada = encriptar(password)
        db.Usuarios.insert_one({
            '_id': usuario_id,
            'nombre': nombre,
            'email': correo,
            'password': password_encriptada
        })
        print("Usuario registrado:", nombre, correo, password)
        return "Usuario registrado"
#Login de usuarios
@app.route('/procesar_login', methods=['POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']
        usuario = db.Usuarios.find_one({'email': correo})
        
        if usuario and validar_contrasena(password, usuario['password']):
            session[ 'usuario' ] =  str(usuario['_id'])
            return redirect(url_for('main_page'))
        else:
            return 'Usuario no encontrado'
        
#subir publicaciones
@app.route('/procesar_publicacion', methods=['POST'])
def publicar():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']

        # Verificar si se envió un archivo
        if 'imagen' in request.files:
            imagen = request.files['imagen']
            # Guardar la imagen en tu sistema de archivos o en tu servicio de almacenamiento preferido
            # En este ejemplo, solo se imprime el nombre del archivo
            print("Nombre del archivo:", imagen.filename)
        else:
            imagen = None

        publicacion_id = ObjectId()

        # Guardar la información en la base de datos
        db.Publicaciones.insert_one({
            '_id': publicacion_id,
            'titulo': titulo,
            'descripcion': descripcion,
            'imagen': imagen.filename if imagen else None  # Puedes guardar el nombre del archivo en la base de datos
        })

        print("Publicacion registrada:", titulo, descripcion, imagen.filename if imagen else None)
        return "Publicacion registrada"
#ver publicaciones 
@app.route('/ver_publicaciones')
def ver_publicaciones():
    # Obtener todas las publicaciones de la base de datos
    publicaciones = list(db.Publicaciones.find())

    # Pasar las publicaciones a la plantilla
    return render_template('main_page.html', publicaciones=publicaciones)

#hacer comentarios
@app.route('/hacer_comentario', methods=['POST'])
def comentar():
    if request.method == 'POST':
        comentario = request.form['contenido_comentario']
        publicacion_id = request.form['publicacion_id']
        correo = current_user.correo
        user_id = session['usuario']
        db.Comentarios.insert_one({
            'comentario': comentario,
            'correo': correo,
            'publicacion_id': publicacion_id,
            'user_id': user_id
        })
        print("Comentario registrado:", comentario)
        return redirect(url_for('ver_publicaciones'))
    
#ver comentarios
@app.route('/ver_comentarios')
def ver_comentarios():
    # Obtener todas las publicaciones de la base de datos
    comentarios = list(db.Comentarios.find())

    # Pasar las publicaciones a la plantilla
    return render_template('main_page.html', comentarios=comentarios)