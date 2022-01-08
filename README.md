# PZSP2

### Temat projektu:

- Generator testów

### Skład zespołu:

- Michał Bielecki
- Krzysztof Kania
- Ignacy Majkusiak
- Andrzej Sawicki
- Patryk Bandyra

### Przed pierwszym uruchomieniem

Należy:
- zainstalować za pomocą instalatora pakietów, np. pip, pakiety wymienione w pliku requirements.txt
- zainstalować na lokalnej maszynie bazę danych PostgreSQL
- ustawić:
    - nasłuch bazy danych na porcie 5432
    - hasło administratora bazy danych na: postgres
- zainstalować rozszerzenie do bazy danych o nazwie: pg_trgm
- uruchomić bazę danych
- przejść do katalogu domowego projektu i uruchomić polecenie:
```batch
python3 ./generator/manage.py migrate
```

### Uruchomienie:

W celu uruchomienia aplikacji należy:
- przejść do katalogu domowego projektu i uruchomić polecenie:
```batch
python3 ./generator/manage.py runserver
```
- uruchomić przeglądarkę internetową i przejść pod adres http://localhost:8000/
