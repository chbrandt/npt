FROM chbrandt/isis3

RUN pip install --upgrade pip && \
    git clone -b neanias https://github.com/chbrandt/gpt-neanias.git && \
    cd gpt-neanias && \
    pip install .
