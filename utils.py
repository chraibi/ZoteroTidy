import logging
from collections import defaultdict
from datetime import datetime
import mylogging as mylog

import streamlit as st

DATE_FMT = "%Y-%m-%dT%XZ"
STATUS_OK = True


# @todo split this to two expander
def intro():
    return st.markdown(
        """
        The app offers several functionalitiest to simplify maintenance
        of a Zotero library.
        ### How to use?
        Before using this app, the following parameters should be defined:
        - the `library_id`: Can be found by opening the
          [group](https://www.zotero.org/groups)’s page
          and hovering over the group settings link.
        - the `api_key`: Can be found from
          [here](https://www.zotero.org/settings/keys/new).
        - `library_type`:
           - own Zotero library --> user (*no tested*)
           - shared library --> group (*recommended*)

        You can define all these necessary information in a config-file.
        See
        [here](https://github.com/chraibi/maintain-zotero/blob/main/config_template.cfg)
        for an example.

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

        ---

        ### Functionalities
        Some functionalities **read** only from an online Zotero library
        and produce reports.

        Others, however, **change** the online Zotero library.
        These can not be executed if the library is not in sync.

        **Tag library items:**
          - Items with duplicate pdf-files: `duplicate_pdf`
          - Items *without* pdf-files: `nopdf`
          - Items with *libraryCatalog* \"Zotero\": `todo_catalog`
          - Duplicate items: `duplicate_item`
        :red_circle: **NOTE**: These options, need to calculate some lists,
        in case these are still empty, e.g.,
        List items with duplicate pdf attachments.

        ---

       **Merge duplicates:**
       We have duplicate `Items`, sorted with respect to the added date
       (oldest first):

       |Item|Number|Attachments |
       :---: | :---: | :---: |
       | $I_1$ |  1  | $PDF_1$ |
       | $I_2$ | 3  | $NOTE_2$, $PDF_2$, $OTHER_2$ |
       | $I_3$ | 2  | $NOTE_3$, $PDF_3$ |

       :red_circle: **NOTE:**
            Duplicate items are identified based on their DOI and/or ISBN

        **Actions**
          - Sort the Items with respect to added time (oldest first)
          - Keep the oldest `Item` (first added), i.e. $I_1$
          - Move all attachments of the newest `Item` to $I_1$
          - Delete other Items including their attachments ($I_2$ and $I_3$)

        **Result**

         The result of the actions described above is:

         - $I_1$ having 3 attachments
         - $PDF_1$, $NOTE_3$, $PDF_3$
        """
    )


def date_added(_item):
    return datetime.strptime(_item["data"]["dateAdded"], DATE_FMT)


def attachment_is_pdf(_child):
    return (
        _child["data"]["itemType"] == "attachment"
        and _child["data"]["contentType"] == "application/pdf"
        and _child["data"]["linkMode"]
        in ["imported_file", "linked_file", "imported_url"]
    )


# https://www.zotero.org/support/dev/web_api/v3/file_upload


def get_suspecious_items(lib_items):
    list_catalog_zotero = []
    for item in lib_items:
        if "libraryCatalog" in item["data"]:
            catalog = item["data"]["libraryCatalog"]
            if catalog == "Zotero":
                list_catalog_zotero.append(item)

    return list_catalog_zotero


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


def get_items_with_no_pdf_attachments2(_items):
    _items_without_attach = []
    for item in _items:
        if is_standalone(item):
            _items_without_attach.append(item)
            continue

        if "attachment" in item["links"]:
            attach_type = item["links"]["attachment"]["attachmentType"]
            if attach_type != "application/pdf":
                _items_without_attach.append(item)

        else:
            _items_without_attach.append(item)

    return _items_without_attach


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
    return _item["data"]["itemType"] in ["note", "attachment"]


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
    return len(zot.trash()) == 0


def get_time(t):
    """Get str run time as min sec"""
    minutes = t // 60
    seconds = t % 60
    return f"""{minutes:.0f} min:{seconds:.2f} sec"""


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
            # duplicates = set([x for x in duplicate_items_by_title[Type] if duplicate_items_by_title[Type].count(x) > 1])
            duplicates = {
                x
                for x in duplicate_items_by_title[Type]
                if duplicate_items_by_title[Type].count(x) > 1
            }

    return duplicates


