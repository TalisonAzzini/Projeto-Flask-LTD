from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import bcrypt

app = Flask(__name__)           # Rota para o site
app.secret_key = 'rafaelds'     # Chave de teste
DATABASE = 'ltd.db'             # Variavel com o nome do db

def get_db_connection():                    # FUNÇÃO PARA CONECTAR NO BANCO DE DADOS
    conn = sqlite3.connect(DATABASE)            # Conecta com o banco de dados
    return conn                                 # Retorna a conexão

def criar_usuario(username, password):                                      # FUNÇÃO PARA REGISTRAR UM NOVO USUARIO NO BANCO DE DADOS
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())          # Variavel da senha criptografada
    conn = get_db_connection()                                                  # Inicia a conexão com o db
    cursor = conn.cursor()                                                      # Cria o cursor (para executar funções no db)
    try:
        cursor.execute("INSERT INTO usuarios (login, senha) VALUES (?, ?)", (username, hashed.decode('utf-8')))     # Comando SQL para inserir no db
        conn.commit()                                                                                               # Execução do comando
    except sqlite3.IntegrityError:
        return False            # Retorna false se o usuario já existir
    finally:
        conn.close()            # Fecha a conexão com o db
    return True                 # Retorna True se tudo ocorrer de acordo

def verificar_credenciais(username, password):                                          # FUNÇÃO RESPONSÁVEL PELA AUTENTICAÇÃO DE USUARIO
    conn = get_db_connection()                                                              # Inicia a conexão com o db
    cursor = conn.cursor()                                                                  # Cria o cursor (para executar funções no db)
    cursor.execute("SELECT senha FROM usuarios WHERE login=?", (username,))                 # Comando SQL
    result = cursor.fetchone()                                                              # Variavel para armazenar o resultado da consulta
    conn.close()                                                                            # Fecha a conexão com o db
    
    if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):      # Verifica se result não é None e se bcrypt.checkpw retorna True
        return True
    return False

@app.route('/', methods=['GET', 'POST'])                                # Define a rota principal
def login():                                                            # FUNÇÃO PARA EXECUTAR O LOGIN
    if request.method == 'POST':                                            # Verifica se o método da requisição é POST
        username = request.form['login']                                    # Variavel que obtem o valor do campo login
        password = request.form['senha']                                    # Variavel que obtem o valor do campo senha
        
        if verificar_credenciais(username, password):                       # Verifica as credenciais passando os parâmetros
            session['username'] = username                                  # Armazena o nome de usuário na sessão
            flash('Login realizado com sucesso!', 'success')                # Mostra uma mensagem de sucesso
            return redirect(url_for('home'))                                # Redireciona para a pagina home.html
        else:
            flash('Nome de usuário ou senha inválidos.', 'danger')          # Exibe mensagem de erro
    
    return render_template('login.html')                                    # Renderiza a tela de login

@app.route('/home')                                                             # Define a rota para a página 'home'
def home():                                                                     # FUNÇÃO PARA A PAGINA HOME
    if 'username' in session:                                                       # Verifica se o usuário está logado
        return render_template('home.html', name=session['username'])               # Renderiza a home.html com o nome do usuário logado
    return redirect(url_for('login'))                                               # Se nao estiver logado redireciona para login.html

@app.route('/logout')                                       # Define a rota para logout
def logout():                                               # FUNÇÃO PARA REALIZAR O LOGOUT
    session.pop('username', None)                               # Remove o nome de usuário da sessão
    flash('Você foi deslogado com sucesso.', 'info')            # Exibe uma mensagem quando sair
    return redirect(url_for('login'))                           # Redireciona para a pagina login.html

if __name__ == '__main__':                                      # Verifica se o script está sendo executado diretamente
    criar_usuario('Rafael', '123')                              # Usuário teste
    app.run(debug=True)                                         # Inicia o servidor Flask no modo de depuração