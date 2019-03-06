import os
import sys
import json
import requests
import subprocess
import unittest
from urllib.request import pathname2url

source_folder = os.getenv("FBN_NOTEBOOK_FOLDER")

if source_folder is None or not os.path.exists(source_folder):
    sys.exit("ERROR: cannot find source folder '{0}'".format(source_folder))

def read_configuration():

    token_url = os.getenv("FBN_TOKEN_URL")
    username = os.getenv("FBN_USERNAME")
    password = pathname2url(os.getenv("FBN_PASSWORD"))
    client_id = pathname2url(os.getenv("FBN_CLIENT_ID"))
    client_secret = pathname2url(os.getenv("FBN_CLIENT_SECRET"))
    api_url = os.getenv("FBN_LUSID_API_URL")

    token_request_body = ("grant_type=password&username={0}".format(username) +
                          "&password={0}&scope=openid client groups".format(password) +
                          "&client_id={0}&client_secret={1}".format(client_id, client_secret))

    headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
    okta_response = requests.post(token_url, data=token_request_body, headers=headers)

    assert okta_response.status_code == 200

    access_token = okta_response.json()["access_token"]

    return api_url, access_token


def create_test_func(notebook_name):
    url, token = read_configuration()

    os.environ["ACCESS_TOKEN"] = token
    os.environ["FBN_LUSID_API_URL"] = url

    def test_func(self):

        print("running {0}...".format(notebook_name), end="")
        nb = subprocess.Popen(["jupyter", "nbconvert", notebook_name, "--execute"],
                              env=os.environ,
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        output, err = nb.communicate()

        if nb.returncode == 0:
            print("PASSED")
        else:
            print("ERROR\n")
            print(err.decode())
            print()
            self.fail()

    return test_func


attrs = {}


for root, dirs, files in os.walk(source_folder):

    for file in files:
        if not file.endswith(".ipynb"):
            continue

        print("checking: {}".format(file))
        safe_name = file[:-6].replace(' ', '_').replace('-', '_')

        attrs["test_" + safe_name] = create_test_func(os.path.join(root, file))

TestRunner = type("TestRunner", (unittest.TestCase,), attrs)


if __name__ == '__main__':
    unittest.main()
