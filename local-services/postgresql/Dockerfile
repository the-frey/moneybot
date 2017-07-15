FROM  postgres:9.6.3

# Install unzip (lol)
RUN   apt-get -qq update && \
      apt-get -qq install -y unzip && \
      rm -rf /var/lib/apt/lists/*

# # Download and restore seed database
# COPY  restore.sh ./
# ENV   DB_RELEASE 7-5-2017
# ENV   DB_NAME historical-poloniex
# ENV   INFLUX_DIR /var/lib/influxdb
# RUN   ./restore.sh
