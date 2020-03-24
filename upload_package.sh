#!/bin/sh
cp README.md package/README.md
cp csv_query.py package/csv-query/
cd package && rm -r dist && python3 setup.py sdist bdist_wheel && python3 -m twine upload dist/*