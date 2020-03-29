#!/usr/bin/env zsh

# update_package_folder <project_root> <package_folder>
#  0 --> success
# -1 --> not enough arguments supplied
function update_pkg_dir() {
  ([ -z $1 ] || [ -z $2 ]) &&
    return -1;
  project=$1
  package=$2

  cp    $project/README.md  $package
  cp    $project/LICENSE    $package
  cp -R $project/src/*      $package/csvquery

  return 0;
}

# clean <package_dir> <package_name>
#  0 --> success
# -1 --> not enough arguments supplied
function clean() {
  ([ -z $1 ] || [ -z $2 ]) &&
    return -1;
  pkg_dir=$1
  pkg_name=$2

  [ -d $pkg_dir/dist ] && # package/dist/
    rm -r $pkg_dir/dist;

  [ -d $pkg_dir/$pkg_name.egg-info ] && # package/my_pkg.egg-info/
    rm -r $pkg_dir/$pkg_name.egg-info;

  [ -d $pkg_dir/build ] && # package/build/
    rm -r $pkg_dir/build;

  return 0;
}

# publish_package <package_folder>
#  0 --> success
# -1 --> not enough arguments supplied
function publish_pkg() {
  [ -z $1 ] &&
    return -1;
  pkg=$1

  cd $pkg;
  python3 setup.py sdist bdist_wheel &&
    python3 -m twine upload $pkg/dist/*;

  return 0;
}
