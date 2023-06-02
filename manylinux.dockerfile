ARG platform
FROM quay.io/pypa/manylinux2014_x86_64 as build

ARG openmpi_version
ARG gromacs_version

ENV OPENMPI_VERSION=${openmpi_version}
ENV GROMACS_VERSION=${gromacs_version}
ENV PATH_OLD="${PATH}"
ENV PATH="/workspace/venv/bin/:/opt/python/cp311-cp311/bin/:${PATH}"
ENV LD_LIBRARY_PATH="/usr/local/lib:${LD_LIBRARY_PATH}"
ENV CMAKE_INSTALL_LIBDIR="/usr/local/lib"
ENV CMAKE_INSTALL_FULL_LIBDIR="/usr/local/lib"
COPY . /workspace

RUN python -m venv /workspace/venv
RUN pip install git+https://github.com/nlesc-nano/nano-qmflows-manylinux@main
RUN mkdir -p /workspace/artifacts
RUN ls -l /workspace
RUN ls -l /workspace/tools
RUN python /workspace/tools/install_openmpi.py $OPENMPI_VERSION --prefix=/workspace/artifacts --libdir=/usr/local/lib
RUN python /workspace/tools/install_gromacs.py $GROMACS_VERSION --prefix=/workspace/artifacts
