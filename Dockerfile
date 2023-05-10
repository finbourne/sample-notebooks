# Pull base image
FROM jupyter/base-notebook:python-3.10

ENV NEXUS_USER ${NEXUS_USER}
ENV NEXUS_PASSWORD ${NEXUS_PASSWORD}
ENV FBN_SECRETS_PATH ${FBN_SECRETS_PATH}

RUN mkdir -p /tmp/working
COPY requirements.txt /tmp/working
COPY .packages/ /tmp/packages/

RUN pip install -r /tmp/working/requirements.txt \
    && pip install /tmp/packages/finbourne_sdk_utilities-2.0.0-py3-none-any.whl --force-reinstall \
    && pip install /tmp/packages/lusid-0.11.5415-py3-none-any.whl --force-reinstall \
    && pip install /tmp/packages/lusidtools-2.0.0-py3-none-any.whl --force-reinstall
    
# Set the theme
RUN jt -ofs 12 -t chesterish

EXPOSE 8888

# Start the Jupyter notebook
CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0"]
