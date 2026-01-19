FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md uv.lock ./
COPY engine ./engine
COPY web ./web
COPY main.py ./

RUN pip install --no-cache-dir uv==0.7.3 \
  && uv venv /opt/venv

ENV VIRTUAL_ENV=/opt/venv
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN uv sync --frozen

EXPOSE 8000

CMD ["python", "main.py", "serve", "--host", "0.0.0.0", "--port", "8000"]
