# Sample Jupyter Notebooks

This repository contains Jupyter notebooks showcasing how to use the LUSID SDK. You can find a list of the notebooks at [examples/README](examples/README.md).

![LUSID_by_Finbourne](https://content.finbourne.com/LUSID_repo.png)

| branch | status |
| --- | --- |
| `master`  | ![Daily build](https://github.com/finbourne/sample-notebooks/workflows/Daily%20build/badge.svg) ![Build and test](https://github.com/finbourne/sample-notebooks/workflows/Build%20and%20test/badge.svg) |
| `develop` | ![Build and test](https://github.com/finbourne/sample-notebooks/workflows/Build%20and%20test/badge.svg?branch=develop) [view builds](https://github.com/finbourne/sample-notebooks/actions/workflows/main.yml?query=branch%3Adevelop) |


## Running the Notebooks in Jupyterhub for your LUSID domain

Authentication is handled automatically; see https://support.lusid.com/knowledgebase/article/KA-01829/en-us

## Running the Notebooks locally

You can run the Notebooks locally but you will need to set up authentication using a secrets file:

1. Clone this repository

```
git clone git@github.com:finbourne/sample-notebooks.git
cd sample-notebooks
```

2. Create a `secrets.json` file in the **examples** folder with your LUSID credentials. [See how to assemble these](https://support.lusid.com/knowledgebase/article/KA-01663/).

3. Build the Docker image

```
docker build -t finbourne/lusid-sample-notebooks .
```

4. Run the Docker image

**Windows**
```bash
docker run --rm -it --name fbn-jupyter -v %cd%:/home/jovyan -e FBN_SECRETS_PATH=/home/jovyan/examples/secrets.json -p 8888:8888 finbourne/lusid-sample-notebooks
```
**macOS/linux**
```bash
docker run --rm -it --name fbn-jupyter \
  -v $(pwd):/home/jovyan \
  -e FBN_SECRETS_PATH=/home/jovyan/examples/secrets.json \
  -p 8888:8888 \
  finbourne/lusid-sample-notebooks
```

You will see something similar to the following output:

```text
[I 09:14:44.031 NotebookApp] Writing notebook server cookie secret to /home/jovyan/.local/share/jupyter/runtime/notebook_cookie_secret
[I 09:14:45.228 NotebookApp] JupyterLab extension loaded from /opt/conda/lib/python3.7/site-packages/jupyterlab
[I 09:14:45.228 NotebookApp] JupyterLab application directory is /opt/conda/share/jupyter/lab
[I 09:14:45.231 NotebookApp] Serving notebooks from local directory: /home/jovyan
[I 09:14:45.231 NotebookApp] The Jupyter Notebook is running at:
[I 09:14:45.231 NotebookApp] http://e910e1f74c45:8888/?token=<token>
[I 09:14:45.231 NotebookApp]  or http://127.0.0.1:8888/?token=<token>
[I 09:14:45.231 NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
[C 09:14:45.245 NotebookApp] 
    
    To access the notebook, open this file in a browser:
        file:///home/jovyan/.local/share/jupyter/runtime/nbserver-6-open.html
    Or copy and paste one of these URLs:
        http://e910e1f74c45:8888/?token=<token>
     or http://127.0.0.1:8888/?token=<token>
```

5. Click on the link shown in the console to open up JupyterHub in a browser.
6. Open the `examples` folder and open <a href="http://localhost:8888/notebooks/examples/index.ipynb" target="_blank">index.ipynb</a> to see a catalogue of available notebooks.

## Contributing

We welcome contributions from our community. See our [contributing guide](docs/CONTRIBUTING.md) for information on how to contribute to the Sample Notebooks repository.