from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text, inspect, func, and_
from whitenoise import WhiteNoise
import os
import logging
from datetime import datetime, timedelta
import gzip
from functools import wraps
from sqlalchemy.orm import joinedload, lazyload
import traceback

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

# Configuração do WhiteNoise para arquivos estáticos
app.wsgi_app = WhiteNoise(
    app.wsgi_app,
    root='static/',
    prefix='static/'
)

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
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Relacionamentos
    tarefas = db.relationship('Tarefa', backref='cliente', lazy=True)
    progresso_seo = db.relationship('ProgressoSEO', backref='cliente', lazy=True)
    seo_tecnico_status = db.relationship('SeoTecnicoStatus', backref='cliente', lazy=True)

    def __init__(self, nome, website=None, descricao=None, usuario_id=None):
        self.nome = nome
        self.website = website
        self.descricao = descricao
        self.usuario_id = usuario_id

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

class SeoTecnicoCategoria(db.Model):
    __tablename__ = 'seo_tecnico_categoria'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    ordem = db.Column(db.Integer)
    
    # Relacionamento com itens
    itens = db.relationship('SeoTecnicoItem', backref='categoria', lazy=True, order_by='SeoTecnicoItem.ordem')

class SeoTecnicoItem(db.Model):
    __tablename__ = 'seo_tecnico_item'
    id = db.Column(db.Integer, primary_key=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('seo_tecnico_categoria.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    documentacao_url = db.Column(db.String(255))
    ordem = db.Column(db.Integer)
    
    # Relacionamento com status
    status = db.relationship('SeoTecnicoStatus', backref='item', lazy=True)

class SeoTecnicoStatus(db.Model):
    __tablename__ = 'seo_tecnico_status'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('seo_tecnico_item.id'), nullable=False)
    status = db.Column(db.String(20), default='pendente')
    prioridade = db.Column(db.String(20), default='media')
    observacoes = db.Column(db.Text)
    data_verificacao = db.Column(db.DateTime)
    data_atualizacao = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

def init_app(app):
    with app.app_context():
        try:
            logger.info("Tentando criar tabelas...")
            db.create_all()
            logger.info("Tabelas criadas com sucesso!")
            
            try:
                # Executa as migrações para garantir que todas as colunas existam
                from migrations import run_migrations
                run_migrations()
                logger.info("Migrações executadas com sucesso!")
            except ImportError:
                logger.warning("Módulo de migrações não encontrado. Continuando sem executar migrações.")
            except Exception as e:
                logger.error(f"Erro ao executar migrações: {str(e)}")
                logger.error("Continuando a inicialização mesmo com erro nas migrações...")
            
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
            db.session.rollback()
            # Não vamos levantar a exceção para permitir que a aplicação continue
            logger.warning("Continuando a inicialização mesmo com erros...")

# Inicializa o app
init_app(app)

# Função para comprimir resposta HTML
def minify_html(html_content):
    # Remove espaços em branco extras e quebras de linha
    import re
    html_content = re.sub(r'>\s+<', '><', html_content)
    html_content = re.sub(r'\s{2,}', ' ', html_content)
    return html_content.strip()

def gzip_response(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        if not request.path.startswith('/static/'):
            accept_encoding = request.headers.get('Accept-Encoding', '')
            if 'gzip' in accept_encoding:
                content = gzip.compress(response.data)
                response.data = content
                response.headers['Content-Encoding'] = 'gzip'
                response.headers['Vary'] = 'Accept-Encoding'
                response.headers['Content-Length'] = len(content)
        return response
    return decorated_function

@app.after_request
def add_security_and_compression_headers(response):
    # Headers de segurança existentes...
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Compressão gzip para respostas não-estáticas
    if not request.path.startswith('/static/'):
        accept_encoding = request.headers.get('Accept-Encoding', '')
        if 'gzip' in accept_encoding and len(response.data) > 500:
            content = gzip.compress(response.data)
            response.data = content
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Vary'] = 'Accept-Encoding'
            response.headers['Content-Length'] = len(content)
    
    # Cache headers
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000'
    else:
        response.headers['Cache-Control'] = 'public, max-age=300'
    
    return response

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # Busca os clientes com seus relacionamentos
        clientes = Cliente.query.filter_by(usuario_id=current_user.id).all()
        
        total_clientes = len(clientes)
        stats = {}
        
        return render_template('dashboard.html', 
                             clientes=clientes,
                             total_clientes=total_clientes,
                             **stats)
    except Exception as e:
        logger.error(f"Erro no dashboard: {str(e)}")
        flash('Erro ao carregar o dashboard', 'error')
        return redirect(url_for('login'))

@app.route('/clientes')
@login_required
def clientes():
    try:
        logger.info(f"Listando clientes para o usuário {current_user.id}")
        clientes = Cliente.query.filter_by(usuario_id=current_user.id).all()
        return render_template('clientes.html', clientes=clientes)
    except Exception as e:
        logger.error(f"Erro ao listar clientes: {str(e)}")
        flash('Ocorreu um erro ao carregar a lista de clientes.', 'error')
        return render_template('clientes.html', clientes=[])

@app.route('/cliente/<int:cliente_id>/seo-roadmap')
@login_required
def seo_roadmap(cliente_id):
    try:
        # Verificar se o cliente existe e pertence ao usuário atual
        cliente = Cliente.query.filter_by(id=cliente_id, usuario_id=current_user.id).first()
        if not cliente:
            flash('Cliente não encontrado.', 'danger')
            return redirect(url_for('dashboard'))
            
        logger.info(f"Acessando SEO Roadmap do cliente {cliente_id}")
        
        # Buscar etapas e progresso
        etapas = EtapaSEO.query.order_by(EtapaSEO.ordem).all()
        progresso = ProgressoSEO.query.filter_by(cliente_id=cliente_id).all()
        
        return render_template('seo_roadmap.html',
            cliente=cliente,
            etapas=etapas,
            progresso=progresso
        )
        
    except Exception as e:
        logger.error(f"Erro ao carregar SEO Roadmap do cliente {cliente_id}: {str(e)}")
        flash('Erro ao carregar o módulo SEO Roadmap.', 'danger')
        return redirect(url_for('detalhe_cliente', id=cliente_id))

@app.route('/cliente/<int:id>')
@login_required
def detalhe_cliente(id):
    try:
        # Verificar se o cliente existe e pertence ao usuário atual
        cliente = Cliente.query.filter_by(id=id, usuario_id=current_user.id).first()
        if not cliente:
            logger.warning(f"Cliente {id} não encontrado ou não pertence ao usuário {current_user.id}")
            flash('Cliente não encontrado.', 'danger')
            return redirect(url_for('dashboard'))
            
        logger.info(f"Carregando detalhes do cliente {id}")
        
        # Buscar dados adicionais
        keywords_count = 0  # TODO: Implementar contagem real
        improved_rankings = 0  # TODO: Implementar contagem real
        total_rankings = 1  # Para evitar divisão por zero
        completed_tasks = 0  # TODO: Implementar contagem real
        total_tasks = 1  # Para evitar divisão por zero
        reports_count = 0  # TODO: Implementar contagem real
        
        # Simular algumas atividades recentes
        activities = [
            {
                'title': 'Análise SEO Técnica',
                'description': 'Análise técnica do site concluída',
                'date': datetime.now()
            },
            {
                'title': 'Nova Palavra-chave',
                'description': 'Adicionada nova palavra-chave para monitoramento',
                'date': datetime.now()
            }
        ]
        
        # Simular algumas palavras-chave
        keywords = [
            {
                'termo': 'marketing digital',
                'posicao': 5,
                'status': 'up',
                'variacao': 2
            },
            {
                'termo': 'seo otimização',
                'posicao': 8,
                'status': 'down',
                'variacao': 1
            }
        ]
        
        logger.info(f"Renderizando template com os dados do cliente {id}")
        return render_template('detalhe_cliente.html',
            cliente=cliente,
            keywords_count=keywords_count,
            improved_rankings=improved_rankings,
            total_rankings=total_rankings,
            completed_tasks=completed_tasks,
            total_tasks=total_tasks,
            reports_count=reports_count,
            activities=activities,
            keywords=keywords
        )
    except Exception as e:
        logger.error(f"Erro ao carregar detalhes do cliente {id}: {str(e)}")
        flash('Erro ao carregar os detalhes do cliente.', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/novo-cliente', methods=['GET', 'POST'])
@login_required
def novo_cliente():
    if request.method == 'POST':
        nome = request.form.get('nome')
        website = request.form.get('website')
        descricao = request.form.get('descricao')

        if not nome:
            flash('O nome do cliente é obrigatório.', 'danger')
            return redirect(url_for('novo_cliente'))

        cliente = Cliente(
            nome=nome,
            website=website,
            descricao=descricao,
            usuario_id=current_user.id
        )

        try:
            db.session.add(cliente)
            db.session.commit()
            flash('Cliente cadastrado com sucesso!', 'success')
            return redirect(url_for('detalhe_cliente', id=cliente.id))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao cadastrar cliente: {str(e)}")
            flash('Erro ao cadastrar cliente. Por favor, tente novamente.', 'danger')
            return redirect(url_for('novo_cliente'))

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

@app.route('/seo-tecnico/<int:cliente_id>')
@login_required
def seo_tecnico(cliente_id):
    try:
        logger.info(f"Iniciando rota SEO Técnico para cliente_id: {cliente_id}")
        logger.info(f"Usuário atual: {current_user.id}")
        
        # Verificar se o cliente pertence ao usuário atual
        cliente = Cliente.query.filter_by(id=cliente_id, usuario_id=current_user.id).first()
        
        if not cliente:
            logger.error(f"Cliente {cliente_id} não encontrado ou não pertence ao usuário {current_user.id}")
            flash('Cliente não encontrado ou sem permissão', 'error')
            return redirect(url_for('dashboard'))
        
        logger.info(f"Cliente encontrado: {cliente.nome}")
        
        # Buscar categorias e itens
        categorias = SeoTecnicoCategoria.query.order_by(SeoTecnicoCategoria.ordem).all()
        logger.info(f"Total de categorias: {len(categorias)}")
        
        dados_categorias = []
        itens_status = {}
        total_items = 0
        completed_count = 0
        in_progress_count = 0
        high_priority_count = 0
        
        for categoria in categorias:
            logger.info(f"Processando categoria: {categoria.nome}")
            
            categoria_dados = {
                'id': categoria.id,
                'nome': categoria.nome,
                'descricao': categoria.descricao,
                'itens': []
            }
            
            # Buscar itens da categoria
            itens = SeoTecnicoItem.query.filter_by(categoria_id=categoria.id).order_by(SeoTecnicoItem.ordem).all()
            logger.info(f"Total de itens na categoria {categoria.nome}: {len(itens)}")
            
            for item in itens:
                total_items += 1
                
                # Buscar ou criar status do item
                status = SeoTecnicoStatus.query.filter_by(
                    cliente_id=cliente_id, 
                    item_id=item.id
                ).first()
                
                if not status:
                    status = SeoTecnicoStatus(
                        cliente_id=cliente_id,
                        item_id=item.id,
                        status='pendente',
                        prioridade='media'
                    )
                    db.session.add(status)
                
                # Contadores de status
                status_item = status.status
                if status_item == 'concluido':
                    completed_count += 1
                elif status_item == 'em_progresso':
                    in_progress_count += 1
                
                if status.prioridade == 'alta':
                    high_priority_count += 1
                
                categoria_dados['itens'].append({
                    'id': item.id,
                    'nome': item.nome,
                    'descricao': item.descricao,
                    'documentacao_url': item.documentacao_url,
                    'status': status_item
                })
                
                # Adicionar status do item por categoria
                if categoria.id not in itens_status:
                    itens_status[categoria.id] = []
                
                itens_status[categoria.id].append({
                    'item': item,
                    'status': status
                })
            
            dados_categorias.append(categoria_dados)
        
        # Calcular progresso
        progress = (completed_count / total_items * 100) if total_items > 0 else 0
        
        # Commit das alterações
        db.session.commit()
        
        logger.info(f"Renderizando página SEO Técnico para cliente {cliente_id}")
        logger.info(f"Métricas: Total={total_items}, Concluídos={completed_count}, Em Progresso={in_progress_count}, Alta Prioridade={high_priority_count}")
        
        return render_template('seo_tecnico.html', 
                               cliente=cliente, 
                               categorias=dados_categorias,
                               itens_status=itens_status,
                               progress=round(progress, 2),
                               completed_count=completed_count,
                               in_progress_count=in_progress_count,
                               high_priority_count=high_priority_count,
                               total_items=total_items)
    except Exception as e:
        logger.error(f"Erro em SEO Técnico: {str(e)}")
        logger.error(f"Detalhes do erro: {traceback.format_exc()}")
        flash('Erro ao carregar SEO Técnico', 'error')
        return redirect(url_for('dashboard'))

@app.route('/api/seo-tecnico/atualizar-status', methods=['POST'])
@login_required
def atualizar_status_seo_tecnico():
    try:
        data = request.get_json()
        cliente_id = data.get('cliente_id')
        item_id = data.get('item_id')
        novo_status = data.get('status')
        nova_prioridade = data.get('priority')

        # Verificar se o cliente pertence ao usuário atual
        cliente = Cliente.query.filter_by(id=cliente_id, usuario_id=current_user.id).first_or_404()
        
        app.logger.info(f"Atualizando status do item {item_id} para cliente {cliente_id}")
        
        # Buscar ou criar status
        status = SeoTecnicoStatus.query.filter_by(
            cliente_id=cliente_id,
            item_id=item_id
        ).first()
        
        if not status:
            status = SeoTecnicoStatus(
                cliente_id=cliente_id,
                item_id=item_id,
                status='pendente',
                prioridade='media'
            )
            db.session.add(status)
        
        # Atualizar status e/ou prioridade
        if novo_status:
            status.status = novo_status
        if nova_prioridade:
            status.prioridade = nova_prioridade
        
        status.data_atualizacao = db.func.current_timestamp()
        db.session.commit()
        
        app.logger.info(f"Status atualizado com sucesso: {novo_status}, prioridade: {nova_prioridade}")
        
        return jsonify({'success': True})
        
    except Exception as e:
        app.logger.error(f"Erro ao atualizar status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/usuario/excluir', methods=['POST'])
@login_required
def excluir_usuario():
    try:
        # Excluir todos os dados relacionados ao usuário
        # Primeiro, excluir registros dependentes
        SeoTecnicoStatus.query.filter(SeoTecnicoStatus.cliente_id.in_(
            db.session.query(Cliente.id).filter_by(usuario_id=current_user.id)
        )).delete(synchronize_session=False)
        
        ProgressoSEO.query.filter(ProgressoSEO.cliente_id.in_(
            db.session.query(Cliente.id).filter_by(usuario_id=current_user.id)
        )).delete(synchronize_session=False)
        
        Tarefa.query.filter(Tarefa.cliente_id.in_(
            db.session.query(Cliente.id).filter_by(usuario_id=current_user.id)
        )).delete(synchronize_session=False)
        
        Cliente.query.filter_by(usuario_id=current_user.id).delete()
        Usuario.query.filter_by(id=current_user.id).delete()
        
        db.session.commit()
        logout_user()
        
        logger.info(f"Usuário {current_user.email} excluído com sucesso")
        flash('Conta excluída com sucesso.', 'success')
        return redirect(url_for('login'))
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao excluir usuário: {str(e)}", exc_info=True)
        flash('Erro ao excluir conta. Por favor, tente novamente.', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/configuracoes', methods=['GET'])
@login_required
def configuracoes():
    try:
        logger.info(f"Carregando configurações para usuário {current_user.id}")
        return render_template('configuracoes.html')
    except Exception as e:
        logger.error(f"Erro ao carregar configurações: {str(e)}", exc_info=True)
        flash('Erro ao carregar configurações.', 'danger')
        return redirect(url_for('dashboard'))

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
                # Faz login automático após o cadastro
                login_user(novo_usuario)
                flash('Cadastro realizado com sucesso!', 'success')
                return redirect(url_for('dashboard'))
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
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server at port {port}")
    app.run(host='0.0.0.0', port=port)