def duplicates_by_doi(lib_items):
    by_doi = get_items_by_doi_or_isbn(lib_items)
    result = []
    for _, items in by_doi.items():
        if len(items) > 1:
            for i in items:
                result.append(i)

    return result


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


def get_items_with_empty_doi_isbn(_lib_items, field):
    """
    field in [DOI, ISBN]
    """
    empty = []
    for _item in _lib_items:
        if field in _item["data"]:
            f = _item["data"][field]

            if not f:
                empty.append(_item["data"]["title"])

    return empty


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
            empty.append(_item["data"]["title"])

    return empty


def delete_pdf_attachments(_children, pl2):
    deleted_attachment = False
    zot = st.session_state.zot
    for child in _children[1:]:
        if not attachment_is_pdf(child):
            continue  # only for pdf files.

        pl2.warning(f"deleting {child['data']['filename']}")
        zot.delete_item(child)
        deleted_attachment = True

    return deleted_attachment


def log_title(_item):
    if "title" in _item["data"].keys():
        ttt = f"{_item['data']['title']}"
    else:
        ttt = f"Standalone item of type: <{_item['data']['itemType']}>"

    with mylog.st_stdout("success"), mylog.st_stderr("code"):

        logging.info(f"{ttt}")


def set_new_tag(z, n, m, d):
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

    if d:
        update_duplicate_items_state()
        duplicate_items = st.session_state.doi_dupl_items
        print(type(duplicate_items))
        
        for item in duplicate_items:
            print(type(item), item)
            new_tags[item["data"]["key"]].append("duplicate_item")

    return new_tags


def add_tag(tags_to_add, _zot, _item):
    if not tags_to_add:
        return False

    title = _item["data"]["title"]
    item_tags = [t["tag"] for t in _item["data"]["tags"]]
    new_tags = [t for t in tags_to_add if t not in item_tags]

    if not new_tags:
        return False

    with mylog.st_stdout("success"), mylog.st_stderr("code"):
        logging.info(f"add tags {new_tags} to {title}")

    _zot.add_tags(_item, *new_tags)
    return True


def update_suspecious_state():
    if not st.session_state.suspecious_items:
        items = get_suspecious_items(st.session_state.zot_items)
        st.session_state.suspecious_items = items


# @todo check if state variable need to be used as input for functions
def update_duplicate_attach_state():
    if not st.session_state.init_multpdf_items:
        items, pdfs = get_items_with_duplicate_pdf(
            st.session_state.zot, st.session_state.zot_items
        )

        st.session_state.multpdf_items = items
        st.session_state.pdfs = pdfs
        st.session_state.init_multpdf_items = True


def force_update_duplicate_attach_state():
    items, pdfs = get_items_with_duplicate_pdf(
        st.session_state.zot, st.session_state.zot_items
    )

    st.session_state.multpdf_items = items
    st.session_state.pdfs = pdfs
    st.session_state.init_multpdf_items = True


def update_duplicate_items_state():
    if not st.session_state.init_doi_dupl_items:
        duplicates = duplicates_by_doi(st.session_state.zot_items)
        st.session_state.doi_dupl_items = duplicates
        st.session_state.init_doi_dupl_items = True


def force_update_duplicate_items_state():
    duplicates = duplicates_by_doi(st.session_state.zot_items)
    st.session_state.doi_dupl_items = duplicates
    st.session_state.init_doi_dupl_items = True


def update_without_pdf_state():
    if not st.session_state.nopdf_items:
        items = get_items_with_no_pdf_attachments2(st.session_state.zot_items)

        st.session_state.nopdf_items = items


def uptodate():
    """Check if library is up to date

    every change in Zotero-Library increments
    the version number by one.
    For example trash being emptied --> +1
    or note's content changed --> +1
    """
    actual_st_version = st.session_state.zot_version
    last_modified_version = st.session_state.zot.last_modified_version()

    return actual_st_version == last_modified_version


def items_uptodate():
    """Check if items are outdated

    If outdated, don't execute any update-functions
    """

    zot = st.session_state.zot
    vs = zot.item_versions()

    vc = {}
    for item in st.session_state.zot_items:
        vc[item["key"]] = item["data"]["version"]

    vs_reduced = {k: vs[k] for k in vc.keys()}
    print("----")
    print("vc: ", len(vc), vc)
    print("vs: ", len(vs), vs)
    print("vs_reduced: ", len(vs_reduced), vs_reduced)
    print(vc == vs_reduced)
    return vc == vs_reduced


