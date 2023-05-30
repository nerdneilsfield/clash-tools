FROM python:3.11-slim-buster

ADD . /app
WORKDIR /app

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -U pip && pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

EXPOSE 8000
CMD ["python", "app.py"]