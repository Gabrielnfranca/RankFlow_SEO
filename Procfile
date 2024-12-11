release: python render_deploy_check.py && psql $DATABASE_URL -f migrations/clear_users.sql && python migrations/run_migrations.py && python init_seo_data.py
web: gunicorn --bind=0.0.0.0:$PORT app:app --timeout 120
