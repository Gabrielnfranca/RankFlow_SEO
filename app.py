from flask import Flask, render_template, request, redirect, url_for, flash, g, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import datetime
import json
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sua_chave_secreta_aqui')

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

@app.route('/health')
def health_check():
    try:
        # Tenta fazer uma consulta simples
        db.session.execute('SELECT 1')
        tables = db.engine.table_names()
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

# Modelos do banco de dados
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    nome = db.Column(db.String(80), nullable=False)
    
    def get_id(self):
        return str(self.id)

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    website = db.Column(db.String(200))
    descricao = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    tarefas = db.relationship('Tarefa', backref='cliente', lazy=True)

class Tarefa(db.Model):
    __tablename__ = 'tarefa'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    status = db.Column(db.String(20), default='todo')
    prioridade = db.Column(db.String(20), default='medium')
    checklist = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class EtapaSEO(db.Model):
    __tablename__ = 'etapa_seo'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    peso = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='todo')

class ProgressoSEO(db.Model):
    __tablename__ = 'progresso_seo'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    etapa_id = db.Column(db.Integer, db.ForeignKey('etapa_seo.id'), nullable=False)
    status = db.Column(db.String(20), default='todo')
    observacoes = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
    try:
        return Usuario.query.get(int(user_id))
    except Exception as e:
        logger.error(f"Erro ao carregar usuário: {str(e)}")
        return None

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            email = request.form.get('email')
            senha = request.form.get('senha')
            
            if not email or not senha:
                flash('Por favor, preencha todos os campos.', 'error')
                return render_template('login.html')
            
            usuario = Usuario.query.filter_by(email=email).first()
            
            if usuario and check_password_hash(usuario.senha, senha):
                login_user(usuario)
                return redirect(url_for('dashboard'))
            
            flash('Email ou senha incorretos.', 'error')
        return render_template('login.html')
    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        flash('Erro ao fazer login. Por favor, tente novamente.', 'error')
        return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        clientes = Cliente.query.filter_by(usuario_id=current_user.id).all()
        
        return render_template('dashboard.html', 
                            clientes=clientes,
                            total_clientes=len(clientes))
    except Exception as e:
        logger.error(f"Erro no dashboard: {str(e)}")
        flash('Erro ao carregar dashboard', 'error')
        return render_template('dashboard.html', clientes=[], total_clientes=0)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        nome = request.form.get('nome')
        
        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'error')
            return redirect(url_for('cadastro'))
        
        hash_senha = generate_password_hash(senha)
        usuario = Usuario(email=email, senha=hash_senha, nome=nome)
        db.session.add(usuario)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('login'))
    
    return render_template('cadastro.html')

