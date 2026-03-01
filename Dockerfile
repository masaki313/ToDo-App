# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# 依存を先に入れる（キャッシュ効く）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリ本体
COPY . .

EXPOSE 7000

# 本番想定ならgunicorn推奨
CMD ["gunicorn", "-b", "0.0.0.0:7000", "app:app"]