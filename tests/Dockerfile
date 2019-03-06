FROM python:3

LABEL maintainer="engineering@finbourne.com"

WORKDIR /usr/src/

COPY requirements.txt /usr/src/

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install lusid-sdk --upgrade

COPY test_notebooks.py /usr/src

ENV FBN_NOTEBOOK_FOLDER ${FBN_NOTEBOOK_FOLDER}
ENV FBN_TOKEN_URL ${FBN_TOKEN_URL}
ENV FBN_USERNAME ${FBN_USERNAME}
ENV FBN_PASSWORD ${FBN_PASSWORD}
ENV FBN_CLIENT_ID ${FBN_CLIENT_ID}
ENV FBN_CLIENT_SECRET ${FBN_CLIENT_SECRET}
ENV FBN_LUSID_API_URL ${FBN_LUSID_API_URL}

ENTRYPOINT python test_notebooks.py
