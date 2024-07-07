#!/usr/bin/env bash

# Included into the built image via its Dockerfile

if [ -s /app/chainmapper.sqlite3 ]; then
    exit 0
else
    exit 1
fi
