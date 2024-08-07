ARG BASE_IMAGE=nvcr.io/nvidia/tensorrt
ARG BASE_TAG=24.02-py3

FROM ${BASE_IMAGE}:${BASE_TAG} as trt_bark
LABEL authors="ginger"

WORKDIR /app

COPY TRT_Bark .

# Combine creation of models directory with subsequent commands
RUN mkdir models && \
    cat /etc/resolv.conf && \
    pip install nvidia-pyindex && \
    pip install -r requirements.txt --no-cache && \
    pip install git+https://github.com/suno-ai/bark --no-cache
RUN python3 download_bark.py && \
    python3 bark_large.py && \
    python3 bark_coarse.py && \
    python3 bark_fine.py && \
    rm -r models/bark_large/ONNX && \
    rm -r models/bark_coarse/ONNX

FROM ${BASE_IMAGE}:${BASE_TAG} as fastapi_bark
LABEL authors="ginger"

WORKDIR /app

COPY OptimizedBark .

COPY --from=trt_bark /app/models models
RUN pip install nvidia-pyindex && \
    pip install -r requirements.txt --no-cache && \
    python3 -c "import nltk;nltk.download('punkt')" && \
    python3 -c "from vocos import Vocos;Vocos.from_pretrained('charactr/vocos-encodec-24khz')"
EXPOSE 5000

CMD ["python3", "main.py"]
