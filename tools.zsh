#!/usr/bin/env zsh

# --- Global Definitions --- #
PROJECT_DIR=${0:a:h}
PACKAGING_DIR="$PROJECT_DIR/package"
# -------------------------- #

case "$1" in 

  prepare_upload)
    cp $PROJECT_DIR/README.md   $PACKAGING_DIR/README.md
    cp $PROJECT_DIR/csvquery.py $PACKAGING_DIR/csvquery/csvquery.py
    rm -r $PACKAGING_DIR/dist
  ;;

  upload)
    cd $PACKAGING_DIR;
    rm -r dist/ &&
      python3 setup.py sdist bdist_wheel &&
      python3 -m twine upload $PACKAGING_DIR/dist/*
  ;;

  *)
    echo "Usage:"
    echo "  $0 prepare_upload     --->   Copy all the necessary files into the packing directory"
    echo "  $0 upload             --->   CAUTION: Publishes package to PyPi"
    echo "WARNING: '$0 upload' DOES NOT COPY ALL FILES INTO packaging dir"
  ;;

esac
