FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc g++ make cmake git \
    build-essential python3-dev \
    libffi-dev libssl-dev \
    libblas-dev liblapack-dev \
    libboost-all-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN git clone https://github.com/jackee777/babelnetpy.git && \
    cd babelnetpy && \
    python setup.py install

RUN python -m spacy download es_core_news_md

# Download NLTK data during build to avoid race conditions with --preload
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Models are inserted using the ./restart_container.sh script. 

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "--timeout", "200", "wsgi:app"]