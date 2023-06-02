"""Python script for building GROMACS."""

from __future__ import annotations

import subprocess
import shutil
import os
import argparse
from collections.abc import Iterable
from pathlib import Path

import dep_builder
from dep_builder import TimeLogger

PKG_NAME = "GROMACS"
URL_TEMPLATE = "https://ftp.gromacs.org/gromacs/gromacs-{version}.tar.gz"

download_and_unpack = TimeLogger(f"Download and unpack {PKG_NAME}")(dep_builder.download_and_unpack)
read_config_log = TimeLogger(f"Dumping {PKG_NAME} config log")(dep_builder.read_config_log)
build = TimeLogger(f"Build {PKG_NAME}")(dep_builder.build)
parse_version = TimeLogger(f"Parsing {PKG_NAME} version")(dep_builder.parse_version)


@TimeLogger(f"Configure {PKG_NAME}")
def configure(
    src_path: str | os.PathLike[str],
    build_path: str | os.PathLike[str],
    install_path: str | os.PathLike[str],
    args: Iterable[str] = (),
) -> None:
    """Run cmake."""
    os.mkdir(build_path)
    os.mkdir(install_path)
    subprocess.run(
        f"cmake -S {os.fspath(src_path)} -B {build_path} --install-prefix={install_path} "
        f"{' '.join(args)}", shell=True, check=True,
    )


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
        os.path.join(src_path, "COPYING"),
        license_path / f"{PKG_NAME}_LICENSE.txt".upper(),
    )


def main(version: str, install_path: str | os.PathLike[str], args: list[str]) -> None:
    """Run the script."""
    parse_version(version)
    url = URL_TEMPLATE.format(version=version)

    src_path: None | Path = None
    build_path = Path(os.getcwd()) / "build"
    try:
        src_path = download_and_unpack(url)
        try:
            config_args = [
                "-DGMX_BUILD_OWN_FFTW=ON",
                "-DGMX_FFT_LIBRARY=fftw3",
                "-DGMX_MPI=ON",
                "-DGMX_DOUBLE=ON",
                "-DBUILD_SHARED_LIBS=OFF",
                "-DGMX_PREFER_STATIC_LIBS=ON",
                *args,
            ]
            configure(src_path, build_path, install_path, config_args)
        finally:
            read_config_log(build_path, os.path.join("CMakeFiles", "CMakeConfigureLog.yaml"))
        build(build_path)
        copy_license(src_path, install_path)
    finally:
        shutil.rmtree(build_path, ignore_errors=True)
        if src_path is not None:
            shutil.rmtree(src_path, ignore_errors=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage="python ./build_gromacs.py 2023.1", description=__doc__)
    parser.add_argument("version", help="The library version")
    parser.add_argument(
        "--prefix", dest="prefix", help="install architecture-independent files in PREFIX"
    )
    parser.add_argument("args", metavar="ARGS", default=[], nargs=argparse.REMAINDER,
                        help="Arguments to pass the 'configure' file")

    args = parser.parse_args()
    main(args.version, args.prefix, args.args)
