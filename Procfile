release: python migrations/run_migrations.py && python migrations/add_documentacao_url_column.py && python init_seo_data.py
web: gunicorn --bind=0.0.0.0:$PORT app:app --timeout 120
