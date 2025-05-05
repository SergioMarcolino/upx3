from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# sql
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mssql+pyodbc://localhost/ecoenergy?'
    'driver=ODBC+Driver+17+for+SQL+Server&'
    'trusted_connection=yes&'
    'TrustServerCertificate=yes'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'supersecretkey-dev-only'

db = SQLAlchemy(app)

# modelos do sql
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(512), nullable=False)

class Consumo(db.Model):
    __tablename__ = 'consumo'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.String(20), nullable=False)
    consumo_kwh = db.Column(db.Float, nullable=False)

class MediaEstadual(db.Model):
    __tablename__ = 'media_estadual'
    id = db.Column(db.Integer, primary_key=True)
    estado = db.Column(db.String(2), nullable=False)  
    ano = db.Column(db.Integer, nullable=False)
    media_kwh = db.Column(db.Float, nullable=False)

# rotas
@app.route('/')
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'usuario_id' in session:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        if not email or not senha:
            flash('Preencha todos os campos', 'danger')
            return render_template('login.html')
            
        usuario = Usuario.query.filter_by(email=email).first()
        
        if not usuario or not check_password_hash(usuario.senha, senha):
            flash('Email ou senha incorretos', 'danger')
            return render_template('login.html')
            
        session['usuario_id'] = usuario.id
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('index'))
        
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        senha2 = request.form.get('senha_confirmacao')

        if not all([nome, email, senha, senha2]):
            flash('Preencha todos os campos', 'danger')
            return redirect(url_for('cadastro'))

        if senha != senha2:
            flash('As senhas não coincidem.', 'danger')
            return redirect(url_for('cadastro'))

        if len(senha) < 6:
            flash('Senha deve ter pelo menos 6 caracteres', 'danger')
            return redirect(url_for('cadastro'))

        if Usuario.query.filter_by(email=email).first():
            flash('Email já registrado.', 'danger')
            return redirect(url_for('cadastro'))

        try:
            senha_hash = generate_password_hash(senha)
            novo_usuario = Usuario(nome=nome, email=email, senha=senha_hash)
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Cadastro feito com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao cadastrar. Tente novamente.', 'danger')
            return redirect(url_for('cadastro'))

    return render_template('cadastro.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('usuario_id', None)
    flash('Você foi deslogado com sucesso', 'info')
    return redirect(url_for('login'))

@app.route('/registrar_consumo', methods=['POST'])
def registrar_consumo():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        usuario_id = session['usuario_id']
        ano = int(request.form['ano'])
        mes = request.form['mes']
        kwh = float(request.form['kwh'])
        
        consumo = Consumo.query.filter_by(
            usuario_id=usuario_id,
            ano=ano,
            mes=mes
        ).first()

        if consumo:
            consumo.consumo_kwh = kwh
            message = 'Consumo atualizado com sucesso!'
        else:
            novo_consumo = Consumo(
                usuario_id=usuario_id,
                ano=ano,
                mes=mes,
                consumo_kwh=kwh
            )
            db.session.add(novo_consumo)
            message = 'Consumo registrado com sucesso!'
        
        db.session.commit()
        return jsonify({'success': True, 'message': message})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/media', methods=['POST'])
def media():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']
    ano = request.form['ano']
    estado = request.form['estado'].upper()

    consumos = Consumo.query.filter_by(usuario_id=usuario_id, ano=ano).all()
    total = sum(c.consumo_kwh for c in consumos) if consumos else 0
    media_user = total / len(consumos) if consumos else 0

    media_est = MediaEstadual.query.filter_by(estado=estado, ano=ano).first()
    media_estadual = media_est.media_kwh if media_est else 300

    if media_user <= media_estadual:
        resultado = "Seu consumo está abaixo da média estadual! ✅"
        cor = "verde"
    else:
        resultado = "Seu consumo está acima da média estadual. Considere reduzir. ⚠️"
        cor = "vermelha"

    return render_template(
        'index.html',
        resultado=resultado,
        cor=cor,
        media_usuario=round(media_user, 2),
        media_estadual=round(media_estadual, 2),
        ano=ano,
        estado=estado
    )

@app.route('/adicionar_medias_exemplo')
def adicionar_medias_exemplo():
    estados = {
            'AC': 220, 'AL': 210, 'AP': 230, 'AM': 280,
            'BA': 210, 'CE': 195, 'DF': 185, 'ES': 175,
            'GO': 200, 'MA': 215, 'MT': 240, 'MS': 230,
            'MG': 150, 'PA': 225, 'PB': 205, 'PR': 170,
            'PE': 200, 'PI': 215, 'RJ': 180, 'RN': 195,
            'RS': 190, 'RO': 235, 'RR': 250, 'SC': 185,
            'SP': 165, 'SE': 210, 'TO': 220
    }
    
    try:
        for estado, media in estados.items():
            for ano in range(2020, 2025):
                if not MediaEstadual.query.filter_by(estado=estado, ano=ano).first():
                    nova_media = MediaEstadual(
                        estado=estado,
                        ano=ano,
                        media_kwh=media
                    )
                    db.session.add(nova_media)
        
        db.session.commit()
        return "Médias estaduais de exemplo adicionadas com sucesso!"
    except Exception as e:
        db.session.rollback()
        return f"Erro: {str(e)}"

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)