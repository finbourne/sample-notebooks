![LUSID_by_Finbourne](https://content.finbourne.com/LUSID_repo.png)

| branch | status |
| --- | --- |
| `master` |  [![Build Status](https://travis-ci.org/finbourne/sample-notebooks.svg?branch=master)](https://travis-ci.org/finbourne/sample-notebooks) |
| `develop` | [![Build Status](https://travis-ci.org/finbourne/sample-notebooks.svg?branch=develop)](https://travis-ci.org/finbourne/sample-notebooks)

Sample notebooks showcasing how to use the LUSID SDK.

## To Interact with the notebooks

1. Clone the sample-notebooks repository
2. Ensure that you are in the sample-notebooks folder
3. Build the Docker image locally

```
docker build -t finbourne/lusid-sample-notebooks .
```

4. Run the Docker image

**Windows**
```
docker run -it -v %cd%:/tmp/working -p 8888:8888 finbourne/lusid-sample-notebooks
```
**Mac/Linux**
```
docker run -it -v $(pwd):/tmp/working -p 8888:8888 finbourne/lusid-sample-notebooks
```
5. Navigate to `localhost:8888`
6. Copy the token shown in your console and paste it into your browser to log in
7. Create a secrets.json file in the **examples** folder with your LUSID credentials
see **Using a secrets.json file** at https://support.lusid.com/getting-started-with-apis-sdks for details on this

You're good to go!
