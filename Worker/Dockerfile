FROM python:3.9

WORKDIR /worker

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["python","-u", "/worker/worker.py"]