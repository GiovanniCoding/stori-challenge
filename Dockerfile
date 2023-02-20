FROM python:3.8.16-slim
WORKDIR /app
COPY . .
RUN apt update &\
    apt install libpq-dev python3-dev&\
    pip install -r requirements.txt
CMD ["python", "main.py"]