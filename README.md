# Sample Jupyter Notebooks

This repository contains sample notebooks showcasing how to use the LUSID SDK. You can find a list of the notebooks at [examples/README](examples/README.md).

![LUSID_by_Finbourne](https://content.finbourne.com/LUSID_repo.png)

| branch | status |
| --- | --- |
| `master`  | ![Daily build](https://github.com/finbourne/sample-notebooks/workflows/Daily%20build/badge.svg) ![Build and test](https://github.com/finbourne/sample-notebooks/workflows/Build%20and%20test/badge.svg) |
| `develop` | ![run-sample-notebooks-tests](https://github.com/finbourne/sample-notebooks/workflows/run-sample-notebooks-tests/badge.svg?branch=develop) |



## Running the notebooks locally

You can run the notebooks locally by following these steps:

1. Clone this repository

```
git clone git@github.com:finbourne/sample-notebooks.git
cd sample-notebooks
```

2. Create a `secrets.json` file in the **examples** folder with your LUSID credentials. For more details on this, see the [Using a secrets.json file](https://support.lusid.com/getting-started-with-apis-sdks) documentation.

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
docker run --rm -it --name fbn-jupyter -v $(pwd):/home/jovyan -e FBN_SECRETS_PATH=/home/jovyan/examples/secrets.json -p 8888:8888 finbourne/lusid-sample-notebooks
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
6. Open the `examples` folder and navigate to your chosen notebook.
