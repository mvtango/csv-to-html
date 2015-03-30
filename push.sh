#! /bin/bash
python3 csv-to-html.py <$1 >index.html
rsync -v index.html $2
