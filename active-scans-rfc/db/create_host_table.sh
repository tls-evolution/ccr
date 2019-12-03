#!/bin/bash
USER=tls13
DB=tls13

# If the DB does not exist, as user postgres:
# CREATE DATABASE tls13 OWNER tls13
# \c tls13
# CREATE EXTENSION ip4r

if [[ "$1" == "--help" ]] || [[ "$1" == "--h" ]] || [[ $# == 0 ]]; then
    echo "Usage $0 SCHEMA TABLE"
    exit
fi

SCHEMA=$1
TABLE=$2

psql -U $USER $DB << EOF
CREATE SCHEMA IF NOT EXISTS $SCHEMA
EOF

psql -U $USER $DB << EOF
CREATE TABLE IF NOT EXISTS $SCHEMA.${TABLE} (host ip4, rtt NUMERIC, port INT, server_name TEXT, synStart INT, synEnd INT, scanEnd INT, protocol TEXT, cipher TEXT, resultString TEXT, verify_err_no TEXT, verify_code TEXT, server_version TEXT, depth INT, depth_verbose TEXT, error_data TEXT)
EOF
