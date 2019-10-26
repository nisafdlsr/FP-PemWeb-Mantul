import re
import MySQLdb.cursors
from flask_mysqldb import MySQL
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

# BUAT JAGA-JAGA AJA
app.secret_key = 'TERSERAH'

# KONEKSIKEN KE DATABASE
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'neurahealth_users'
mysql = MySQL(app)

# RUTE UNTUK LAMAN LOGIN => http://localhost:5000/pythonlogin/
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    msg = ''   # VARIABEL UNTUK MENAMPUNG PESAN
    
    # CEK APAKAH USERNAME & PASSWORD SESUAI & ADA PADA DATABASE KITA
    if request.method == 'POST' and 'email' in request.form and 'pass_word' in request.form:
        email = request.form['email']
        pass_word = request.form['pass_word']
        
        # PENELUSURAN PADA DATABASE
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s AND pass_word = %s', (email, pass_word))
        account = cursor.fetchone()   # AMBIL SATU BARIS DATA
        
        # JIKA USERNAME & PASSWORD BENAR + DATANYA ADA PADA DATABASE KITA
        if account:
            # AGAR VARIABEL DI BAWAH INI DAPAT DIAKSES LEWAT RUTE LAIN
            session['loggedin'] = True
            session['doctor_id'] = account['doctor_id']
            session['doctor_name'] = account['doctor_name']
            
            # LANGSUNG MASUK KE LAMAN home ATAU dashboard
            return redirect(url_for('home'))
        
        # JIKA USERNAME/PASSWORD SALAH DAN/ATAU DATANYA TIDAK ADA PADA DATABASE KITA
        else:
            msg = 'Email/password salah!'
    
    return render_template('index.html', msg=msg)

# RUTE UNTUK LAMAN REGISTER => http://localhost:5000/pythinlogin/register
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    msg = '' # VARIABEL UNTUK MENAMPUNG PESAN

    # CEK APAKAH DATA YANG DIMASUKKAN SUDAH ADA PADA DATABASE
    if request.method == 'POST' and 'doctor_name' in request.form and 'pass_word' in request.form and 'email' in request.form and 'hospital_name' in request.form and 'hospital_code' in request.form:
        doctor_name = request.form['doctor_name']
        pass_word = request.form['pass_word']
        email = request.form['email']
        hospital_name = request.form['hospital_name']
        hospital_code = request.form['hospital_code']

        # PENELUSURAN PADA DATABASE
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM accounts WHERE doctor_name = '{0}'".format(doctor_name))
        account = cursor.fetchone()   # AMBIL SATU DATA

        # TAMPILKAN PESAN ERROR APABILA AKUN SUDAH TERDAFTAR PADA DATABASE KITA
        if account:
            msg = 'Akun itu sudah ada!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Alamat email salah'
        elif not re.match(r'[A-Za-z0-9]+', doctor_name):
            msg = 'Cuma angka dan huruf saja!'
        elif not doctor_name or not pass_word or not email or not hospital_name or not hospital_code:
            msg = 'Masih ada data yang belum dimasukkan!'
        
        # JIKA AKUN TERSEBUT TIDAK ADA PADA DATABASE KITA
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s, %s)', (doctor_name, pass_word, email, hospital_name, hospital_code)) # NULL KARENA KOLOM ID AUTOINCREMENT
            mysql.connection.commit()
            msg = 'Anda sudah terdaftar!'
    
    # JIKA KLIK REGISTER TAPI ADA DATA YANG MASIH BELUM TERISI
    elif request.method == 'POST':
        msg = 'Masih ada data yang belum dimasukkan!'

    return render_template('register.html', msg=msg)

# RUTE UNTUK LAMAN HOME => http://localhost:5000/pythinlogin/home
@app.route('/pythonlogin/home')
def home():
    # CEK APAKAH USER SUDAH LOGIN
    if 'loggedin' in session:
        return render_template('home.html', doctor_name=session['doctor_name'])
    
    # JIKA BELUM LOGIN MAKA BALIK KE LAMAN LOGIN
    return redirect(url_for('login'))

# RUTE UNTUK LAMAN PROFIL => http://localhost:5000/pythinlogin/profile
@app.route('/pythonlogin/profile')
def profile():
    # CEK APAKAH USER SUDAH LOGIN
    if 'loggedin' in session:
        # AKSES DATABASE
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE doctor_id = %s', [session['doctor_id']])
        account = cursor.fetchone()   # AMBIL SATU DATA
        
        return render_template('profile.html', account=account)
    
    # JIKA BELUM LOGIN MAKA BALIK KE LAMAN LOGIN
    return redirect(url_for('login'))

# RUTE UNTUK LAMAN LOGOUT => http://localhost:5000/pythonlogin/logout
@app.route('/pythonlogin/logout')
def logout():
    # HAPUS DATA YANG TERSIMPAN SELAMA SESI
    session.pop('loggedin', None)
    session.pop('doctor_id', None)
    session.pop('doctor_name', None)
    
    # BALIK KE LAMAN LOGIN
    return redirect(url_for('login'))
