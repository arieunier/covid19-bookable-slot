
web: export PYTHONPATH=.:./libs:./appsrc; env;  gunicorn --workers=4 run:app
release: export PYTHONPATH=.:./libs:./appsrc; python db_migrate.py db migrate; python db_migrate.py db upgrade

