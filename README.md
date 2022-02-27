# Maintain-zotero

These notebooks do two different operations:

1. detect items with multiple attachments, then delete the duplicates,
keeping only one attachment.

2. detect duplicate items and merge them.

`Zotero`, can detect duplicates and merge them. However, this [operation](https://www.zotero.org/support/duplicate_detection)
can only be done manually.

## Before usage

| :warning: WARNING          |
|:---------------------------|
| Do not use these notebooks without first backing up your data.     |

These functions modify the library hosted on [zotero.org](http://zotero.org).

Therefore

1. **Backup** first. See How to
   [locate, back up, and restore](https://www.zotero.org/support/zotero_data)
   your `Zotero` library data.
2. Disable sync in your desktop client before using it
3. Copy [config_template.cfg](config_template.cfg) in a new file called `config.cfg`,
   then populate it with the necessary information.

See notenbooks for more information.

## Usage

Since, these operations alter the `Zotero` library on the server, it is better,
to run the notebooks individually and **sync the group inbetween**.

For example: 

1. backup the library
2. manualy sync the library
3. [merge duplicate items](merge_duplicate_items.ipynb)
4. manualy sync the library
5. [delete duplicate attachments](remove_duplicate_attachments.ipynb)
6. manualy sync the library

Detailed documentation inside the notebooks.

## Requirements

These notebooks uses [Pyzotero documentation](https://pyzotero.readthedocs.io/en/latest/).

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

Some parts of the merging notebook are adapted from [zotero-cleanup](https://github.com/christianbrodbeck/zotero-cleanup).
