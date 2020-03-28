#!/usr/bin/env zsh

# --- Global Definitions --- #
PROJECT_DIR=${0:a:h}
PACKAGING_DIR="$PROJECT_DIR/package"
# -------------------------- #

case "$1" in 

  dryrun)
    # Copy everything into packaging folder
    cp $PROJECT_DIR/README.md  $PACKAGING_DIR
    cp $PROJECT_DIR/LICENSE    $PACKAGING_DIR
    cp -R $PROJECT_DIR/src/*   $PACKAGING_DIR/csvquery
    # Delete package/dist if it exists
    [ -d $PACKAGING_DIR/dist ] &&
      rm -r $PACKAGING_DIR/dist;
  ;;

  upload)
    # Copy everything into packaging folder
    cp $PROJECT_DIR/README.md  $PACKAGING_DIR
    cp $PROJECT_DIR/LICENSE    $PACKAGING_DIR
    cp -R $PROJECT_DIR/src/*   $PACKAGING_DIR/csvquery
    # Delete package/dist if it exists
    [ -d $PACKAGING_DIR/dist ] &&
      rm -r $PACKAGING_DIR/dist;
    # Upload the package
    cd $PACKAGING_DIR;
    python3 setup.py sdist bdist_wheel &&
      python3 -m twine upload $PACKAGING_DIR/dist/*
  ;;

  *)
    echo "Usage:"
    echo "  $0 upload  --->   CAUTION: Publishes package to PyPi"
    echo "  $0 dryrun  --->   Does everything except publish to PyPi"
  ;;

esac
