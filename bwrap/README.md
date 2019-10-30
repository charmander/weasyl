```sh
bwrap/postgres initdb -E UTF-8 --auth-host=reject --auth-local=trust --username=postgres data
```

```sh
bwrap/postgres postgres -D data -h '' -k ..
```

```
sqlalchemy.url = postgresql+psycopg2cffi://weasyl@/weasyl?host=/home/weasyl/weasyl/sandbox/postgres
```

```sh
bwrap/postgres createuser -U postgres weasyl
bwrap/postgres createdb -U postgres -O weasyl weasyl
bwrap/postgres psql -U postgres -d weasyl -c 'CREATE EXTENSION hstore'
bwrap/postgres psql -U postgres -d weasyl -c 'CREATE EXTENSION fuzzystrmatch'
< weasyl-latest-staff.sql.xz unxz | bwrap/postgres psql
bwrap/alembic -c libweasyl/alembic.ini upgrade head
```

```sh
bwrap/pip install -r etc/requirements.txt -e . -e ./libweasyl --index-url https://pypi.weasyl.dev/ --extra-index-url https://pypi.org/simple/
```
