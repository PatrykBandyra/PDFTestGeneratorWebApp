# PZSP2

### Temat projektu:

- Generator testów

### Skład zespołu:

- Michał Bielecki
- Krzysztof Kania
- Ignacy Majkusiak
- Andrzej Sawicki
- Patryk Bandyra

### Instalacja

Należy:
- zainstalować pakiety
```batch
sudo apt install python3 python3-pip postgresql texlive texlive-latex-extra texlive-fonts-recommended dvipng cm-super
```
- zainstalować za pomocą instalatora pakietów, np. pip, pakiety wymienione w pliku requirements.txt
```batch
pip install -r requirements.txt
```
- zainstalować na lokalnej maszynie bazę danych PostgreSQL
```batch
sudo apt install postgresql postgresql-contrib
```
- utworzyć bazę danych, użytkownika oraz uprawnienia
```batch
sudo -u postgres psql -c "CREATE DATABASE testgenerator"
sudo -u postgres psql -c "CREATE USER testgenerator WITH PASSWORD 'testgenerator';"
sudo -u postgres psql -c "ALTER USER testgenerator CREATEDB;"
sudo -u postgres psql -c "ALTER ROLE testgenerator SUPERUSER;"
``` 
- zainstalować rozszerzenie do bazy danych o nazwie *pg_trgm*
```batch
sudo -u postgres psql testgenerator -c "CREATE EXTENSION pg_trgm"
``` 
- pobrać, dostosować plik *config.json* oraz umieścić go w lokalizacji *generator/* oraz *generator/generator/*
- zmigrować bazę danych za pomocą skryptu:
```batch
python3 generator/manage.py migrate
```
- zebrać wszystkie statyczne pliki do jednej lokalizacji
```batch
python3 generator/manage.py collectstatic
```

*Polecenia dostosowane do systemu Ubuntu 20.04 LTS*

### Uruchomienie:

Należy:
- uruchomić lokalną usługę za pomocą skryptu:
```batch
python3 generator/manage.py runserver
```
- uruchomić przeglądarkę internetową i przejść pod adres http://127.0.0.1:8000/
```batch
firefox -new-tab "http://127.0.0.1:8000/"
```

*Polecenia dostosowane do systemu Ubuntu 20.04 LTS*

### Testowanie:
Należy:
- uruchomić wykonywanie testów:
```batch
coverage run --source='.' --omit='*.tests.py' generator/manage.py test generator account questions quiz
```
- wygenerować rezultaty:
```batch
coverage html
```
- uruchomić przeglądarkę internetową i otworzyć plik htmlcov/index.html
```batch
firefox -new-tab "htmlcov/index.html"
```

*Polecenia dostosowane do systemu Ubuntu 20.04 LTS*
