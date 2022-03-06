import logging
from collections import defaultdict
from datetime import datetime
import mylogging as mylog

import streamlit as st

DATE_FMT = "%Y-%m-%dT%XZ"
STATUS_OK = True


def intro():
    return st.markdown(
            """
        The app offers several functionalitiest to simplify maintenance
        of a Zotero library.
        #### How to use?
        Before using this app, the following parameters should be defined:
        - the `library_id`: Can be found by opening the
          [group](https://www.zotero.org/groups)’s page
          and hovering over the group settings link.
        - the `api_key`: Can be found from [here](https://www.zotero.org/settings/keys/new).
        - `library_type`:
           - own Zotero library --> user (*no tested*)
           - shared library --> group (*recommended*)

        You can define all these necessary information in a config-file.
        See [here](https://github.com/chraibi/maintain-zotero/blob/main/config_template.cfg)
        for an example.

        #### Functionalities
        Some functionalities **read** only from an online Zotero library
        and produce reports.

        Others, however, **change** the online Zotero library.

        **Tag library items:**
          - duplicate pdf-files: `duplicate_pdf`
          - Items *without* pdf-files: `nopdf`
          - Tag elements *libraryCatalog* \"Zotero\" with `todo_catalog`

        :red_circle: **NOET**: These options, need to calculate some lists,
        in case these are still empty, e.g.,
        List items with duplicate pdf attachments.

        ### :warning: Before changing the library
        :red_circle: **If you intend to change the Zotero library with
        this app, then** :red_circle:

        - Backup first
           See How to
           [locate, back up, and restore](https://www.zotero.org/support/zotero_data)
           your `Zotero` library data.
        -  Disable sync in your desktop client before using it.
           You can sync manually the group by right-clicking
           on it in your Zotero-client.
        """
        )

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


def get_suspecious_items(lib_items):
    list_catalog_zotero = []
    for item in lib_items:
        if 'libraryCatalog' in item['data']:
            catalog = item['data']['libraryCatalog']
            if catalog == "Zotero":
                list_catalog_zotero.append(item)

    return list_catalog_zotero


@st.cache
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


@st.cache
def get_items_with_no_pdf_attachments2(_items):
    _items_without_attach = []
    for item in _items:
        if is_standalone(item):
            _items_without_attach.append(item)
            continue

        if 'attachment' in item['links']:
            attach_type = item['links']['attachment']['attachmentType']
            if attach_type != 'application/pdf':
                _items_without_attach.append(item)

        else:
            _items_without_attach.append(item)

    return _items_without_attach


@st.cache
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
            standalone.append(_item["data"]["itemType"])

    return standalone


def is_standalone(_item):
    return _item["data"]["itemType"] in ['note', 'attachment']


def retrieve_data(zot, num_items):
    """
    Retrieve  top num_items data from zotero-library.

    Input:
    zot: zotero instance
    return:
    items
    """
    lib_items = zot.top(limit=num_items)
    return lib_items


def trash_is_empty(zot):
    print(len(st.session_state.suspecious_items))
    if len(zot.trash()) > 0:
        return False
    else:
        return True


def get_time(t):
    """ Get str run time as min sec
    """
    minutes = t // 60
    seconds = t % 60
    return f"""{minutes:.0f} min:{seconds:.0f} sec"""


def duplicates_by_title(lib_items):
    duplicate_items_by_title = defaultdict(list)
    duplicates = []
    for item in lib_items:
        if is_standalone(item):
            continue

        # key = item["data"]["key"]
        iType = item["data"]["itemType"]
        Title = item["data"]["title"]
        duplicate_items_by_title[iType].append(Title.capitalize())

    for Type in duplicate_items_by_title.keys():
        num_duplicates_items = len(duplicate_items_by_title[Type]) - len(
            set(duplicate_items_by_title[Type])
        )
        if num_duplicates_items:
            duplicates = set([x for x in duplicate_items_by_title[Type] if duplicate_items_by_title[Type].count(x) > 1])

    return duplicates


