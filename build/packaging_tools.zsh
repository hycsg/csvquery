#!/usr/bin/env zsh

function error_msg() {
  ([ -z $1 ] || [ -z $2 ]) &&
    return -1;
  caller=$1
  msg=$2

  print "$caller: $msg" 1>&2
}

# update_pkg_dir <project_root> <package_folder>
#  0 --> success
# -1 --> not enough arguments supplied
function update_pkg_dir() {
  ([ -z $1 ] || [ -z $2 ]) &&
    return -1;
  project=$1
  package=$2

  cp    $project/README.md  $package ||
    error_msg "update_pkg_dir" "failed to copy README.md into package"

  cp    $project/LICENSE    $package ||
    error_msg "update_pkg_dir" "failed to copy LICENSE into package"

  cp -R $project/src/*      $package/csvquery ||
    error_msg "update_pkg_dir" "failed to copy src/* into package"

  return 0;
}

# clean <package_dir> <package_name>
#  0 --> success
# -1 --> not enough arguments supplied
# -2 --> failed to remove directory
# -3 --> failed to remove file
function clean() {
  ([ -z $1 ] || [ -z $2 ]) &&
    return -1;
  pkg_dir=$1
  pkg_name=$2

  dirs_to_delete=(
    "$pkg_dir/dist"
    "$pkg_dir/build"
    "$pkg_dir/$pkg_name"
    "$pkg_dir/$pkg_name.egg-info"
  )
  files_to_delete=(
    "$pkg_dir/README.md"
    "$pkg_dir/LICENSE"
  )

  for dir in $dirs_to_delete; do
    [ -d $dir ] && (
      rm -r $dir || (
        error_msg "clean" "Could not remove directory '$dir'" &&
        return -2
      )
    )
  done

  for file in $files_to_delete; do
    [ -e $file ] && (
      rm $file || (
        error_msg "clean" "Could not remove file '$file'" &&
        return -3
      )
    )
  done

  return 0;
}

# publish_pkg <package_folder>
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
