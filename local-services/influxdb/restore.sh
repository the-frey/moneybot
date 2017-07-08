#!/usr/bin/env sh

# Download latest release
wget https://github.com/elsehow/moneybot/releases/download/database/${DB_RELEASE}.zip
unzip ./${DB_RELEASE}.zip

# Restore to InfluxDB
influxd restore -metadir ${INFLUX_DIR}/meta ./${DB_RELEASE}
influxd restore -database "${DB_NAME}" -datadir ${INFLUX_DIR}/data ./${DB_RELEASE}

# Clean up artifacts
rm -r ./${DB_RELEASE} ./${DB_RELEASE}.zip
