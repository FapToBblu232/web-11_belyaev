
```bash
python3 -m venv .venv
source .venv/bin/activate
```


```bash
pip install -r requirements.txt
```

БД я создавал вот такой командой
```bash
docker run --name my_postgres -p 5555:5432 -e POSTGRES_PASSWORD=asdfq1w2 -e POSTGRES_USER=my_user -e POSTGRES_DB=questions -d postgres
```

```bash
export POSTGRES_USER=my_user
export POSTGRES_PASSWORD=asdfq1w2
export POSTGRES_DB=questions
export POSTGRES_PORT=5555
```

```bash
python manage.py migrate
```

```bash
python manage.py runserver 7777
```

```bash
python manage.py createsuperuser
```

Создание пользователей, вопросов, ответов на них и реакций на каждую из этих штук)
```bash
python manage.py fill_db --ratio <число из условия дз>
```

Создание для ratio=1000 занимает у меня 163 секунды, т.к. создаётся 100_000 ответов, у каждого из которых есть лайки/дизлайки + я попытался денормолизовать

