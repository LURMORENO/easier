FROM python:3.7-slim-buster

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc g++ make cmake \
    build-essential python3-dev \
    libffi-dev libssl-dev \
    libblas-dev liblapack-dev \
    libboost-all-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN python -m spacy download es_core_news_md

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "--timeout", "200", "wsgi:app"]