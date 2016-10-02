from python:2-slim

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
RUN mkdir /pysmhs && mkdir /usr/local/etc/pysmhs
COPY ["pysmhs", "/pysmhs/pysmhs"]
COPY ["config", "/pysmhs/config/"]
COPY ["config", "/usr/local/etc/pysmhs/"]
COPY ["bin", "/pysmhs/bin/"]
COPY ["setup.py", "MANIFEST.in", "/pysmhs/"]
RUN cd /pysmhs/ && python setup.py install
EXPOSE 80
CMD ["pysmhs"]
