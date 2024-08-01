FROM python:3.11

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./app /app

CMD ["python3", "-m", "debugpy", "--listen", "0.0.0.0:5858", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]