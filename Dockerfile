FROM python:3.11
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install -U pip
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
