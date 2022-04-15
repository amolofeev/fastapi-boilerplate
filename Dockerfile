FROM python:3.10
ARG UID=1000
ARG GID=1000
ENV UID=${UID}
ENV GID=${GID}
RUN groupadd --gid ${GID} www &&\
    useradd --uid ${UID} --gid www --shell /bin/bash --create-home -d /www www

COPY . /www
RUN pip install -r /www/requirements.txt
WORKDIR /www

USER www
CMD ['echo', 'Ready to work!']
