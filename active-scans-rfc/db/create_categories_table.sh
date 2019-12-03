#!/bin/bash
USER=tls13
DB=tls13

# If the DB does not exist, as user postgres:
# CREATE DATABASE tls13 OWNER tls13
# \c tls13
# CREATE EXTENSION ip4r

if [[ "$1" == "--help" ]] || [[ "$1" == "--h" ]] || [[ $# == 0 ]]; then
    echo "Usage $0 SCHEMA"
    exit
fi

SCHEMA=$1

psql -U $USER $DB << EOF
CREATE SCHEMA IF NOT EXISTS $SCHEMA
EOF

psql -U $USER $DB << EOF
CREATE TABLE IF NOT EXISTS $SCHEMA.categories (server_name TEXT, category TEXT, list TEXT, sample TEXT)
EOF
