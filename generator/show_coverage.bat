coverage run --source='.' manage.py test generator account questions
coverage html
start "" "htmlcov/index.html"