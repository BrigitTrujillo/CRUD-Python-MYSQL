from flask import Flask, render_template, request, url_for, flash
from werkzeug.utils import redirect
from flask_mysqldb import MySQL


app = Flask(__name__)
app.secret_key = 'many random bytes'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'productos'

mysql = MySQL(app)

@app.route('/')
def Index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM productos")
    data = cur.fetchall()
    cur.close()

    return render_template('index.html', students=data)


@app.route('/insert', methods = ['POST'])
def insert():
    if request.method == "POST":
        flash("Data Inserted Successfully")
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        stock = request.form['stock']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO productos (nombre, descripcion, precio, stock) VALUES (%s, %s, %s,  %s)", (nombre, descripcion, precio, stock))
        mysql.connection.commit()
        return redirect(url_for('Index'))

@app.route('/delete/<string:id_data>', methods = ['GET'])
def delete(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM productos WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('Index'))



@app.route('/update', methods= ['POST', 'GET'])
def update():
    if request.method == 'POST':
        id_data = request.form['id']
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        stock = request.form['stokc']

        cur = mysql.connection.cursor()
        cur.execute("""
        UPDATE proudctos SET nombre=%s, descripcion=%s, precio=%s, stock=%s
        WHERE id=%s
        """, (nombre, descripcion, precio,stock, id_data))
        flash("Data Updated Successfully")
        return redirect(url_for('Index'))




if __name__ == "__main__":
    app.run(debug=True)