@app.route('/clientes/novo', methods=['GET', 'POST'])
@login_required
def novo_cliente():
    if request.method == 'POST':
        nome = request.form.get('nome')
        website = request.form.get('website')
        descricao = request.form.get('descricao')
        
        if not nome:
            flash('O nome do cliente é obrigatório.', 'error')
            return redirect(url_for('novo_cliente'))
        
        try:
            cliente = Cliente(nome=nome, website=website, descricao=descricao, usuario_id=current_user.id)
            db.session.add(cliente)
            db.session.commit()
            
            flash('Cliente adicionado com sucesso!', 'success')
            return redirect(url_for('cliente_detalhes', cliente_id=cliente.id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao adicionar cliente: {str(e)}")
            flash('Erro ao adicionar cliente. Por favor, tente novamente.', 'error')
            return redirect(url_for('novo_cliente'))
    
    return render_template('novo_cliente.html')

@app.route('/cliente/<int:cliente_id>')
@login_required
def cliente_detalhes(cliente_id):
    cliente = Cliente.query.get(cliente_id)
    
    if not cliente or cliente.usuario_id != current_user.id:
        flash('Cliente não encontrado.', 'error')
        return redirect(url_for('dashboard'))
    
    tarefas = Tarefa.query.filter_by(cliente_id=cliente_id).all()
    
    tarefas_formatadas = []
    for tarefa in tarefas:
        tarefa_dict = tarefa.__dict__
        if tarefa_dict.get('checklist'):
            try:
                checklist = json.loads(tarefa_dict['checklist'])
                total = len(checklist)
                completed = sum(1 for item in checklist if item.get('completed'))
                tarefa_dict['progresso'] = (completed / total * 100) if total > 0 else 0
            except:
                tarefa_dict['progresso'] = 0
        else:
            tarefa_dict['progresso'] = 0
        tarefas_formatadas.append(tarefa_dict)
    
    return render_template('cliente_detalhes.html',
                         cliente=cliente,
                         tarefas=tarefas_formatadas)

@app.route('/cliente/<int:cliente_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_cliente(cliente_id):
    cliente = Cliente.query.get(cliente_id)
    
    if not cliente or cliente.usuario_id != current_user.id:
        flash('Cliente não encontrado.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        website = request.form.get('website')
        descricao = request.form.get('descricao')
        
        if not nome:
            flash('O nome do cliente é obrigatório.', 'error')
            return redirect(url_for('editar_cliente', cliente_id=cliente_id))
        
        try:
            cliente.nome = nome
            cliente.website = website
            cliente.descricao = descricao
            db.session.commit()
            
            flash('Cliente atualizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao atualizar cliente: {str(e)}")
            flash('Erro ao atualizar cliente. Por favor, tente novamente.', 'error')
    
    return render_template('editar_cliente.html', cliente=cliente)

@app.route('/cliente/<int:cliente_id>/excluir', methods=['POST'])
@login_required
def excluir_cliente(cliente_id):
    cliente = Cliente.query.get(cliente_id)
    
    if not cliente or cliente.usuario_id != current_user.id:
        flash('Cliente não encontrado.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Primeiro excluir registros relacionados
        Tarefa.query.filter_by(cliente_id=cliente_id).delete()
        
        # Depois excluir o cliente
        db.session.delete(cliente)
        db.session.commit()
        
        flash('Cliente excluído com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao excluir cliente: {str(e)}")
        flash('Erro ao excluir cliente. Por favor, tente novamente.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/cliente/<int:cliente_id>/tarefas', methods=['POST'])
@login_required
def criar_tarefa(cliente_id):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Dados não fornecidos'}), 400
            
        titulo = data.get('titulo')
        descricao = data.get('descricao', '')
        tipo = data.get('tipo')
        
        if not titulo:
            return jsonify({'success': False, 'error': 'Título é obrigatório'}), 400
        
        # Verificar se o cliente pertence ao usuário
        cliente = Cliente.query.get(cliente_id)
        
        if not cliente or cliente.usuario_id != current_user.id:
            return jsonify({'success': False, 'error': 'Cliente não encontrado'}), 404
        
        # Inserir a tarefa
        tarefa = Tarefa(cliente_id=cliente_id, titulo=titulo, descricao=descricao, tipo=tipo)
        db.session.add(tarefa)
        db.session.commit()
        
        # Retornar a tarefa criada
        return jsonify({
            'success': True,
            'message': 'Tarefa criada com sucesso',
            'tarefa': tarefa.__dict__
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao criar tarefa: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro ao criar tarefa: {str(e)}'
        }), 500

@app.route('/cliente/<int:cliente_id>/tarefas/<int:tarefa_id>', methods=['PUT'])
@login_required
def atualizar_tarefa(cliente_id, tarefa_id):
    cliente = Cliente.query.get(cliente_id)
    
    if not cliente or cliente.usuario_id != current_user.id:
        abort(403)
    
    tarefa = Tarefa.query.get(tarefa_id)
    
    if not tarefa or tarefa.cliente_id != cliente_id:
        abort(404)
    
    data = request.get_json()
    if 'status' in data:
        tarefa.status = data['status']
        db.session.commit()
    
    return jsonify({'success': True, 'message': 'Tarefa atualizada com sucesso'})

@app.route('/cliente/<int:cliente_id>/tarefas/<int:tarefa_id>', methods=['DELETE'])
@login_required
def remover_tarefa(cliente_id, tarefa_id):
    cliente = Cliente.query.get(cliente_id)
    
    if not cliente or cliente.usuario_id != current_user.id:
        abort(403)
    
    tarefa = Tarefa.query.get(tarefa_id)
    
    if not tarefa or tarefa.cliente_id != cliente_id:
        abort(404)
    
    db.session.delete(tarefa)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Tarefa removida com sucesso'})

@app.route('/cliente/<int:cliente_id>/seo-roadmap')
@login_required
def seo_roadmap(cliente_id):
    cliente = Cliente.query.get(cliente_id)
    
    if not cliente or cliente.usuario_id != current_user.id:
        abort(404)
    
    # Buscar todas as etapas e seu progresso
    etapas = EtapaSEO.query.all()
    
    # Converter etapas para lista de dicionários
    etapas_dict = []
    for etapa in etapas:
        etapa_dict = etapa.__dict__
        tarefas = Tarefa.query.filter_by(etapa_seo_id=etapa.id, cliente_id=cliente_id).all()
        
        # Converter tarefas para lista de dicionários
        etapa_dict['tarefas'] = [tarefa.__dict__ for tarefa in tarefas]
        etapas_dict.append(etapa_dict)
    
    # Calcular progresso geral
    total_peso = sum(etapa['peso'] for etapa in etapas_dict)
    peso_concluido = sum(
        etapa['peso'] 
        for etapa in etapas_dict 
        if etapa['status'] == 'concluida'
    )
    
    progresso_geral = (peso_concluido / total_peso * 100) if total_peso > 0 else 0
    
    # Agrupar etapas por categoria
    etapas_por_categoria = {}
    for etapa in etapas_dict:
        categoria = etapa['categoria']
        if categoria not in etapas_por_categoria:
            etapas_por_categoria[categoria] = []
        etapas_por_categoria[categoria].append(etapa)
    
    return render_template(
        'seo_roadmap.html',
        cliente=cliente,
        etapas_por_categoria=etapas_por_categoria,
        progresso_geral=progresso_geral,
        membros=[]
    )

@app.route('/cliente/<int:cliente_id>/tarefas/atualizar', methods=['POST'])
@login_required
def atualizar_status_tarefa(cliente_id):
    try:
        data = request.get_json()
        tarefa_id = data.get('tarefa_id')
        status = data.get('status')
        
        if not tarefa_id or not status:
            return jsonify({'success': False, 'error': 'Dados incompletos'}), 400
            
        # Verificar se a tarefa pertence ao cliente
        tarefa = Tarefa.query.get(tarefa_id)
        
        if not tarefa or tarefa.cliente_id != cliente_id:
            return jsonify({'success': False, 'error': 'Tarefa não encontrada'}), 404
            
        # Atualizar status da tarefa
        tarefa.status = status
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao atualizar status da tarefa: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/cliente/<int:cliente_id>/seo-roadmap/atualizar', methods=['POST'])
@login_required
def atualizar_progresso_seo(cliente_id):
    cliente = Cliente.query.get(cliente_id)
    
    if not cliente or cliente.usuario_id != current_user.id:
        abort(404)
    
    data = request.get_json()
    etapa_id = data.get('etapa_id')
    status = data.get('status')
    observacoes = data.get('observacoes')
    
    try:
        # Verificar se já existe um progresso
        progresso = ProgressoSEO.query.filter_by(cliente_id=cliente_id, etapa_id=etapa_id).first()
        
        if progresso:
            # Atualizar progresso existente
            progresso.status = status
            progresso.observacoes = observacoes
            db.session.commit()
        else:
            # Criar novo progresso
            progresso = ProgressoSEO(cliente_id=cliente_id, etapa_id=etapa_id, status=status, observacoes=observacoes)
            db.session.add(progresso)
            db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao atualizar progresso SEO: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/cliente/<int:cliente_id>/seo-tecnico')
@login_required
def seo_tecnico_kanban(cliente_id):
    cliente = Cliente.query.get(cliente_id)
    
    if not cliente or cliente.usuario_id != current_user.id:
        flash('Cliente não encontrado', 'error')
        return redirect(url_for('dashboard'))

    # Verificar se existem tarefas
    count = Tarefa.query.filter_by(cliente_id=cliente_id).count()
    
    # Se não houver tarefas, criar tarefas padrão
    if count == 0:
        try:
            tarefa = Tarefa(cliente_id=cliente_id, titulo='Análise Técnica', descricao='Realizar análise técnica do site', status='todo', prioridade='high', checklist='[{"text": "Verificar velocidade", "completed": false}, {"text": "Analisar mobile", "completed": false}]')
            db.session.add(tarefa)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar tarefa padrão: {str(e)}")
            flash(f'Erro ao criar tarefa padrão: {str(e)}', 'error')
            return redirect(url_for('dashboard'))

    # Carregar todas as tarefas
    tasks = Tarefa.query.filter_by(cliente_id=cliente_id).order_by(Tarefa.status, Tarefa.prioridade, Tarefa.data_criacao.desc()).all()
    
    # Preparar listas para cada status
    todo = []
    doing = []
    done = []
    
    # Processar cada tarefa
    for task in tasks:
        task_dict = task.__dict__
        status = task_dict.get('status', 'todo')
        
        # Processar o checklist
        checklist_progress = 0
        checklist = task_dict.get('checklist')
        if checklist:
            try:
                import json
                checklist_data = json.loads(checklist)
                if isinstance(checklist_data, list):
                    total = len(checklist_data)
                    completed = sum(1 for item in checklist_data if isinstance(item, dict) and item.get('completed', False))
                    checklist_progress = (completed / total * 100) if total > 0 else 0
            except json.JSONDecodeError:
                checklist_progress = 0
        
        formatted_task = {
            'id': task_dict['id'],
            'title': str(task_dict['titulo']),
            'description': str(task_dict.get('descricao', '')),
            'priority': str(task_dict.get('prioridade', 'medium')),
            'status': str(status),
            'date': str(task_dict.get('data_criacao', '')),
            'priority_class': f"priority-{str(task_dict.get('prioridade', 'medium'))}",
            'checklist_progress': round(checklist_progress, 1)
        }
        
        if status == 'doing':
            doing.append(formatted_task)
        elif status == 'done':
            done.append(formatted_task)
        else:
            todo.append(formatted_task)
                    
    # Calcular progresso geral
    total_tasks = len(tasks)
    progress = round((len(done) / total_tasks * 100), 1) if total_tasks > 0 else 0

    return render_template('seo_tecnico_kanban.html',
                         cliente=dict(cliente),
                         todo_tasks=todo,
                         doing_tasks=doing,
                         done_tasks=done,
                         todo_count=len(todo),
                         doing_count=len(doing),
                         done_count=len(done),
                         progress=progress)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
