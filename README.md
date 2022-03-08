[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/chraibi/maintain-zotero/main/app.py)

# Maintain-zotero

This is a diagnostic tool to ease maintaining a Zotero library. 

It implements some functionalities as: 

- List all duplicate items and/or merge them.
- List all items with no pdf files
- List all items with duplicate pdf files and/or delete them (but one).
- List standanlone items 
- List items with some flaws, e.g. missing doi/isbn numbers or "ill-formes".
- Update and/or delete some tags
- ...



## Example 

### Before 
<img width="648" alt="Screen Shot 2022-02-27 at 15 27 25" src="https://user-images.githubusercontent.com/5772973/155886867-8ffa5580-4061-43a6-9c9a-d428afc485d8.png">

### After calling "delete duplicate attachments" notebook

<img width="651" alt="Screen Shot 2022-02-27 at 15 33 06" src="https://user-images.githubusercontent.com/5772973/155886881-61e3ba2f-105b-4f9a-8689-9f010d88e3b7.png">

To be on the save side, **manual** decisions have to be made here:

<img width="548" alt="Screen Shot 2022-02-27 at 15 33 16" src="https://user-images.githubusercontent.com/5772973/155886926-a38d3cb0-c3c1-438a-92ba-741be19d0331.png">

### After calling "merge duplicate items" notebook

<img width="652" alt="Screen Shot 2022-02-27 at 15 34 11" src="https://user-images.githubusercontent.com/5772973/155886971-72ba7c69-639e-4820-aad7-c83db19942b8.png">

Output:

<img width="489" alt="Screen Shot 2022-02-27 at 15 33 59" src="https://user-images.githubusercontent.com/5772973/155886978-ef1524b8-c205-4e52-be08-916e6a7bfbfc.png">


## Credits

Some parts of the merging function are adapted from [zotero-cleanup](https://github.com/christianbrodbeck/zotero-cleanup).
