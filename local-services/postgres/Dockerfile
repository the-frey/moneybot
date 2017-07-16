FROM  postgres:9.6

# Install wget (lol)
# RUN   apt-get -qq update && \
#       apt-get -qq install -y wget && \
#       rm -rf /var/lib/apt/lists/*

# Download and restore seed database
COPY  restore.sh ./
ENV   DB_RELEASE 07-14-17
COPY  07-14-17.sql ./
RUN   ./restore.sh
