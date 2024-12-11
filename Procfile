release: python migrations/reset_database.py && python migrations/run_migrations.py && python migrations/force_add_documentacao_url.py && python init_seo_data.py
web: gunicorn --bind=0.0.0.0:$PORT app:app --timeout 120
