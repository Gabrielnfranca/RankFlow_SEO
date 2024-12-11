release: psql $DATABASE_URL -f migrations/full_database_reset.sql && python migrations/run_migrations.py && python init_seo_data.py
web: gunicorn --bind=0.0.0.0:$PORT app:app --timeout 120
