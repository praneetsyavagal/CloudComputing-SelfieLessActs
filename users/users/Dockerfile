FROM python:3.6-alpine

WORKDIR /app

COPY . /app

RUN apk --update add py3-pip libxml2-dev libxslt-dev libffi-dev gcc musl-dev libgcc openssl-dev curl
RUN apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

EXPOSE 80

ENV NAME TEAM_ID=CC_261_272_273_279

CMD ["python3", "main.py"]

