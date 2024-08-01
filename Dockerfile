FROM python:3.11

RUN pip3 install fastapi uvicorn debugpy

COPY ./app /app

CMD ["python3", "-m", "debugpy", "--listen", "0.0.0.0:5858", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]