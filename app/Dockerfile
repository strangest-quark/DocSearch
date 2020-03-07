#FROM tiangolo/uwsgi-nginx-flask:python3.6
FROM python:3.6

EXPOSE 80

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

RUN python -m nltk.downloader -d /usr/local/nltk_data wordnet
RUN python -c "import nltk; nltk.download('punkt')"

COPY . /app

CMD python app.py --config ./config/config.yaml
#CMD ["uwsgi", "--ini", "uwsgi.ini"]
