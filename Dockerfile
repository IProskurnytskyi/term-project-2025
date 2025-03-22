FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /home/app
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /home/app

COPY ./pyproject.toml ./

RUN pip install poetry
RUN poetry install --no-root

COPY . ./

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
