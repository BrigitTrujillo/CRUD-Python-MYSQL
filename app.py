from flask import Flask, render_template, request, url_for, flash
from werkzeug.utils import redirect
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os
import uuid
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

import os

# ...

S3_BUCKET = os.getenv('S3_BUCKET')
S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY')
S3_REGION = os.getenv('S3_REGION')

s3 = boto3.client(
    's3',
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION
)

# ...


app = Flask(__name__)
# Other configurations...

upload_folder = 'uploads'

if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)




app = Flask(__name__)
app.secret_key = 'many random bytes'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'productos'
app.config['UPLOAD_FOLDER'] = 'uploads'

mysql = MySQL(app)

@app.route('/productos')
def Index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM productos")
    data = cur.fetchall()
    cur.close()

    return render_template('index.html', students=data)

@app.route('/')
def inicio():
    return render_template('inicio.html')


@app.route('/insert', methods=['POST'])
def insert():
    if request.method == "POST":
        flash("Data Inserted Successfully")
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        stock = request.form['stock']
        
        imagen = request.files['imagen']
        if imagen:
            # Generar un nombre único para la imagen
            filename = str(uuid.uuid4().hex) + secure_filename(imagen.filename)
            
            # Upload the image to S3
            try:
                s3.upload_fileobj(imagen, S3_BUCKET, filename)
                image_url = filename
            except NoCredentialsError:
                flash('AWS credentials not available.')
                return redirect(url_for('Index'))

        else:
            filename = None
            image_url = None
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO productos (nombre, descripcion, precio, stock, imagen, imagen_url) VALUES (%s, %s, %s, %s, %s, %s)", (nombre, descripcion, precio, stock, filename, image_url))

        mysql.connection.commit()
        return redirect(url_for('Index'))



@app.route('/delete/<int:id_data>', methods=['GET'])
def delete(id_data):
    cur = mysql.connection.cursor()

    # Obtener los detalles del producto antes de eliminarlo
    # Obtener la imagen_url del registro a eliminar
    cur.execute("SELECT imagen_url FROM productos WHERE id = %s", (id_data,))
    result = cur.fetchone()
    imagen_url = result[0] if result else None
    if imagen_url:
        try:
            url_parts = imagen_url.split('/')
            filename = url_parts[-1]
            s3.delete_object(Bucket=S3_BUCKET, Key=filename)
        except NoCredentialsError:
            flash('AWS credentials not available.')

    cur.execute("DELETE FROM productos WHERE id = %s", (id_data,))
    mysql.connection.commit()
    flash("Data Deleted Successfully")
    return redirect(url_for('Index'))



   
    
    
@app.route('/update', methods=['POST', 'GET'])
def update():
    if request.method == 'POST':
        id_data = request.form['id']
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        stock = request.form['stock']
        
        imagen = request.files['imagen']
        if imagen:
            # Generar un nombre único para la imagen
            filename = str(uuid.uuid4().hex) + secure_filename(imagen.filename)
            
            # Upload the image to S3
            try:
                s3.upload_fileobj(imagen, S3_BUCKET, filename)
                image_url = filename
                
                # Actualizar la columna de imagen en la base de datos solo si se proporciona una nueva imagen
                cur = mysql.connection.cursor()
                cur.execute("""
                    UPDATE productos SET nombre=%s, descripcion=%s, precio=%s, stock=%s, imagen=%s, imagen_url=%s
                    WHERE id=%s
                """, (nombre, descripcion, precio, stock, filename, image_url, id_data))
                mysql.connection.commit()
            except NoCredentialsError:
                flash('AWS credentials not available.')
                return redirect(url_for('Index'))
        else:
            # Mantener la imagen existente en la base de datos
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE productos SET nombre=%s, descripcion=%s, precio=%s, stock=%s
                WHERE id=%s
            """, (nombre, descripcion, precio, stock,  id_data))
            mysql.connection.commit()
        
        flash("Data Updated Successfully")
        return redirect(url_for('Index'))





if __name__ == "__main__":
    app.run(debug=True)
