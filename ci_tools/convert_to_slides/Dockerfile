# Specify base image
# this one https://hub.docker.com/layers/library/python/slim-bullseye/images/sha256-f5bb52ea4db7c29a8f4253efaeae6ba2e69e435c1509368d4a774076b82e8f86?context=explore
FROM python@sha256:f5bb52ea4db7c29a8f4253efaeae6ba2e69e435c1509368d4a774076b82e8f86 as base

RUN pip install poetry==1.3.2



COPY . convert_to_slides
WORKDIR /convert_to_slides
RUN ls -a
RUN poetry install --without dev

FROM base as test
RUN poetry install
RUN poetry run tox

FROM base as release
