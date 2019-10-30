```sh
bwrap/postgres initdb -E UTF-8 --auth-host=reject --auth-local=trust --username=postgres data
```

```sh
bwrap/postgres postgres -D data -h '' -k ..
```

```
sqlalchemy.url = postgresql+psycopg2cffi://weasyl@/weasyl?host=/home/weasyl/weasyl/sandbox/postgres
```