# def uptodate():
#     """Check if library is outdated

#     If outdated, don't execute any update-functions
#     """
#     most_recent_item_on_server = st.session_state.zot.top(limit=1)[0]
#     first_item_in_cache = st.session_state.zot_items[0]

#     v1 = most_recent_item_on_server["data"]["version"]
#     v2 = first_item_in_cache["data"]["version"]
#     print("v1", v1)
#     print("v2", v2)
#     return v1 == v2


def update_tags(pl2,
                update_tags_z,
                update_tags_n,
                update_tags_m,
                update_tags_d):
    """
    Update special items with some tags (suspecious, nopdf, multiple pdf, duplicate)
    """

    new_tags = set_new_tag(update_tags_z,
                           update_tags_n,
                           update_tags_m,
                           update_tags_d)
    changed = []
    if not new_tags:
        pl2.info(":heavy_check_mark: Tags of the library are not changed.")
    else:
        pl2.warning(":red_circle: Updating tags ...")

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
            pl2.warning(":warning: Library updated. You may want to re-load it")
        else:
            pl2.info(":heavy_check_mark: Tags of the library are not changed.")


def init_update_delete_lists():
    DELETE_OWN_ATTACHMENTS = False  # @todo add option to ui
    zot = st.session_state.zot
    lib_items = st.session_state.zot_items
    by_doi = get_items_by_doi_or_isbn(lib_items)
    delete_items = []
    update_items = []
    for _, items in by_doi.items():
        if len(items) == 1:
            continue

        # sort by age. oldest first
        items.sort(key=date_added)
        # keep oldest item
        keep = items[0]
        # keep latest attachments
        keep_cs = zot.children(keep["key"])
        duplicates_have_pdf = False
        for item in items[-1:0:-1]:
            cs = zot.children(item["key"])
            if cs:
                for c in cs:
                    c["data"]["parentItem"] = keep["key"]
                    if attachment_is_pdf(c):
                        duplicates_have_pdf = True

                update_items.extend(cs)
                if DELETE_OWN_ATTACHMENTS and duplicates_have_pdf:
                    delete_items.extend(keep_cs)

                break  # cause, only the newest attachements are added

        delete_items.extend(items[1:])
    return update_items, delete_items


def delete_duplicate_items(pl2):
    update_duplicate_items_state()
    zot = st.session_state.zot
    deleted_or_updated = False
    update_items, delete_items = init_update_delete_lists()

    if update_items:
        with mylog.st_stdout("success"), mylog.st_stderr("code"):
            logging.info("Updating library ...")

    # update first, so we don't delete parents of items we want to keep
    for update_item in update_items:
        zot.update_item(update_item)
        log_title(update_item)
        deleted_or_updated = True

    if delete_items:
        with mylog.st_stdout("success"), mylog.st_stderr("code"):
            logging.info("Deleting from library ...")

    #  now delete: DANGER AREA!
    for delete_item in delete_items:
        zot.delete_item(delete_item)
        log_title(delete_item)
        deleted_or_updated = True

    # remove tag

    if not deleted_or_updated:
        pl2.info(":heavy_check_mark: Library has no duplicates!")

    force_update_duplicate_items_state()

    return deleted_or_updated


def delete_duplicate_pdf(pl2):
    pl2.info("check list of items with duplicate pdfs")
    update_duplicate_attach_state()
    deleted_attachment = False
    items_duplicate_attach = st.session_state.multpdf_items
    pdf_attachments = st.session_state.pdfs
    zot = st.session_state.zot
    for item in items_duplicate_attach:
        files = pdf_attachments[item["key"]]
        cs = zot.children(item["key"])
        if len(set(files)) == 1 and len(files) > 1:
            # some items have different pdf files, like suppl materials.
            # Should not be deleted
            # here attachments are all named the same
            # -->  a sign of duplicates
            with mylog.st_stdout("success"), mylog.st_stderr("code"):
                logging.warning(f"Proceed deleting {files} ...")

            deleted_attachment = delete_pdf_attachments(cs, pl2)

        # todo remove tag duplicate_pdf if exists
        if deleted_attachment:
            force_update_duplicate_attach_state()

    return deleted_attachment
