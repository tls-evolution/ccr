#!/bin/bash
USER=tls13
DB=tls13

# If the DB does not exist, as user postgres:
# CREATE DATABASE tls13 OWNER tls13
# \c tls13
# CREATE EXTENSION ip4r

for SCHEMA in may_2019 jun_2019 jul_2019 aug_2019; do
    psql -U $USER $DB << EOF
        CREATE SCHEMA IF NOT EXISTS $SCHEMA
EOF
done

for SCHEMA in may_2019 jun_2019 jul_2019 aug_2019; do
    for ZONE in alexa czds cno cctld com net org; do
        psql -U $USER $DB << EOF
            CREATE TABLE IF NOT EXISTS $SCHEMA.${ZONE}_hosts (host ip4r, rtt NUMERIC, port INT, server_name TEXT, synStart INT, synEnd INT, scanEnd INT, protocol TEXT, cipher TEXT, resultString TEXT, verify_err_no TEXT, verify_code TEXT, server_version TEXT, depth INT, depth_verbose TEXT, error_data TEXT)
EOF
    done
done

for SCHEMA in may_2019 jun_2019 jul_2019 aug_2019; do
    for ZONE in alexa czds cno cctld com net org; do
        psql -U $USER $DB << EOF
            CREATE TABLE IF NOT EXISTS $SCHEMA.${ZONE}_cloudflare_hosts (host ip4r, rtt NUMERIC, port INT, server_name TEXT, synStart INT, synEnd INT, scanEnd INT, protocol TEXT, cipher TEXT, resultString TEXT, verify_err_no TEXT, verify_code TEXT, server_version TEXT, depth INT, depth_verbose TEXT, error_data TEXT)
EOF
    done
done
