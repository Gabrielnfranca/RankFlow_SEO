from flask import Flask, render_template, request, redirect, url_for, flash, g
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'

# Configuração do LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configuração do banco de dados
DATABASE = 'rankflow.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        # Criar tabela usuario
        db.execute('DROP TABLE IF EXISTS usuario')
        db.execute('''
            CREATE TABLE usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                nome TEXT NOT NULL
            )
        ''')
        
        # Criar tabela cliente
        db.execute('DROP TABLE IF EXISTS cliente')
        db.execute('''
            CREATE TABLE cliente (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                website TEXT,
                descricao TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usuario_id INTEGER NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuario (id)
            )
        ''')
        
        # Criar tabela tarefa
        db.execute('DROP TABLE IF EXISTS tarefa')
        db.execute('''
            CREATE TABLE tarefa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                titulo TEXT NOT NULL,
                descricao TEXT,
                status TEXT NOT NULL DEFAULT 'todo',
                prioridade TEXT NOT NULL DEFAULT 'medium',
                checklist TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES cliente (id)
            )
        ''')
        
        # Criar usuário admin
        senha_hash = generate_password_hash('admin123')
        db.execute('INSERT INTO usuario (email, senha, nome) VALUES (?, ?, ?)',
                  ('admin@rankflow.com', senha_hash, 'Administrador'))
        db.commit()

class Usuario(UserMixin):
    def __init__(self, id, email, nome):
        self.id = id
        self.email = email
        self.nome = nome

    def get_id(self):
        return str(self.id)

    @staticmethod
    def get(user_id):
        db = get_db()
        user = db.execute('SELECT * FROM usuario WHERE id = ?', (user_id,)).fetchone()
        if user:
            return Usuario(user['id'], user['email'], user['nome'])
        return None

@login_manager.user_loader
def load_user(user_id):
    return Usuario.get(user_id)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        if not email or not senha:
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('login.html')
        
        db = get_db()
        user = db.execute('SELECT * FROM usuario WHERE email = ?', (email,)).fetchone()
        
        if user and check_password_hash(user['senha'], senha):
            usuario = Usuario(user['id'], user['email'], user['nome'])
            login_user(usuario)
            return redirect(url_for('dashboard'))
        
        flash('Email ou senha incorretos.', 'error')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        db = get_db()
        clientes = db.execute('''
            SELECT 
                c.id,
                c.nome,
                c.website,
                c.descricao,
                c.data_criacao,
                COUNT(DISTINCT t.id) as total_tarefas,
                COUNT(DISTINCT CASE WHEN t.status = 'done' THEN t.id END) as tarefas_concluidas
            FROM cliente c
            LEFT JOIN tarefa t ON t.cliente_id = c.id
            WHERE c.usuario_id = ?
            GROUP BY c.id, c.nome, c.website, c.descricao, c.data_criacao
            ORDER BY c.data_criacao DESC
        ''', (current_user.id,)).fetchall()
        
        return render_template('dashboard.html', 
                            clientes=[dict(row) for row in clientes],
                            total_clientes=len(clientes))
    except Exception as e:
        print(f"Erro no dashboard: {str(e)}")
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
        
        db = get_db()
        if db.execute('SELECT id FROM usuario WHERE email = ?', (email,)).fetchone():
            flash('Email já cadastrado.', 'error')
            return redirect(url_for('cadastro'))
        
        hash_senha = generate_password_hash(senha)
        db.execute('INSERT INTO usuario (email, senha, nome) VALUES (?, ?, ?)',
                  (email, hash_senha, nome))
        db.commit()
        
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
            db = get_db()
            cursor = db.execute('''
                INSERT INTO cliente (nome, website, descricao, usuario_id)
                VALUES (?, ?, ?, ?)
            ''', (nome, website, descricao, current_user.id))
            
            cliente_id = cursor.lastrowid
            db.commit()
            
            flash('Cliente adicionado com sucesso!', 'success')
            return redirect(url_for('cliente_detalhes', cliente_id=cliente_id))
            
        except Exception as e:
            print(f"Erro ao criar cliente: {str(e)}")
            db.rollback()
            flash('Erro ao adicionar cliente. Por favor, tente novamente.', 'error')
            return redirect(url_for('novo_cliente'))
    
    return render_template('novo_cliente.html')

