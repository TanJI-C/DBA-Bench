FROM postgres:16

RUN apt-get update \
    && apt-get install -y --no-install-recommends pgbouncer \
    && rm -rf /var/lib/apt/lists/*

USER postgres
ENTRYPOINT ["pgbouncer"]
