FROM python:3.9
ARG UID=1000
ARG GID=1000
ENV UID=${UID}
ENV GID=${GID}
RUN groupadd --gid ${GID} www &&\
    useradd --uid ${UID} --gid www --shell /bin/bash --create-home -d /www www

COPY . /www
WORKDIR /www
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install -v --no-root

USER www
CMD ['echo', 'Ready to work!']
