# Pull base image
FROM gcr.io/kaggle-images/python

# Install Jupyterthemes
RUN pip install jupyterthemes

# Set the theme
RUN jt -ofs 12 -t chesterish

ENV NEXUS_USER ${NEXUS_USER}
ENV NEXUS_PASSWORD ${NEXUS_PASSWORD}

RUN pip install lusid-sdk-preview

RUN mkdir -p /tmp/working

EXPOSE 8888

# Start the Jupyter notebook
CMD ["jupyter", "notebook", "--no-browser", "--ip='0.0.0.0'", "--notebook-dir=/tmp/working", "--allow-root"]
