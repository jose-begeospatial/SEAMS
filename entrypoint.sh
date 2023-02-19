#!/bin/bash

set -e

# Set custom pg_hba.conf file
# Connect to all databases (all) from any IP address on the localhost network (localhost/24) using the md5 authentication method
# Change to localhost/32 for single access
echo "host all all localhost/24 md5" > /var/lib/postgresql/data/pg_hba.conf

# Start the PostgreSQL service
/usr/lib/postgresql/$PG_MAJOR/bin/postgres -D /var/lib/postgresql/data
