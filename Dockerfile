# Pull base image
FROM jupyter/base-notebook:python-3.11.4

ENV NEXUS_USER ${NEXUS_USER}
ENV NEXUS_PASSWORD ${NEXUS_PASSWORD}
ENV FBN_SECRETS_PATH ${FBN_SECRETS_PATH}

RUN mkdir -p /tmp/working
COPY requirements.txt /tmp/working

RUN pip install -r /tmp/working/requirements.txt

# Set the theme
RUN jt -ofs 12 -t chesterish

EXPOSE 8888

# Start the Jupyter notebook
CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0"]