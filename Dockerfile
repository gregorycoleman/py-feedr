# docker build . -t py-feedr
FROM python:3.6

# Create app directory
WORKDIR /app

RUN apt-get -y update
RUN apt-get install -y git vim
RUN git clone https://github.com/gregorycoleman/py-feedr.git
RUN pip3 install beautifulsoup4==4.6.0
RUN pip3 install feedparser==5.2.1
RUN pip3 install twitter==1.18.0
RUN cd py-feedr
RUN touch /app/py-feedr/README.rst
RUN python3 setup.py install

# Run this

# /usr/bin/python3 /app/py-feedr/bin/feedr cfg.ini
