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
- zainstalować za pomocą instalatora pakietów, np. pip, pakiety wymienione w pliku requirements.txt
```batch
pip install -r requirements.txt
```
- zainstalować na lokalnej maszynie bazę danych PostgreSQL
```batch
sudo apt install postgresql postgresql-contrib
```
- utworzyć bazę danych oraz użytkownika
```batch
sudo -u postgres psql -c "CREATE DATABASE testgenerator"
sudo -u postgres psql -c "CREATE USER testgenerator WITH PASSWORD 'testgenerator';"
``` 
- zainstalować rozszerzenie do bazy danych o nazwie *pg_trgm*
```batch
sudo -u postgres psql postgres -c "CREATE EXTENSION pg_trgm"
``` 
- zmigrować bazę danych za pomocą skryptu:
```batch
python3 generator/manage.py migrate
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