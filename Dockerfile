FROM daocloud.io/library/python:3.6.2rcl-alpine
MAINTAINER zbsuper 123456@163.com

ADD ./www/
WORKDIR /www

RUN pip install -r requirement.txt
CMD ["python", "app.py", "runserver"]