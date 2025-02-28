FROM python:3.13-slim

WORKDIR /app

COPY app/ /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8677

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8677"]
