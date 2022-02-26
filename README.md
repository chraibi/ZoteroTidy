# Maintain-zotero

This notebook detects items with multiple attachments, then deltes them,
keeping only one attachment.

Furthermore, if detects duplicate items and merges them.

Zotero, can detect duplicates and merge them. However, this [operation](https://www.zotero.org/support/duplicate_detection)
can only be done manually.

## Before usage

These functions modify the library hosted on [zotero.org](http://zotero.org).

Therefore

1. **Backup** first. See How to
   [locate, back up, and restore](https://www.zotero.org/support/zotero_data)
   your Zotero library data.
2. Disable sync in your desktop client before using it
3. Copy [config_template.cfg](config_template.cfg) in a new file called `config.cfg`,
   then populate it with the necessary information.
   See Notenbook for more information.

## Requirements

This notebook uses [Pyzotero documentation](https://pyzotero.readthedocs.io/en/latest/).
