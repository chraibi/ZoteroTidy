# Maintain-zotero

These notebooks detects items with multiple attachments, then delete them,
keeping only one attachment.

Zotero, can detect duplicates and merge them. However, this [operation](https://www.zotero.org/support/duplicate_detection)
can only be done manually.

## Before usage

| :warning: WARNING          |
|:---------------------------|
| Do not use these notebooks without first backing up your data.     |

These functions modify the library hosted on [zotero.org](http://zotero.org).

Therefore

1. **Backup** first. See How to
   [locate, back up, and restore](https://www.zotero.org/support/zotero_data)
   your Zotero library data.
2. Disable sync in your desktop client before using it
3. Copy [config_template.cfg](config_template.cfg) in a new file called `config.cfg`,
   then populate it with the necessary information.

See notenbooks for more information.

## Usage

Since, these operations alter the zotero group on the server, it is better,
to run the notebooks individually and **sync the group inbetween**.

- [merge items](merge_items.ipynb)
- [delete duplicate attachements](remove_duplicate_attachements.ipynb)

Detailed documentation inside the notebooks.

## Requirements

This notebook uses [Pyzotero documentation](https://pyzotero.readthedocs.io/en/latest/).

## Credits

Some parts of the merging notebook are adapted from [zotero-cleanup](https://github.com/christianbrodbeck/zotero-cleanup).
