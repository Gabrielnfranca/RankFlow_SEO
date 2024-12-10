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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
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
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

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
            
            # Executa as migrações para garantir que todas as colunas existam
            from migrations import run_migrations
            run_migrations()
            
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
            logger.error(f"Erro durante a inicialização: {str(e)}")
            if hasattr(e, '__cause__'):
                logger.error(f"Causa do erro: {e.__cause__}")
            raise

# Inicializa o app
init_app(app)

@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        logger.info(f"Acessando dashboard para o usuário {current_user.id}")
        clientes = Cliente.query.filter_by(usuario_id=current_user.id).all()
        logger.info(f"Encontrados {len(clientes)} clientes")
        return render_template('dashboard.html', clientes=clientes)
    except Exception as e:
        logger.error(f"Erro ao acessar dashboard: {str(e)}", exc_info=True)
        if hasattr(e, '__cause__'):
            logger.error(f"Causa do erro: {e.__cause__}")
        flash('Ocorreu um erro ao carregar o dashboard. Por favor, tente novamente.', 'error')
        return render_template('dashboard.html', clientes=[]), 500

@app.route('/cliente/novo', methods=['GET', 'POST'])
@login_required
def novo_cliente():
    try:
        if request.method == 'POST':
            nome = request.form.get('nome')
            website = request.form.get('website')
            descricao = request.form.get('descricao')

            if not nome:
                flash('O nome do cliente é obrigatório.', 'danger')
                return render_template('novo_cliente.html')

            cliente = Cliente(
                nome=nome,
                website=website,
                descricao=descricao,
                usuario_id=current_user.id
            )

            db.session.add(cliente)
            db.session.commit()

            flash('Cliente adicionado com sucesso!', 'success')
            return redirect(url_for('dashboard'))

        return render_template('novo_cliente.html')
    except Exception as e:
        logger.error(f"Erro ao adicionar cliente: {str(e)}", exc_info=True)
        db.session.rollback()
        flash('Erro ao adicionar cliente. Por favor, tente novamente.', 'danger')
        return render_template('novo_cliente.html')

@app.route('/cliente/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_cliente(id):
    try:
        cliente = Cliente.query.filter_by(id=id, usuario_id=current_user.id).first_or_404()

        if request.method == 'POST':
            cliente.nome = request.form.get('nome')
            cliente.website = request.form.get('website')
            cliente.descricao = request.form.get('descricao')

            if not cliente.nome:
                flash('O nome do cliente é obrigatório.', 'danger')
                return render_template('editar_cliente.html', cliente=cliente)

            db.session.commit()
            flash('Cliente atualizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))

        return render_template('editar_cliente.html', cliente=cliente)
    except Exception as e:
        logger.error(f"Erro ao editar cliente: {str(e)}", exc_info=True)
        db.session.rollback()
        flash('Erro ao editar cliente. Por favor, tente novamente.', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/cliente/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_cliente(id):
    try:
        cliente = Cliente.query.filter_by(id=id, usuario_id=current_user.id).first_or_404()
        db.session.delete(cliente)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Cliente excluído com sucesso!'})
    except Exception as e:
        logger.error(f"Erro ao excluir cliente: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Erro ao excluir cliente.'}), 500

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
    try:
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        # Captura e sanitiza o parâmetro next
        next_page = request.args.get('next', '')
        logger.info(f"Parâmetro next recebido: {next_page}")
        
        # Sanitiza o next_page para evitar redirecionamentos maliciosos
        if next_page and not next_page.startswith('/'):
            logger.warning(f"Tentativa de redirecionamento inválido: {next_page}")
            next_page = ''

        if request.method == 'POST':
            email = request.form.get('email')
            senha = request.form.get('senha')
            
            if not email or not senha:
                flash('Por favor, preencha todos os campos.', 'error')
                return render_template('login.html', next=next_page)
            
            try:
                user = Usuario.query.filter_by(email=email).first()
                
                if user and check_password_hash(user.senha, senha):
                    login_user(user)
                    
                    if next_page:
                        logger.info(f"Redirecionando para: {next_page}")
                        return redirect(next_page)
                    return redirect(url_for('dashboard'))
                
                flash('Email ou senha inválidos.', 'error')
            except Exception as e:
                logger.error(f"Erro no login: {str(e)}")
                flash('Ocorreu um erro ao tentar fazer login. Por favor, tente novamente.', 'error')
        
        return render_template('login.html', next=next_page)
    
    except Exception as e:
        logger.error(f"Erro inesperado na rota de login: {str(e)}", exc_info=True)
        flash('Ocorreu um erro inesperado. Por favor, tente novamente.', 'error')
        return render_template('login.html'), 500

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            nome = request.form.get('nome')
            email = request.form.get('email')
            senha = request.form.get('senha')
            confirmar_senha = request.form.get('confirmar_senha')

            # Validação dos campos
            if not all([nome, email, senha, confirmar_senha]):
                flash('Por favor, preencha todos os campos.', 'error')
                return render_template('cadastro.html')

            if senha != confirmar_senha:
                flash('As senhas não coincidem.', 'error')
                return render_template('cadastro.html')

            # Verifica se o email já está em uso
            usuario_existente = Usuario.query.filter_by(email=email).first()
            if usuario_existente:
                flash('Este email já está cadastrado.', 'error')
                return render_template('cadastro.html')

            # Cria o novo usuário
            novo_usuario = Usuario(
                nome=nome,
                email=email,
                senha=generate_password_hash(senha)
            )

            try:
                db.session.add(novo_usuario)
                db.session.commit()
                flash('Cadastro realizado com sucesso! Por favor, faça login.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Erro ao criar usuário: {str(e)}")
                flash('Erro ao criar usuário. Por favor, tente novamente.', 'error')
                return render_template('cadastro.html')

        return render_template('cadastro.html')
    except Exception as e:
        logger.error(f"Erro inesperado na rota de cadastro: {str(e)}", exc_info=True)
        flash('Ocorreu um erro inesperado. Por favor, tente novamente.', 'error')
        return render_template('cadastro.html'), 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