def duplicates_by_doi(lib_items):
    by_doi = get_items_by_doi_or_isbn(lib_items)
    result = []
    for doi, items in by_doi.items():
        if len(items) > 1:
            for i in items:
                result.append(i['data']['title'])

    return result


@st.cache
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


@st.cache
def get_items_with_empty_doi_isbn(_lib_items, field):
    """
    field in [DOI, ISBN]
    """
    empty = []
    for _item in _lib_items:
        if field in _item["data"]:
            f = _item["data"][field]

            if not f:
                empty.append(_item['data']['title'])

    return empty


@st.cache
def get_items_with_empty_doi_and_isbn(_lib_items, fields):
    """
    return title of items with no isbn and no doi

    fields is a list of str: ["DOI", "ISBN"]

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


def set_new_tag(z, n, m):
    """Update tags. This function updates session_state if necessary

    if session_state lists are empty, update.
    """
    new_tags = defaultdict(list)
    if z:
        update_suspecious_state()
        zotero_items = st.session_state.suspecious_items
        for item in zotero_items:
            new_tags[item["data"]["key"]].append("todo_catalog")

    if n:
        update_duplicate_attach_state()
        items_duplicate_attach = st.session_state.multpdf_items
        for item in items_duplicate_attach:
            new_tags[item["data"]["key"]].append("duplicate_pdf")

    if m:
        update_without_pdf_state()
        items_without_pdf = st.session_state.nopdf_items
        for item in items_without_pdf:
            new_tags[item["data"]["key"]].append("nopdf")

    return new_tags


def add_tag(tags_to_add, _zot, _item):
    if not tags_to_add:
        return False

    title = _item["data"]["title"]
    item_tags = [t['tag'] for t in _item['data']['tags']]
    new_tags = [t for t in tags_to_add if t not in item_tags]

    if not new_tags:
        return False

    with mylog.st_stdout("success"), mylog.st_stderr("code"):
        logging.info(f"add tags {new_tags} to {title}")

    _zot.add_tags(_item, *new_tags)
    return True


def update_suspecious_state():
    if not st.session_state.suspecious_items:
        items = get_suspecious_items(
            st.session_state.zot_items
        )
        st.session_state.suspecious_items = items


# @todo check if state variable need to be used as input for functions
def update_duplicate_attach_state():
    if not st.session_state.multpdf_items:
        items, pdfs = get_items_with_duplicate_pdf(
            st.session_state.zot, st.session_state.zot_items
        )

        st.session_state.multpdf_items = items
        st.session_state.pdfs = pdfs


def update_without_pdf_state():
    if not st.session_state.nopdf_items:
        items = get_items_with_no_pdf_attachments2(
            st.session_state.zot_items
        )

        st.session_state.nopdf_items = items


def uptodate():
    """Check if library is outdated

    If outdated, don't execute any update-functions
    """
    most_recent_item_on_server = st.session_state.zot.top(limit=1)[0]
    first_item_in_cache = st.session_state.zot_items[0]

    v1 = most_recent_item_on_server['data']['version']
    v2 = first_item_in_cache['data']['version']
    return v1 == v2


def update_tags(pl2, update_tags_z, update_tags_n, update_tags_m):
    new_tags = set_new_tag(
        update_tags_z,
        update_tags_n,
        update_tags_m
    )
    changed = []
    if not new_tags:
        pl2.info("Tags of the library are not changed.")
    else:
        pl2.warning("Updating tags ...")

        my_bar = st.progress(0)
        step = int(100 / st.session_state.num_items)
        for i, item in enumerate(st.session_state.zot_items):
            progress_by = (i + 1) * step
            if i == st.session_state.num_items - 1:
                progress_by = 100

            my_bar.progress(progress_by)
            ch = add_tag(
                new_tags[item["data"]["key"]],
                st.session_state.zot,
                item,
            )
            changed.append(ch)

        if any(changed):
            pl2.warning("Library updated. You may want to re-load it")
        else:
            pl2.info("Tags of the library are not changed.")
