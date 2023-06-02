"""Python script for building OpenMPI."""

from __future__ import annotations

import shutil
import os
import argparse
from pathlib import Path

import dep_builder
from dep_builder import TimeLogger

PKG_NAME = "OpenMPI"
URL_TEMPLATE = "https://download.open-mpi.org/release/open-mpi/v{version_short}/openmpi-{version}.tar.gz"  # noqa: #E501

download_and_unpack = TimeLogger(f"Download and unpack {PKG_NAME}")(dep_builder.download_and_unpack)
read_config_log = TimeLogger(f"Dumping {PKG_NAME} config log")(dep_builder.read_config_log)
build = TimeLogger(f"Build {PKG_NAME}")(dep_builder.build)
parse_version = TimeLogger(f"Parsing {PKG_NAME} version")(dep_builder.parse_version)
configure = TimeLogger(f"Configure {PKG_NAME}")(dep_builder.configure)


@TimeLogger(f"Copy {PKG_NAME} license")
def copy_license(
    src_path: str | os.PathLike[str],
    install_path: str | os.PathLike[str],
) -> None:
    """Copy the packages license."""
    license_path = Path(install_path) / "licenses"
    if not os.path.isdir(license_path):
        os.mkdir(license_path)
    shutil.copy2(
        os.path.join(src_path, "LICENSE"),
        license_path / f"{PKG_NAME}_LICENSE.txt".upper(),
    )


def main(version: str, install_path: str | os.PathLike[str], args: list[str]) -> None:
    """Run the script."""
    version_obj = parse_version(version)
    url = URL_TEMPLATE.format(
        version=version,
        version_short=f"{version_obj.major}.{version_obj.minor}"
    )

    src_path: None | Path = None
    build_path = Path(os.getcwd()) / "build"
    try:
        src_path = download_and_unpack(url)
        try:
            config_args = [
                "--enable-shared=no",
                "--enable-static=yes",
                f"--prefix={os.fspath(install_path)}",
                *args,
            ]
            configure(src_path, build_path, config_args)
        finally:
            read_config_log(build_path)
        build(build_path)
        copy_license(src_path, install_path)
    finally:
        shutil.rmtree(build_path, ignore_errors=True)
        if src_path is not None:
            shutil.rmtree(src_path, ignore_errors=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage="python ./build_openmpi.py 4.1.5", description=__doc__)
    parser.add_argument("version", help="The library version")
    parser.add_argument("args", metavar="ARGS", default=[], nargs=argparse.REMAINDER,
                        help="Arguments to pass the 'configure' file")

    args = parser.parse_args()
    prefix = args.args[0][9:]
    main(args.version, prefix, args.args)
