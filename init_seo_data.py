from app import app, db, SeoTecnicoCategoria, SeoTecnicoItem

def init_seo_data():
    with app.app_context():
        # Criar categorias
        categorias = [
            {
                'nome': 'Otimização On-page',
                'descricao': 'Elementos básicos de otimização na página',
                'itens': [
                    {
                        'nome': 'Meta Title',
                        'descricao': 'Verificar se todas as páginas têm títulos únicos e otimizados',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/appearance/title-link'
                    },
                    {
                        'nome': 'Meta Description',
                        'descricao': 'Verificar se todas as páginas têm descrições únicas e atraentes',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/appearance/snippet'
                    },
                    {
                        'nome': 'Heading Tags',
                        'descricao': 'Verificar estrutura de H1-H6 e uso de palavras-chave',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/guidelines/heading-tags'
                    }
                ]
            },
            {
                'nome': 'Performance',
                'descricao': 'Métricas de desempenho e velocidade',
                'itens': [
                    {
                        'nome': 'Core Web Vitals',
                        'descricao': 'Verificar LCP, FID e CLS',
                        'documentacao_url': 'https://web.dev/vitals/'
                    },
                    {
                        'nome': 'Mobile Speed',
                        'descricao': 'Testar velocidade em dispositivos móveis',
                        'documentacao_url': 'https://developers.google.com/speed/docs/insights/mobile'
                    },
                    {
                        'nome': 'Otimização de Imagens',
                        'descricao': 'Verificar compressão e formatos modernos',
                        'documentacao_url': 'https://web.dev/fast/#optimize-your-images'
                    }
                ]
            },
            {
                'nome': 'Conteúdo',
                'descricao': 'Análise e otimização de conteúdo',
                'itens': [
                    {
                        'nome': 'Palavras-chave',
                        'descricao': 'Verificar densidade e posicionamento',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/guidelines/irrelevant-keywords'
                    },
                    {
                        'nome': 'Links Internos',
                        'descricao': 'Analisar estrutura de links internos',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/guidelines/links-crawlable'
                    },
                    {
                        'nome': 'Conteúdo Duplicado',
                        'descricao': 'Identificar e corrigir conteúdo duplicado',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/guidelines/duplicate-content'
                    }
                ]
            },
            {
                'nome': 'Técnico',
                'descricao': 'Aspectos técnicos e infraestrutura',
                'itens': [
                    {
                        'nome': 'SSL/HTTPS',
                        'descricao': 'Verificar certificado e redirecionamentos',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/security/https'
                    },
                    {
                        'nome': 'Sitemap XML',
                        'descricao': 'Validar estrutura e submissão',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/sitemaps/overview'
                    },
                    {
                        'nome': 'Robots.txt',
                        'descricao': 'Verificar configurações de crawling',
                        'documentacao_url': 'https://developers.google.com/search/docs/advanced/robots/intro'
                    }
                ]
            }
        ]

        # Inserir categorias e itens
        for i, cat_data in enumerate(categorias, 1):
            categoria = SeoTecnicoCategoria.query.filter_by(nome=cat_data['nome']).first()
            if not categoria:
                categoria = SeoTecnicoCategoria(
                    nome=cat_data['nome'],
                    descricao=cat_data['descricao'],
                    ordem=i
                )
                db.session.add(categoria)
                db.session.flush()  # Para obter o ID da categoria

            # Inserir itens da categoria
            for j, item_data in enumerate(cat_data['itens'], 1):
                item = SeoTecnicoItem.query.filter_by(
                    categoria_id=categoria.id,
                    nome=item_data['nome']
                ).first()
                
                if not item:
                    item = SeoTecnicoItem(
                        categoria_id=categoria.id,
                        nome=item_data['nome'],
                        descricao=item_data['descricao'],
                        documentacao_url=item_data['documentacao_url'],
                        ordem=j
                    )
                    db.session.add(item)

        db.session.commit()
        print("Dados SEO inseridos com sucesso!")

if __name__ == '__main__':
    init_seo_data()
