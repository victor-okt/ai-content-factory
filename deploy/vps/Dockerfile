FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY deploy/vps/worker.py /app/worker.py
USER nobody
CMD ["python","/app/worker.py"]
