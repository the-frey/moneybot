#!/usr/bin/env sh

DB_RELEASE=2017-14-07

echo "Downloading latest release"
wget https://github.com/elsehow/moneybot/releases/download/$DB_RELEASE/$DB_RELEASE.sql

echo "Restoring database to dockerized"
cat ./$DB_RELEASE.sql | docker exec -i postgres psql -U postgres

echo "Cleaning up artifacts"
rm -r ./$DB_RELEASE.sql
