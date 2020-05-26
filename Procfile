web: export PYTHONPATH=.:./libs:./app; env;  gunicorn --workers=4 run:app
release: export PYTHONPATH=.:./libs:./app ; python /app/manage.py db migrate;  python /app/manage.py db upgrade