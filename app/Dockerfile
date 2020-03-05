FROM tiangolo/uwsgi-nginx-flask:python3.6

EXPOSE 5000

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

RUN python -m nltk.downloader -d /usr/local/nltk_data wordnet
RUN python -c "import nltk; nltk.download('punkt')"

COPY . /app
CMD ["uwsgi", "--ini", "uwsgi.ini"]
