FROM python:3.12

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN pip install -r requirements.txt

CMD [ "python",  "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080" ]