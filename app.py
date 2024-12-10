from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text, inspect
import os
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')

# Configuração do banco de dados
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    DATABASE_URL = 'sqlite:///rankflow.db'
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o SQLAlchemy
db = SQLAlchemy(app)

# Configuração do LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelos do banco de dados
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    nome = db.Column(db.String(80), nullable=False)
    clientes = db.relationship('Cliente', backref='usuario', lazy=True)

    def get_id(self):
        return str(self.id)

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    website = db.Column(db.String(200))
    descricao = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

class Tarefa(db.Model):
    __tablename__ = 'tarefa'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    prazo = db.Column(db.Date)
    status = db.Column(db.String(20), default='pendente')

class EtapaSEO(db.Model):
    __tablename__ = 'etapa_seo'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    ordem = db.Column(db.Integer)

class ProgressoSEO(db.Model):
    __tablename__ = 'progresso_seo'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    etapa_id = db.Column(db.Integer, db.ForeignKey('etapa_seo.id'), nullable=False)
    status = db.Column(db.String(20), default='todo')
    observacoes = db.Column(db.Text)

def init_app(app):
    with app.app_context():
        try:
            logger.info("Tentando criar tabelas...")
            db.create_all()
            logger.info("Tabelas criadas com sucesso!")
            
            # Verifica se já existe um usuário admin
            admin = Usuario.query.filter_by(email='admin@admin.com').first()
            if not admin:
                logger.info("Criando usuário admin...")
                hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256')
                admin = Usuario(
                    email='admin@admin.com',
                    senha=hashed_password,
                    nome='Administrador'
                )
                db.session.add(admin)
                db.session.commit()
                logger.info("Usuário admin criado com sucesso!")
            else:
                logger.info("Usuário admin já existe!")
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {str(e)}")
            if hasattr(e, '__cause__'):
                logger.error(f"Causa do erro: {e.__cause__}")

# Inicializa o app
init_app(app)

@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    clientes = Cliente.query.filter_by(usuario_id=current_user.id).all()
    return render_template('dashboard.html', clientes=clientes)

@app.route('/cliente/novo', methods=['GET', 'POST'])
@login_required
def novo_cliente():
    if request.method == 'POST':
        try:
            # Log dos dados recebidos
            logger.info("Dados do formulário recebidos:")
            logger.info(f"Nome: {request.form.get('nome')}")
            logger.info(f"Website: {request.form.get('website')}")
            logger.info(f"Descrição: {request.form.get('descricao')}")
            
            # Obtém os dados do formulário
            nome = request.form.get('nome')
            website = request.form.get('website')
            descricao = request.form.get('descricao')
            
            # Validação básica
            if not nome:
                flash('O nome do cliente é obrigatório.', 'error')
                return render_template('novo_cliente.html')
            
            # Cria o novo cliente
            novo_cliente = Cliente(
                nome=nome,
                website=website,
                descricao=descricao,
                usuario_id=current_user.id
            )
            
            # Log antes de adicionar ao banco
            logger.info("Tentando adicionar cliente ao banco de dados")
            
            # Adiciona e salva no banco de dados
            db.session.add(novo_cliente)
            db.session.commit()
            
            logger.info("Cliente adicionado com sucesso!")
            flash('Cliente adicionado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao adicionar cliente: {str(e)}")
            if hasattr(e, '__cause__'):
                logger.error(f"Causa do erro: {e.__cause__}")
            flash('Erro ao adicionar cliente. Por favor, tente novamente.', 'error')
            return render_template('novo_cliente.html')
    
    return render_template('novo_cliente.html')

@app.route('/health')
def health_check():
    try:
        # Tenta fazer uma consulta simples
        db.session.execute(text('SELECT 1'))
        
        # Lista todas as tabelas
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'tables': tables
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'type': str(type(e))
        }), 500

@login_manager.user_loader
def load_user(user_id):
    try:
        return Usuario.query.get(int(user_id))
    except Exception as e:
        logger.error(f"Erro ao carregar usuário: {str(e)}")
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        user = Usuario.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.senha, senha):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Email ou senha inválidos.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
