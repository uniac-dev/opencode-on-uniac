FROM ghcr.io/anomalyco/opencode:2.2.5@sha256:205e1bf535120ea110c1f93cbed0e91844fbb887725e7e70a44698f052f34328

COPY entrypoint.sh /usr/local/bin/uniac-opencode
COPY opencode.json /etc/uniac-opencode.json
RUN apk add --no-cache bash git python3 nodejs npm curl \
    && chmod 0755 /usr/local/bin/uniac-opencode
WORKDIR /data/workspace
EXPOSE 4096
ENTRYPOINT ["/usr/local/bin/uniac-opencode"]
