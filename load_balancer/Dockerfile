FROM python:3.9

WORKDIR /app
COPY . .
RUN apt update && \
    apt install -y jq curl && \
    curl -L https://fly.io/install.sh | sh && \
    pip install --no-cache-dir --upgrade -r ./requirements.txt
ENV PATH="/root/.fly/bin:${PATH}"
CMD ["uvicorn", "balance_server:app", "--host", "0.0.0.0", "--port", "5000"]