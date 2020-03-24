#!/bin/bash
cp README.md package/README.md
cp csvquery.py package/csvquery/
cd package && rm -r dist && python3 setup.py sdist bdist_wheel && python3 -m twine upload dist/*
