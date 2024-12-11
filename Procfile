release: python migrations/run_migrations.py && python init_seo_data.py
web: python migrations/run_migrations.py && python init_seo_data.py && gunicorn app:app
