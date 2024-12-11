import os
import logging
from app import app, db
from models import Usuario, Cliente, SeoTecnicoStatus, SeoTecnicoItem, SeoTecnicoCategoria
from werkzeug.security import generate_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_database():
    with app.app_context():
        try:
            # Excluir todos os dados existentes
            SeoTecnicoStatus.query.delete()
            SeoTecnicoItem.query.delete()
            SeoTecnicoCategoria.query.delete()
            Cliente.query.delete()
            Usuario.query.delete()
            
            # Criar usuário de teste
            usuario_teste = Usuario(
                nome='Usuário Teste',
                email='teste@rankflow.com.br',
                senha=generate_password_hash('teste123')
            )
            db.session.add(usuario_teste)
            db.session.flush()  # Gerar ID para o usuário
            
            # Criar cliente de teste
            cliente_teste = Cliente(
                nome='Cliente Exemplo',
                website='https://webone.com.br',
                usuario_id=usuario_teste.id
            )
            db.session.add(cliente_teste)
            
            # Criar categorias de SEO
            categorias = [
                SeoTecnicoCategoria(
                    nome='Análise Técnica Inicial', 
                    descricao='Verificações técnicas básicas e essenciais',
                    ordem=1
                ),
                SeoTecnicoCategoria(
                    nome='Performance do Site', 
                    descricao='Análise e otimização de desempenho',
                    ordem=2
                )
            ]
            db.session.add_all(categorias)
            db.session.flush()
            
            # Criar itens de SEO
            itens = [
                SeoTecnicoItem(
                    categoria_id=categorias[0].id,
                    nome='Verificação de robots.txt', 
                    descricao='Verificar configuração e regras do robots.txt',
                    documentacao_url='https://developers.google.com/search/docs/advanced/robots/intro',
                    ordem=1
                ),
                SeoTecnicoItem(
                    categoria_id=categorias[0].id,
                    nome='Análise do sitemap.xml', 
                    descricao='Verificar estrutura e URLs no sitemap',
                    documentacao_url='https://developers.google.com/search/docs/advanced/sitemaps/overview',
                    ordem=2
                )
            ]
            db.session.add_all(itens)
            
            # Commit das alterações
            db.session.commit()
            
            logger.info("Banco de dados resetado com sucesso!")
            logger.info(f"Usuário criado - Email: teste@rankflow.com.br")
            logger.info(f"Cliente criado - Nome: Cliente Exemplo")
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao resetar banco de dados: {e}")
            raise

if __name__ == "__main__":
    reset_database()
