from app import app, db
from models import SeoTecnicoCategoria, SeoTecnicoItem

def init_seo_data():
    with app.app_context():
        # Recriar as tabelas
        db.drop_all()
        db.create_all()
        
        # Criar categorias
        categorias = [
            {
                'nome': 'Otimização On-page',
                'descricao': 'Elementos básicos de otimização na página',
                'ordem': 1,
                'itens': [
                    {
                        'nome': 'Meta Title',
                        'descricao': 'Verificar se todas as páginas têm títulos únicos e otimizados',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/appearance/title-link',
                        'ordem': 1
                    },
                    {
                        'nome': 'Meta Description',
                        'descricao': 'Verificar se todas as páginas têm descrições únicas e atraentes',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/appearance/snippet',
                        'ordem': 2
                    },
                    {
                        'nome': 'Heading Tags',
                        'descricao': 'Verificar estrutura de H1-H6 e uso de palavras-chave',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/guidelines/heading-tags',
                        'ordem': 3
                    }
                ]
            },
            {
                'nome': 'Performance',
                'descricao': 'Métricas de desempenho e velocidade',
                'ordem': 2,
                'itens': [
                    {
                        'nome': 'Core Web Vitals',
                        'descricao': 'Verificar LCP, FID e CLS',
                        'documentacao_url': 'https://web.dev/vitals/',
                        'ordem': 1
                    },
                    {
                        'nome': 'Mobile Speed',
                        'descricao': 'Testar velocidade em dispositivos móveis',
                        'documentacao_url': 'https://developers.google.com/speed/docs/insights/mobile',
                        'ordem': 2
                    },
                    {
                        'nome': 'Otimização de Imagens',
                        'descricao': 'Verificar compressão e formatos modernos',
                        'documentacao_url': 'https://web.dev/fast/#optimize-your-images',
                        'ordem': 3
                    }
                ]
            },
            {
                'nome': 'Conteúdo',
                'descricao': 'Análise e otimização de conteúdo',
                'ordem': 3,
                'itens': [
                    {
                        'nome': 'Palavras-chave',
                        'descricao': 'Verificar densidade e posicionamento de palavras-chave',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/guidelines/keyword-placement',
                        'ordem': 1
                    },
                    {
                        'nome': 'Estrutura de Conteúdo',
                        'descricao': 'Analisar hierarquia e organização do conteúdo',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/guidelines/content-structure',
                        'ordem': 2
                    },
                    {
                        'nome': 'Links Internos',
                        'descricao': 'Verificar estratégia de linking interno',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/guidelines/internal-links',
                        'ordem': 3
                    }
                ]
            },
            {
                'nome': 'Técnico',
                'descricao': 'Aspectos técnicos e estruturais',
                'ordem': 4,
                'itens': [
                    {
                        'nome': 'Robots.txt',
                        'descricao': 'Verificar configurações de crawling',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/robots/intro',
                        'ordem': 1
                    },
                    {
                        'nome': 'Sitemap XML',
                        'descricao': 'Verificar estrutura e atualização do sitemap',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/sitemaps/overview',
                        'ordem': 2
                    },
                    {
                        'nome': 'Schema Markup',
                        'descricao': 'Implementar dados estruturados relevantes',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/structured-data/intro-structured-data',
                        'ordem': 3
                    }
                ]
            }
        ]
        
        # Inserir categorias e itens
        for categoria_data in categorias:
            itens = categoria_data.pop('itens')
            categoria = SeoTecnicoCategoria(**categoria_data)
            db.session.add(categoria)
            db.session.flush()  # Para obter o ID da categoria
            
            for item_data in itens:
                item = SeoTecnicoItem(categoria_id=categoria.id, **item_data)
                db.session.add(item)
        
        db.session.commit()
        print("Dados SEO inicializados com sucesso!")

if __name__ == '__main__':
    init_seo_data()
