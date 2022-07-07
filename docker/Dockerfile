FROM gmap/isis3:gdal

# You can use a tag (v0.8rc, for example)
ARG VERSION='master'

RUN ls /opt || mkdir /opt 

RUN cd /opt && \
    git clone --branch $VERSION https://github.com/chbrandt/npt.git && \
    cd npt && \
    pip install .

