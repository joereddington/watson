#!/bin/bash
cd "$(dirname "$0")"
cp /Users/joereddingtonfileless/Library/Application\ Support/Firefox/Profiles/qrl7jda1.default-release/places.sqlite databases/firefox.sqlite
python3 history_list.py "$1"
