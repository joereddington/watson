#!/bin/bash
cd "$(dirname "$0")"
#cp /Users/joe2021/Library/Application\ Support/Firefox/Profiles/qrl7jda1.default-release/places.sqlite databases/firefox.sqlite
cp /Users/joe2021/Library/Application\ Support/Firefox/Profiles/dato3gap.default-release/places.sqlite databases/firefox.sqlite
python3 history_list.py "$1"
