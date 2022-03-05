import datetime as dt
import logging
import os
import sys
from collections import defaultdict
from datetime import datetime

from pyzotero import zotero

DATE_FMT = "%Y-%m-%dT%XZ"
STATUS_OK = True
# T = dt.datetime.now()
# logfile = f"{T.year}-{T.month:02}-{T.day:02}_{T.hour:02}-{T.minute:02}-{T.second:02}.log"
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(levelname)s - %(asctime)s - %(message)s",
#     handlers=[logging.FileHandler(filename=logfile), logging.StreamHandler(sys.stdout)],
#     datefmt='%Y-%m-%d %H:%M:%S'
# )
# log = logging.getLogger()


def date_added(_item):
    return datetime.strptime(_item["data"]["dateAdded"], DATE_FMT)


def attachment_is_pdf(_child):
    return (
        _child["data"]["itemType"] == "attachment"
        and _child["data"]["contentType"] == "application/pdf"
        and _child["data"]["linkMode"] in ["imported_file",
                                         "linked_file",
                                         "imported_url"]
    )
# https://www.zotero.org/support/dev/web_api/v3/file_upload


def get_items_with_duplicate_pdf(_zot, _items):
    _items_duplicate_attach = []
    _pdf_attachments = defaultdict(list)
    for _item in _items:
        if is_standalone(_item):
            continue

        key = _item["key"]
        cs = _zot.children(key)
        for c in cs:
            if attachment_is_pdf(c):
                _pdf_attachments[key].append(c["data"]["filename"])

        if len(_pdf_attachments[key]) > 1:
            _items_duplicate_attach.append(_item)

    return _items_duplicate_attach, _pdf_attachments


def get_items_with_no_pdf_attachments(_zot, _items):
    _items_without_attach = []
    for _item in _items:
        has_attach = False
        if is_standalone(_item):
            continue

        key = _item["key"]
        cs = _zot.children(key)
        for c in cs:
            if attachment_is_pdf(c):
                has_attach = True
                break

        if not has_attach:
            _items_without_attach.append(_item)

    return _items_without_attach


def get_standalone_items(_items):
    standalone = []
    for _item in _items:
        if is_standalone(_item):
            standalone.append(_item)

    return standalone


def is_standalone(_item):      
    return _item["data"]["itemType"] in ['note', 'attachment']


# In[ ]:


def retrieve_data(zot, num_items):
    """
    Retrieve  top num_items data from zotero-library.

    Input:
    zot: zotero instance
    return:
    items
    """
    lib_items = zot.top(limit=num_items)
    print(len(lib_items))
    return lib_items


# In[ ]:


def get_items_by_doi_or_isbn(_lib_items):
    _items_by_doi_isbn = defaultdict(list)
    for _item in _lib_items:
        if "DOI" in _item["data"]:
            doi = _item["data"]["DOI"]
            if doi:
                _items_by_doi_isbn[doi].append(_item)

        elif "ISBN" in _item["data"]:
            isbn = _item["data"]["ISBN"]
            if isbn:
                _items_by_doi_isbn[isbn].append(_item)

    return _items_by_doi_isbn


# In[1]:


def get_items_with_empty_doi_isbn(_lib_items, field):
    """
    field in [DOI, ISBN]
    """
    empty = []
    print()
    for _item in _lib_items:
        if field in _item["data"]:
            f = _item["data"][field]
            
            if not f:
                empty.append(_item['data']['title'])
                
    return empty


# In[ ]:


def get_items_with_empty_doi_and_isbn(_lib_items, fields):
    """
    fields is a list: [DOI, ISBN]
    """
    empty = []
    for _item in _lib_items:
        result = []
        for field in fields:
            if field in _item["data"]:
                f = _item["data"][field]
                if not f:
                    result.append(False)     
                else:
                    result.append(True)

        if not any(result):
            empty.append(_item['data']['title'])
        
    return empty


# In[ ]:


def log_item(_item, pdf_attachments={}):
    key = item["key"]  
    if pdf_attachments:
        PDF_msg = f"PDF attachements: {pdf_attachments[key]}"
    else:
        PDF_msg = ""
    
    if "title" in _item["data"].keys():
        ttt = f"{_item['data']['title']}"
    else:
        ttt = ""
    
    firstname = ""
    lastname = ""
    attach = ""
    type_attach = ""
    if not is_standalone(_item):    
        creators = item["data"]["creators"]  # could be author or editor
        for creator in creators:
            if creator["creatorType"] == "author":
                firstname = creator["firstName"]
                lastname = creator["lastName"]
                break

        if "attachment" in item["links"].keys():
            attach = item["links"]["attachment"]["href"].split("/")[-1]
            type_attach = item["links"]["attachment"]["attachmentType"]

    
        msg = f"""Title: {ttt}
            ItemType: {_item['data']['itemType']}
            Author: {firstname}  {lastname}
            {PDF_msg}
            """   
    else:
        msg = f"""{ttt} ({_item['data']['itemType']})"""   

    #log.info(inspect.cleandoc(msg))
    log.info(msg)
#        Num Attach: {_item['meta']['numChildren']}
#        Key: {_item['data']['key']}    


# In[ ]:


def delete_pdf_attachments(_children, ask=False):
    deleted_attachment = False
    for child in _children[1:]:
        if not attachment_is_pdf(child):
            continue  # only for pdf files. Other files, like notes, zip, etc, should not be deleted, anyway.

        if ask:
            answer = input(f"delete {child['data']['filename']}? (y[N])")
            if answer == "y":
                log.warning(f"deleting {child['data']['filename']}")
                zot.delete_item(child)
                deleted_attachment = True

        else:
            log.warning(f"deleting {child['data']['filename']}")
            zot.delete_item(child)
            deleted_attachment = True

    return deleted_attachment


# In[ ]:


def log_title(_item):
    if "title" in _item["data"].keys():
        ttt = f"{_item['data']['title']}"
    else:
        ttt = ""

    msg = f"Title: {ttt}"
    logging.info(msg)


def add_tag(tags, _zot, _item):
    if not tags:
        return
    
    item_tags = _item['data']['tags']
    new_tags = [t for t in tags if not t in item_tags]
    log_title(_item)
    log.info(f" item has {len(tags)} tags: {', '.join([t['tag'] for t in item_tags])}")
    _zot.add_tags(_item, *new_tags)
    log.warning(f"add tags <{new_tags}> to item")

