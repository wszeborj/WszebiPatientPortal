FROM python:3.12.8-slim-bullseye

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV POETRY_VIRTUALENVS_CREATE=0

RUN pip install poetry==1.8.4

COPY poetry.lock pyproject.toml README.md ./

RUN poetry check
RUN poetry install --no-interaction --no-cache

#COPY ./compose/local/django/entrypoint /entrypoint
RUN #sed -i 's/\r$//g' /entrypoint
RUN #chmod +x /entrypoint

COPY ./.docker/compose/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY ./.docker/compose/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./.docker/compose/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat

COPY ./.docker/compose/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower

COPY . .

#ENTRYPOINT ["/entrypoint"]

WORKDIR /app

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
