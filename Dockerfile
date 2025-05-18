FROM python:3.13-alpine

COPY . .

RUN pip install -r requirements.txt

EXPOSE 3000

CMD ["python", "main.py"]