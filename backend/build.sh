#!/bin/bash
set -e
pip install -r requirements.txt
python manage.py collectstatic --noinput
<<<<<<< HEAD
python manage.py migrate --run-syncdb
=======
python manage.py migrate
>>>>>>> 6a4e5b39b9e9a60daa2fe6a8179104db3b7acdfd
python manage.py seed_data
