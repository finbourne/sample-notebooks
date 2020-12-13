![LUSID_by_Finbourne](https://content.finbourne.com/LUSID_repo.png)

| branch | status |
| --- | --- |
| `master`  | ![Daily build](https://github.com/finbourne/sample-notebooks/workflows/Daily%20build/badge.svg) ![Build and test](https://github.com/finbourne/sample-notebooks/workflows/Build%20and%20test/badge.svg) |
| `develop` | ![run-sample-notebooks-tests](https://github.com/finbourne/sample-notebooks/workflows/run-sample-notebooks-tests/badge.svg?branch=develop) |

Sample notebooks showcasing how to use the LUSID SDK.

# Running the notebooks locally

Create a `secrets.json` file in the **examples** folder with your LUSID credentials. See **Using a secrets.json file** at https://support.lusid.com/getting-started-with-apis-sdks for details on this.

## Docker

1. Ensure that you are in the sample-notebooks folder
2. Build the Docker image locally

```
docker build -t finbourne/lusid-sample-notebooks .
```

3. Run the Docker image

**Windows**
```
$ docker run --rm -it --name fbn-jupyter -v %cd%:/home/jovyan -e FBN_SECRETS_PATH=/home/jovyan/examples/secrets.json -p 8888:8888 finbourne/lusid-sample-notebooks
```
**macOS/linux**
```
$ docker run --rm -it --name fbn-jupyter -v $(pwd):/home/jovyan -e FBN_SECRETS_PATH=/home/jovyan/examples/secrets.json -p 8888:8888 finbourne/lusid-sample-notebooks
```

4. Click on the link shown in the console to open up JupyterHub in a browser.
5. You can now navigate to your chosen notebook and run it.
