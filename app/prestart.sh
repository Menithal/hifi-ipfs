#! /usr/bin/env bash

echo "Running inside /app/prestart.sh"

sleep 10;
echo "Trying to upgrade db";
flask db upgrade;
echo "DB Upgrade Complete";