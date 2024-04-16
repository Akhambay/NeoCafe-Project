FROM python:3.12

ENV APP_HOME /app

WORKDIR $APP_HOME

# Install PostgreSQL client
RUN apt-get update && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/*
COPY ./requirements.txt .
RUN pip install -r requirements.txt
#RUN pip install loguru
RUN pip install 'uvicorn[standard]'
#ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /wait-for-it.sh
#RUN chmod +x /wait-for-it.sh

COPY . .