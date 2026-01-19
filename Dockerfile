FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md uv.lock ./

RUN pip install --no-cache-dir uv==0.7.3 \
  && uv sync --system --frozen

COPY engine ./engine
COPY web ./web
COPY main.py ./

EXPOSE 8000

CMD ["python", "main.py"]
