web: export PYTHONPATH=.:./libs:./app; env;  gunicorn --workers=4 run:app
release: export PYTHONPATH=.:./libs:./app; python db_migrate.py db migrate; python db_migrate.py db upgrade