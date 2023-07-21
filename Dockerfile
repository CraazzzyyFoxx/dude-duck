FROM python:3.11

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y sqlite3 libsqlite3-dev

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH "$PATH:/root/.local/bin"

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false
RUN poetry install -n --only main

COPY . ./
CMD ["poetry", "shell"]
CMD ["aerich", "init-db"]
CMD ["aerich", "upgrade"]
CMD ["poetry", "exit"]
CMD ["python3.11", "-O", "starter.py", "run"]