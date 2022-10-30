
# ZoteroTidy

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/chraibi/zoterotidy/main/app.py)
[![Heroku](http://heroku-shields.herokuapp.com/zotero-tidy)](https://zotero-tidy.herokuapp.com/)

This is a diagnostic tool to ease maintaining a Zotero library.

It implements some repetitive, simple, but annoyingly repetitive tasks such as:

- List all duplicate items and/or merge them.
- List all items with no pdf files
- List all items with duplicate pdf files and/or delete them (but one).
- List standanlone items
- List items with some flaws, e.g. missing doi/isbn numbers or "ill-formmed".
- Update and/or delete some tags
- ...

(YouTube-Video)

[![Alt text](https://user-images.githubusercontent.com/5772973/157309426-0eb7013d-4ded-4697-88ab-a549bd0985b1.png)](https://www.youtube.com/watch?v=P_YeNXEOINk)

## Example

**Before**
- 11 Items
- 2 Items are duplicates 
- 5 Items have duplicate pdf files

<img width="1018" alt="Zotero_Before" src="https://user-images.githubusercontent.com/5772973/157308069-6fc1e798-8a87-4b02-b6f3-5288c3663517.png">

**After**
- 9 Items
- 0 Items are duplicates 
- 0 Items have duplicate pdf files

<img width="1019" alt="Zotero_After" src="https://user-images.githubusercontent.com/5772973/157308107-7c33d7ba-6b6d-4e8e-86de-ff2c18b6ad22.png">

## Limitations

For read-only operations, the app is quite fast.

The UI needs some polishing. The `syncing` and `loading` can be put together. Might need some *advanced* Streamlite skills, though :trollface:

## Requirements

The notebooks use [Pyzotero documentation](https://pyzotero.readthedocs.io/en/latest/).
But they are kinda absolete. You should use the Streamlite-App in the link above.

## Credits

Some parts of the merging function are adapted from [zotero-cleanup](https://github.com/christianbrodbeck/zotero-cleanup).

