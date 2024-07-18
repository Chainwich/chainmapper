#!/usr/bin/env bash

# Included into the built image via its Dockerfile

DB_FILE="/app/data/chainmapper.sqlite3"

if [ -s $DB_FILE ]; then
    exit 0
else
    echo "Database file not found"
    exit 1
fi
