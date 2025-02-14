from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_123'

# Usaremos un CSV temporalmente antes de conectar con Google Sheets
USERS_FILE = 'users.csv'

# Crear el archivo CSV si no existe
if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=[
        'email', 
        'password', 
        'tipo_perfil',
        'empresa',
        'nit',
        'nombres',
        'apellidos',
        'contacto',
        'fecha_registro'
    ]).to_csv(USERS_FILE, index=False)

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Leer usuarios del CSV con tipos de datos específicos
        users_df = pd.read_csv(USERS_FILE, dtype={
            'contacto': str,
            'nit': str
        })
        user = users_df[users_df['email'] == email]
        
        if not user.empty and user.iloc[0]['password'] == password:
            session['user'] = email
            session['tipo_perfil'] = user.iloc[0]['tipo_perfil']
            
            if user.iloc[0]['tipo_perfil'] == 'empresa':
                session['empresa'] = user.iloc[0]['empresa']
                session['nit'] = user.iloc[0]['nit']
            else:
                session['nombres'] = user.iloc[0]['nombres']
                session['apellidos'] = user.iloc[0]['apellidos']
                session['contacto'] = user.iloc[0]['contacto']
            
            return redirect(url_for('home'))
        flash('Credenciales incorrectas')
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        tipo_perfil = request.form['tipo_perfil']
        
        # Leer usuarios del CSV con tipos de datos específicos
        users_df = pd.read_csv(USERS_FILE, dtype={
            'contacto': str,
            'nit': str
        })
        
        if email in users_df['email'].values:
            flash('El correo electrónico ya está registrado')
            return render_template('registro.html')
            
        # Crear diccionario base para el nuevo usuario
        new_user_data = {
            'email': [email],
            'password': [password],
            'tipo_perfil': [tipo_perfil],
            'empresa': [''],
            'nit': [''],
            'nombres': [''],
            'apellidos': [''],
            'contacto': [''],
            'fecha_registro': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        }

        if tipo_perfil == 'empresa':
            new_user_data['empresa'] = [request.form['empresa']]
            new_user_data['nit'] = [str(request.form['nit'])]
        else:
            new_user_data['empresa'] = ['Consultor Independiente']
            new_user_data['nombres'] = [request.form['nombres']]
            new_user_data['apellidos'] = [request.form['apellidos']]
            new_user_data['contacto'] = [str(request.form['contacto'])]

        # Agregar nuevo usuario
        new_user = pd.DataFrame(new_user_data)
        users_df = pd.concat([users_df, new_user], ignore_index=True)
        users_df.to_csv(USERS_FILE, index=False)
        
        flash('¡Registro exitoso! Por favor inicia sesión')
        return redirect(url_for('login'))
    
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)