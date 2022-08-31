# docgen

To generate the docs run the following command from the root of the repo:

```
$ PYTHONPATH=$(pwd):$PYTHONPATH python docgen/parser.py
```

This script writes its output to [examples/README.md](../examples/README.md). The generated README file is based on the [README.mustache](README.mustache) template
