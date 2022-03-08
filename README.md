# Maintain-zotero

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/chraibi/maintain-zotero/main/app.py)


This is a diagnostic tool to ease maintaining a Zotero library.

It implements some functionalities as:

- List all duplicate items and/or merge them.
- List all items with no pdf files
- List all items with duplicate pdf files and/or delete them (but one).
- List standanlone items
- List items with some flaws, e.g. missing doi/isbn numbers or "ill-formes".
- Update and/or delete some tags
- ...

<img width="1164" alt="Screen Shot 2022-03-08 at 05 54 09" src="https://user-images.githubusercontent.com/5772973/157168705-67b5f83e-2a93-4591-a08b-cf962764c31a.png">

## Requirements

These notebooks uses [Pyzotero documentation](https://pyzotero.readthedocs.io/en/latest/).
>>>>>>> 304ebc02347c8f003d7d852476ea710033773086

## Credits

Some parts of the merging function are adapted from [zotero-cleanup](https://github.com/christianbrodbeck/zotero-cleanup).
