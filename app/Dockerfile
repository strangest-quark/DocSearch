FROM python:3.6

EXPOSE 80

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

RUN python -m nltk.downloader wordnet

COPY . /app
CMD python app.py --config ./config/config.yaml