@app.route('/cliente/<int:cliente_id>')
@login_required
def cliente_detalhes(cliente_id):
    db = get_db()
    cliente = db.execute('''
        SELECT c.*, 
               COUNT(DISTINCT t.id) as total_tarefas,
               COUNT(DISTINCT CASE WHEN t.status = 'done' THEN t.id END) as tarefas_concluidas
        FROM cliente c
        LEFT JOIN tarefa t ON t.cliente_id = c.id
        WHERE c.id = ? AND c.usuario_id = ?
        GROUP BY c.id
    ''', (cliente_id, current_user.id)).fetchone()
    
    if cliente is None:
        flash('Cliente não encontrado.', 'error')
        return redirect(url_for('dashboard'))
    
    tarefas = db.execute('''
        SELECT * FROM tarefa 
        WHERE cliente_id = ?
        ORDER BY data_criacao DESC
    ''', (cliente_id,)).fetchall()
    
    tarefas_formatadas = []
    for tarefa in tarefas:
        tarefa_dict = dict(tarefa)
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
                         cliente=dict(cliente),
                         tarefas=tarefas_formatadas)

@app.route('/cliente/<int:cliente_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_cliente(cliente_id):
    db = get_db()
    cliente = db.execute('''
        SELECT * FROM cliente 
        WHERE id = ? AND usuario_id = ?
    ''', (cliente_id, current_user.id)).fetchone()
    
    if not cliente:
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
            db.execute('''
                UPDATE cliente 
                SET nome = ?, website = ?, descricao = ?
                WHERE id = ? AND usuario_id = ?
            ''', (nome, website, descricao, cliente_id, current_user.id))
            db.commit()
            
            flash('Cliente atualizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.rollback()
            flash('Erro ao atualizar cliente. Por favor, tente novamente.', 'error')
    
    return render_template('editar_cliente.html', cliente=cliente)

@app.route('/cliente/<int:cliente_id>/excluir', methods=['POST'])
@login_required
def excluir_cliente(cliente_id):
    db = get_db()
    cliente = db.execute('''
        SELECT * FROM cliente 
        WHERE id = ? AND usuario_id = ?
    ''', (cliente_id, current_user.id)).fetchone()
    
    if not cliente:
        flash('Cliente não encontrado.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Primeiro excluir registros relacionados
        db.execute('DELETE FROM tarefa WHERE cliente_id = ?', (cliente_id,))
        
        # Depois excluir o cliente
        db.execute('DELETE FROM cliente WHERE id = ? AND usuario_id = ?', 
                  (cliente_id, current_user.id))
        db.commit()
        
        flash('Cliente excluído com sucesso!', 'success')
        
    except Exception as e:
        db.rollback()
        flash('Erro ao excluir cliente. Por favor, tente novamente.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/cliente/<int:cliente_id>/tarefas', methods=['POST'])
@login_required
def criar_tarefa(cliente_id):
    try:
        db = get_db()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Dados não fornecidos'}), 400
            
        titulo = data.get('titulo')
        descricao = data.get('descricao', '')
        tipo = data.get('tipo')
        
        if not titulo:
            return jsonify({'success': False, 'error': 'Título é obrigatório'}), 400
        
        # Verificar se o cliente pertence ao usuário
        cliente = db.execute('''
            SELECT id FROM cliente 
            WHERE id = ? AND usuario_id = ?
        ''', (cliente_id, current_user.id)).fetchone()
        
        if not cliente:
            return jsonify({'success': False, 'error': 'Cliente não encontrado'}), 404
        
        # Inserir a tarefa
        cursor = db.execute('''
            INSERT INTO tarefa (
                cliente_id, titulo, descricao, tipo, status
            )
            VALUES (?, ?, ?, ?, 'pendente')
        ''', (cliente_id, titulo, descricao, tipo))
        
        db.commit()
        
        # Retornar a tarefa criada
        tarefa_id = cursor.lastrowid
        tarefa = db.execute('''
            SELECT *
            FROM tarefa
            WHERE id = ?
        ''', (tarefa_id,)).fetchone()
        
        return jsonify({
            'success': True,
            'message': 'Tarefa criada com sucesso',
            'tarefa': dict(tarefa)
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({
            'success': False,
            'error': f'Erro ao criar tarefa: {str(e)}'
        }), 500

@app.route('/cliente/<int:cliente_id>/tarefas/<int:tarefa_id>', methods=['PUT'])
@login_required
def atualizar_tarefa(cliente_id, tarefa_id):
    db = get_db()
    cliente = db.execute('SELECT * FROM cliente WHERE id = ? AND usuario_id = ?', 
                        (cliente_id, current_user.id)).fetchone()
    if not cliente:
        abort(403)
    
    tarefa = db.execute('SELECT * FROM tarefa WHERE id = ? AND cliente_id = ?', 
                       (tarefa_id, cliente_id)).fetchone()
    if not tarefa:
        abort(404)
    
    data = request.get_json()
    if 'status' in data:
        db.execute('''
            UPDATE tarefa 
            SET status = ?,
                data_conclusao = CASE WHEN ? = 'concluida' THEN CURRENT_TIMESTAMP ELSE NULL END
            WHERE id = ?
        ''', (data['status'], data['status'], tarefa_id))
        db.commit()
    
    return jsonify({'success': True, 'message': 'Tarefa atualizada com sucesso'})

@app.route('/cliente/<int:cliente_id>/tarefas/<int:tarefa_id>', methods=['DELETE'])
@login_required
def remover_tarefa(cliente_id, tarefa_id):
    db = get_db()
    cliente = db.execute('SELECT * FROM cliente WHERE id = ? AND usuario_id = ?', 
                        (cliente_id, current_user.id)).fetchone()
    if not cliente:
        abort(403)
    
    tarefa = db.execute('SELECT * FROM tarefa WHERE id = ? AND cliente_id = ?', 
                       (tarefa_id, cliente_id)).fetchone()
    if not tarefa:
        abort(404)
    
    db.execute('DELETE FROM tarefa WHERE id = ?', (tarefa_id,))
    db.commit()
    
    return jsonify({'success': True, 'message': 'Tarefa removida com sucesso'})

@app.route('/cliente/<int:cliente_id>/seo-roadmap')
@login_required
def seo_roadmap(cliente_id):
    db = get_db()
    cliente = db.execute('''
        SELECT * FROM cliente 
        WHERE id = ? AND usuario_id = ?
    ''', (cliente_id, current_user.id)).fetchone()
    
    if not cliente:
        abort(404)
    
    # Buscar todas as etapas e seu progresso
    etapas = db.execute('''
        SELECT 
            e.*,
            p.status,
            p.data_conclusao,
            p.observacoes,
            COUNT(t.id) as total_tarefas,
            SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) as tarefas_concluidas
        FROM etapa_seo e
        LEFT JOIN progresso_seo p ON p.etapa_id = e.id AND p.cliente_id = ?
        LEFT JOIN tarefa t ON t.etapa_seo_id = e.id AND t.cliente_id = ?
        GROUP BY e.id
        ORDER BY e.ordem
    ''', (cliente_id, cliente_id)).fetchall()
    
    # Converter etapas para lista de dicionários
    etapas_dict = []
    for etapa in etapas:
        etapa_dict = dict(etapa)
        tarefas = db.execute('''
            SELECT t.*
            FROM tarefa t
            WHERE t.etapa_seo_id = ? AND t.cliente_id = ?
            ORDER BY t.data_criacao DESC
        ''', (etapa['id'], cliente_id)).fetchall()
        
        # Converter tarefas para lista de dicionários
        etapa_dict['tarefas'] = [dict(tarefa) for tarefa in tarefas]
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
        db = get_db()
        data = request.get_json()
        tarefa_id = data.get('tarefa_id')
        status = data.get('status')
        
        if not tarefa_id or not status:
            return jsonify({'success': False, 'error': 'Dados incompletos'}), 400
            
        # Verificar se a tarefa pertence ao cliente
        tarefa = db.execute('''
            SELECT * FROM tarefa
            WHERE id = ? AND cliente_id = ?
        ''', (tarefa_id, cliente_id)).fetchone()
        
        if not tarefa:
            return jsonify({'success': False, 'error': 'Tarefa não encontrada'}), 404
            
        # Atualizar status da tarefa
        db.execute('''
            UPDATE tarefa
            SET status = ?,
                data_conclusao = CASE WHEN ? = 'concluida' THEN CURRENT_TIMESTAMP ELSE NULL END
            WHERE id = ?
        ''', (status, status, tarefa_id))
        
        db.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/cliente/<int:cliente_id>/seo-roadmap/atualizar', methods=['POST'])
@login_required
def atualizar_progresso_seo(cliente_id):
    db = get_db()
    cliente = db.execute('''
        SELECT * FROM cliente 
        WHERE id = ? AND usuario_id = ?
    ''', (cliente_id, current_user.id)).fetchone()
    
    if not cliente:
        abort(404)
    
    data = request.get_json()
    etapa_id = data.get('etapa_id')
    status = data.get('status')
    observacoes = data.get('observacoes')
    
    try:
        # Verificar se já existe um progresso
        progresso = db.execute('''
            SELECT id FROM progresso_seo
            WHERE cliente_id = ? AND etapa_id = ?
        ''', (cliente_id, etapa_id)).fetchone()
        
        if progresso:
            # Atualizar progresso existente
            db.execute('''
                UPDATE progresso_seo
                SET status = ?,
                    data_conclusao = CASE WHEN ? = 'concluida' THEN CURRENT_TIMESTAMP ELSE NULL END,
                    observacoes = ?
                WHERE cliente_id = ? AND etapa_id = ?
            ''', (status, status, observacoes, cliente_id, etapa_id))
        else:
            # Criar novo progresso
            db.execute('''
                INSERT INTO progresso_seo (cliente_id, etapa_id, status, data_conclusao, observacoes)
                VALUES (?, ?, ?, 
                    CASE WHEN ? = 'concluida' THEN CURRENT_TIMESTAMP ELSE NULL END,
                    ?
                )
            ''', (cliente_id, etapa_id, status, status, observacoes))
        
        db.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/cliente/<int:cliente_id>/seo-tecnico')
@login_required
def seo_tecnico_kanban(cliente_id):
    db = get_db()
    try:
        print(f"Iniciando seo_tecnico_kanban para cliente_id: {cliente_id}")
        
        # Verificar se o cliente existe e pertence ao usuário atual
        cliente = db.execute('''
            SELECT c.* 
            FROM cliente c 
            WHERE c.id = ? AND c.usuario_id = ?
        ''', (cliente_id, current_user.id)).fetchone()
        
        if not cliente:
            print("Cliente não encontrado")
            flash('Cliente não encontrado', 'error')
            return redirect(url_for('dashboard'))

        print("Cliente encontrado:", dict(cliente))

        # Verificar se existem tarefas
        count = db.execute('SELECT COUNT(*) as count FROM tarefa WHERE cliente_id = ?', 
                         (cliente_id,)).fetchone()['count']
        
        print(f"Número de tarefas encontradas: {count}")

        # Se não houver tarefas, criar tarefas padrão
        if count == 0:
            print("Criando tarefa padrão...")
            try:
                db.execute('''
                    INSERT INTO tarefa (cliente_id, titulo, descricao, status, prioridade, checklist)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    cliente_id,
                    'Análise Técnica',
                    'Realizar análise técnica do site',
                    'todo',
                    'high',
                    '[{"text": "Verificar velocidade", "completed": false}, {"text": "Analisar mobile", "completed": false}]'
                ))
                db.commit()
                print("Tarefa padrão criada com sucesso")
            except Exception as e:
                db.rollback()
                print(f"Erro ao criar tarefa padrão: {str(e)}")
                print(f"Tipo do erro: {type(e)}")
                import traceback
                print("Traceback completo:")
                print(traceback.format_exc())
                raise Exception(f"Erro ao criar tarefa padrão: {str(e)}")

        # Carregar todas as tarefas
        print("Carregando tarefas...")
        tasks = db.execute('''
            SELECT id, titulo, descricao, status, prioridade, data_criacao, checklist
            FROM tarefa 
            WHERE cliente_id = ?
            ORDER BY 
                CASE status 
                    WHEN 'todo' THEN 1 
                    WHEN 'doing' THEN 2 
                    WHEN 'done' THEN 3 
                END,
                CASE prioridade
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                END,
                data_criacao DESC
        ''', (cliente_id,)).fetchall()
        
        print(f"Número de tarefas carregadas: {len(tasks)}")

        # Preparar listas para cada status
        todo = []
        doing = []
        done = []
        
        # Processar cada tarefa
        for task in tasks:
            try:
                task_dict = dict(task)
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
                    
            except Exception as task_error:
                print(f"Erro ao processar tarefa: {str(task_error)}")
                continue

        # Calcular progresso geral
        total_tasks = len(tasks)
        progress = round((len(done) / total_tasks * 100), 1) if total_tasks > 0 else 0

        print("Renderizando template...")
        return render_template('seo_tecnico_kanban.html',
                             cliente=dict(cliente),
                             todo_tasks=todo,
                             doing_tasks=doing,
                             done_tasks=done,
                             todo_count=len(todo),
                             doing_count=len(doing),
                             done_count=len(done),
                             progress=progress)

    except Exception as e:
        print(f"Erro geral: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        import traceback
        print("Traceback completo:")
        print(traceback.format_exc())
        flash(f'Erro ao carregar o kanban: {type(e).__name__} - {str(e)}', 'error')
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    # Inicializar o banco de dados
    init_db()
    app.run(debug=True, port=5000)
