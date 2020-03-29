#!/usr/bin/env zsh

# --- Global Definitions --- #
PROJ_DIR=${0:a:h}
PKG_DIR="$PROJ_DIR/package"
PKG_NAME="csvquery"

source build/packaging_tools.zsh
# -------------------------- #

case "$1" in 
  dryrun)
    update_pkg_dir $PROJ_DIR $PKG_DIR
    return $?;
  ;;

  publish)
    update_pkg_dir $PROJ_DIR $PKG_DIR &&
      publish_pkg  $PKG_DIR &&
      clean        $PKG_DIR $PKG_NAME

    return $?
  ;;

  clean)
    clean $PKG_DIR $PKG_NAME
    return $?
  ;;

  *)
    echo "Usage:"
    echo "  $0 publish  ---> CAUTION: Publishes package to PyPi"
    echo "  $0 dryrun   ---> Does everything except publish to PyPi"
    echo "  $0 clean    ---> clears out package/{dist,$PKG_NAME.egg-info,build}/"
    return -1;
  ;;
esac
