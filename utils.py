from collections import defaultdict
from datetime import datetime

import lovely_logger as logging
import streamlit as st
from unpywall import Unpywall
from unpywall.utils import UnpywallCredentials


def unpywall_credits(mail):
    """Setup credidentials for unpaywall

    :param mail: valid email-adress
    :type mail: str
    :returns:

    """
    try:
        UnpywallCredentials.validate_email(mail)

    except ValueError:
        st.error(f"mail-adress {mail} is not valid.")
        st.stop()

    UnpywallCredentials(mail)


DATE_FMT = "%Y-%m-%dT%XZ"


def yt_icon():
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAB2klEQVRIS8WWSy8DURTHOxMJbQgJmz5Sn4AF0qXUK76DJbGz8YiVEGzVxraWfAMrbdQSkQhfQJg+oo0FqUqjU7/TdBgyk2lrGpPcnnvPPef/v+fcc++t4ql/gUDAp6rqkK7rPYauFQnGKxh3mUzmTfwV+fH7/bOKohzR7W8F1MKngG4OklNFVs7gwUVwg69ANGElFApFCOnCpZX/gAE3IgRROmftICCCiX8jKBJRio1/Rpaq1eoLsmKKUmWuV8bMddP6GEcZyn5+fXYRVDAeS6fTN82kjWIZwf6Kphp+dgQJymumGXDDFpIE/SkngjgEi78JcA6jf5Ss2JFjE2duwYkgBtCaBcEeqRunrWualrIi4cDGmF9xItiBYMuKAN1qXX9CaS/lcrl7sx0RbDPe/CuBRtXsZrPZQ4DMleVplMAyRcFgcAPgMpVxQIpKNinaJ0XLThFYbnIjVUUEEtW8E0GSPZhuBNBin5LoJp0IdFIRIcfXzZBQQaOk5xIfx4MmuO+0cxyekHJVlJFF5IdMou9A+JCdVFMXUt4RWbnXvKh/veyayY6trRFB2x8cL3mUJ3PAlWV/g+SJYLD26FO/cnseu0iSB0se/USNQD6eTqmAYTf+toBza5z2T0qH/Q2OKb2sAAAAAElFTkSuQmCC"


def manual():
    return st.markdown(
        """
        **Tag library items:**
          - Items with duplicate pdf-files: `duplicate_pdf`
          - Items *without* pdf-files: `nopdf`
          - Items with *libraryCatalog* \"Zotero\": `todo_catalog`
          - Duplicate items: `duplicate_item`
        :red_circle: **NOTE**: These options need to calculate some lists
        in case these are still empty, e.g.,
        the list of items with duplicate pdf attachments.

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
            Duplicate items are identified based on their DOI and/or ISBN.

        Description:
          - Sort the Items with respect to added time (oldest first)
          - Keep the oldest `Item` (first added), i.e., $I_1$
          - Move all attachments of the newest `Item` to $I_1$
          - Delete other items, including their attachments ($I_2$ and $I_3$)

         The result of the actions described above is:

         - $I_1$ having 3 attachments
         - $PDF_1$, $NOTE_3$, $PDF_3$

        ---

        **Remove duplicate pdf files**

        Some items have duplicate pdf files, e.g. `[file1.pdf, file1.pdf]`.
        In this case (all attachments are pdf files with the same name)
        only one attachment will be kept.

        :red_circle: **NOTE:**
            Nothing will be deleted if the pdf files have different names.  
        This might be the case of items, for example,
        supplementary materials nebst the actual pdf file.
        """
    )


def howto():
    return st.markdown(
        """
        **Config file**

        The following parameters should be defined, before using this app:
        - the `library_id`: This can be found by opening the
          [group](https://www.zotero.org/groups)’s page
          and hovering over the group settings link.
        - the `api_key`: Can be found from
          [here](https://www.zotero.org/settings/keys/new).
        - `library_type`:
           - own Zotero library --> user (*no tested*)
           - shared library --> group (*recommended*)

        You can define all this necessary information in a config file.

        :point_right:
        [Here](https://github.com/chraibi/maintain-zotero/blob/main/config_template.cfg)
        is an example to use.

        ---

        :warning: **Before changing the library**

        If you intend to change the Zotero library with
        this app, then

        - **Backup first.**
           See How to
           [locate, back up, and restore](https://www.zotero.org/support/zotero_data)
           your `Zotero` library data.
        -  Disable sync in your desktop client before using it.
           You can sync the group manually by right-clicking
           on it in your Zotero client.
        """
    )


def about():

    msg = st.markdown(
        """ This app offers several functionalities
    to ease the maintenance of Zotero libraries.

    Some functionalities are **read-only** from an online Zotero library
    and produce reports.

    Others, however, **change** the online Zotero library.
    These can not be executed if the library is not in sync.
    """
    )

    return msg


def date_added(_item):
    return datetime.strptime(_item["data"]["dateAdded"], DATE_FMT)


def get_item(key, _items):
    """Get item by key

    :param key: key of item
    :type key: str
    :param _items: Zotero items
    :type _Items: list of dicts
    :returns: dict

    """
    for item in _items:
        if item["key"] == key:
            return item


def attachment_is_pdf(_child):
    """
    True if item is pdf

    Criteria according to this url
    # https://www.zotero.org/support/dev/web_api/v3/file_upload

    :param _child:
    :type _child:
    :return: True is pdf

    """

    return (
        _child["data"]["itemType"] == "attachment"
        and _child["data"]["contentType"] == "application/pdf"
        and _child["data"]["linkMode"]
        in ["imported_file", "linked_file", "imported_url"]
    )


def get_suspecious_items(_items):
    """Items with libraryCatalog==Zotero

    These items are suspecious, cause they were imported from
    pdf files and maybe Zotero did not import the metadata properly.

    :param _items: Zotero library items
    :type _items: list containing dicts
    :returns: list containing dicts

    """

    list_catalog_zotero = []
    for item in _items:
        if "libraryCatalog" in item["data"]:
            catalog = item["data"]["libraryCatalog"]
            if catalog == "Zotero":
                list_catalog_zotero.append(item)

    return list_catalog_zotero


def get_items_with_duplicate_pdf(_zot, _items):
    """Items having several identical pdf files and their pdf files

    :param _zot: A Zotero instance
    :type _zot: pyzotero.zotero.Zotero
    :param _items: Zotero library items
    :type _items: list containing dicts
    :returns: (list containing dicts, dict containing lists)

    """
    _items_duplicate_attach = []
    _pdf_attachments = defaultdict(list)
    for _item in _items:
        if is_standalone(_item):
            continue

        key = _item["key"]
        cs = st.session_state.children[key]
        for c in cs:
            if attachment_is_pdf(c):
                _pdf_attachments[key].append(c["data"]["filename"])

        if len(_pdf_attachments[key]) > 1:
            _items_duplicate_attach.append(_item)

    return _items_duplicate_attach, _pdf_attachments


def get_items_with_no_pdf_attachments2(_items):
    """Items with no pdf file

    :type _items: list containing dicts
    :returns: list containing dicts

    """

    _items_without_attach = []
    for item in _items:
        if is_standalone(item) or is_file(item):
            continue

        if "attachment" in item["links"]:
            attach_type = item["links"]["attachment"]["attachmentType"]
            if attach_type != "application/pdf":
                _items_without_attach.append(item)

        else:
            _items_without_attach.append(item)

    return _items_without_attach


# def get_items_with_no_pdf_attachments(_zot, _items):
#     """Single Items with no attachments

#     :param _zot: A Zotero instance
#     :type _zot: pyzotero.zotero.Zotero
#     :param _items: Zotero library items
#     :type _items: list containing dicts
#     :returns: list containing dicts

#     """

#     _items_without_attach = []
#     for _item in _items:
#         has_attach = False
#         if is_standalone(_item):
#             continue

#         key = _item["key"]
#         cs = st.session_state.children[key]
#         for c in cs:
#             if attachment_is_pdf(c):
#                 has_attach = True
#                 break

#         if not has_attach:
#             _items_without_attach.append(_item)

#     return _items_without_attach


def get_standalone_items(_items):
    """Standalone items with no metadata (notes, pdfs, etc)

    :param _items: Zotero library items
    :type _items: list containing dicts
    :returns: list of dicts

    """

    standalone = []
    for _item in _items:
        if is_standalone(_item):
            standalone.append(_item)

    return standalone


def is_file(_item):
    """Definition of a file item

    :param _item: Zotero library item
    :type _item: dict
    :returns: True if file

    """
    return _item["data"]["itemType"] in ["note", "attachment", "annotation"]


# zot.item_types()
def is_book(_item):
    """item is book

    :param _item: Zotero library item
    :type _item: dict
    :returns: True of book or  bookSection

    """
    return _item["data"]["itemType"] in ["book", "bookSection"]


def is_misc(_item):
    """item is report, thesis or document

    :param _item: Zotero library item
    :type _item: dict
    :returns: Bool

    """
    return _item["data"]["itemType"] in ["thesis", "report", "document"]


def is_article(_item):
    """Item is an article

    :param _item: Zotero library item
    :type _item: dict
    :returns: True if conf, encyArt or journalArt

    """
    return _item["data"]["itemType"] in [
        "conferencePaper",
        "encyclopediaArticle",
        "journalArticle",
    ]


def is_standalone(_item):
    """Definition of a standalone item

    :param _item: Zotero library item
    :type _item: dict
    :returns: True if standalone

    """
    # Zotero 6 write annotations in pdfs as a standalone item with parent being
    # the pdf file!

    return _item["data"]["itemType"] in ["note", "attachment", "annotation"] and \
        "parentItem" not in _item["data"]


def retrieve_data(_zot, _num_items):
    """Retrieve <num_items> top-level Zotero library items.

    :param _zot: A Zotero instance
    :type _zot: pyzotero.zotero.Zotero
    :param _num_items: Number if items to retrieve
    :type _num_items: int
    :returns: list of dicts

    """
    msg = st.empty()
    logging.info(f"retrieve_data. trying to get {_num_items} items")
    limit = 100  # determined by the API
    start = 0
    lib_items = []
    count = 1
    step = int(limit * 100 / _num_items)
    read_items = 0
    my_bar = st.progress(0)
    while read_items < _num_items:
        progress_by = (count + 1) * step
        count += 1
        try:
            lib_items.extend(_zot.items(limit=limit, start=start))
        except Exception as e:
            logging.error(f"Could not retrive data with error {str(e)}")
            st.stop()

        read_items += limit
        start = start + limit
        if _num_items - read_items < limit:
            progress_by = 100

        logging.info(f"read {len(lib_items)} / {_num_items} items")
        msg.info(f"read {len(lib_items)} / {_num_items} items")
        my_bar.progress(progress_by)

    return lib_items


def trash_is_empty(_zot):
    """Is trash empty?
    :todo: Maybe return len
    :param _zot: A Zotero instance
    :type _zot: pyzotero.zotero.Zotero

    :returns: True if empty

    """

    return len(_zot.trash()) == 0


def get_time(t):
    """Time in min sec

    :param t: Run time
    :type t: float
    :returns: str

    """

    minutes = t // 60
    seconds = t % 60
    return f"""{minutes:.0f} min:{seconds:.0f} sec"""


def duplicates_by_title(_items):
    """Duplicate items by Title

    Some items do not have DOI not ISBN.
    This functions compares items by title

    :todo: Similar to duplicates_by_doi.
    :todo: Return items not titles
    :param _items: Zotero library items
    :type _items: list containing dicts

    :returns: list of str (titles)

    """
    duplicate_items_by_title = defaultdict(list)
    duplicates = []
    for item in _items:
        if is_standalone(item):
            continue

        iType = item["data"]["itemType"]
        Title = item["data"]["title"]
        duplicate_items_by_title[iType].append(Title.capitalize())

    for _type, _titles in duplicate_items_by_title.items():
        num_duplicates_items = len(_titles) - len(set(_titles))
        if num_duplicates_items:
            duplicates = {x for x in _titles if _titles.count(x) > 1}

    return duplicates


def duplicates_by_doi(_items):
    """Duplicate items by DOI/ISBN

    Items are sorted by DOI/ISBN and then duplicates
    are returned.

    Similar to duplicates_by_title().

    :param _items: Zotero library items
    :type _items: list containing dicts
    :returns: list of dicts

    """

    by_doi = get_items_by_doi_or_isbn(_items)
    result = []
    for _, items in by_doi.items():
        if len(items) > 1:
            for i in items:
                result.append(i)

    return result


# @todo: separate doi from isbn
# doi and issn for papers
# isbn for books and book sections


def _get_books_without_isbn(_items):
    # item['data']['itemType']
    # = book, bookSection
    # item['data']['title']
    return


def get_items_by_isbn(_items):
    return


def duplicates_by_isbn(_items):
    return


def doi_to_item(dois):
    """return items to a list of dois

    :param dois: DOI numbers
    :type dois: list of str
    :returns: items with DOIS

    """
    items = []
    for doi in dois:
        for _item in st.session_state.zot_items:
            if is_standalone(_item) or is_file(_item):
                continue

            if "DOI" in _item["data"]:
                doi_item = _item["data"]["DOI"]                
                if doi_item.lower() == doi.lower():
                    items.append(_item)
                    continue

    return items


def get_items_by_doi(_items):
    """Items having a DOI

    :param _items: Zotero library items
    :returns: dict of lists

    """

    _items_by_doi = defaultdict(list)
    for _item in _items:
        if is_standalone(_item) or is_file(_item):
            continue

        if "DOI" in _item["data"]:
            doi = _item["data"]["DOI"]
            if doi:
                _items_by_doi[doi].append(_item)

    return _items_by_doi


def get_items_by_doi_or_isbn(_items):
    """Items having a DOI and/or ISBN

    :param _items: Zotero library items
    :returns: dict of lists

    """

    _items_by_doi_isbn = defaultdict(list)
    for _item in _items:
        if is_standalone(_item) or is_file(_item):
            continue

        if "DOI" in _item["data"]:
            doi = _item["data"]["DOI"]
            if doi:
                _items_by_doi_isbn[doi].append(_item)

        elif "ISBN" in _item["data"]:
            isbn = _item["data"]["ISBN"]
            if isbn:
                _items_by_doi_isbn[isbn].append(_item)

    return _items_by_doi_isbn


def get_items_with_empty_doi_or_isbn(_items):
    """
    Articles with no DOI. Books with no ISBN.

    :param _items: Zotero library items
    :type _items: list containing dicts
    :return: list of dicts
    """

    empty_items = []
    for _item in _items:
        if is_standalone(_item) or is_file(_item):
            continue

        if is_article(_item):
            _field = "DOI"

        elif is_book(_item):
            _field = "ISBN"

        elif is_misc(_item):
            logging.warning(f"Misc {_item['data']['itemType']}")
        else:
            logging.warning(f"Type of item not known {_item['data']['itemType']}")
            st.warning(f"Type of item not known {_item['data']['itemType']}")

        if _field in _item["data"]:
            if not _item["data"][_field]:
                empty_items.append(_item)

    return empty_items


def get_items_with_empty_doi_and_isbn(_items, _fields):
    """
    Items with no DOI and no ISBN.

    :param _items: Zotero library items
    :type _items: list containing dicts
    :param _fields: DOI and ISBN
    :type _fields: list of str
    :return: list of dict

    """
    empty = []
    for _item in _items:
        result = []
        if is_standalone(_item) or is_file(_item):
            continue

        for field in _fields:
            if field in _item["data"]:
                f = _item["data"][field]
                if not f:
                    result.append(False)
                else:
                    result.append(True)

        if not any(result):
            empty.append(_item)

    return empty


def delete_pdf_attachments(_children, pl2):
    """Delete pdf attachments of an item and keep only one.

    This functions changes the online Zotero library!

    :param _children: Children items of a specific item
    :type _children: list of dicts
    :param pl2: placeholder to print messages
    :type pl2: st.empty()
    :returns: True if an attachment has been deleted.

    """

    deleted_attachment = False
    zot = st.session_state.zot
    for child in _children[1:]:
        if not attachment_is_pdf(child):
            continue  # only for pdf files.

        pl2.warning(f"deleting {child['data']['filename']}")
        logging.warning(f"deleting {child['data']['filename']}")
        zot.delete_item(child)
        deleted_attachment = True

    return deleted_attachment


def log_title(_item):
    """Log title of an item

    :param _item: Zotero library item
    :type _item: dict
    :returns: st.code

    """

    if is_standalone(_item):
        ttt = f"Standalone item of type: <{_item['data']['itemType']}>"
        if "filename" in _item["data"]:
            ttt += f" ({_item['data']['filename']})"
    else:
        ttt = f"{_item['data']['title']}"

    st.code(f"{ttt}")
    logging.info(f"{ttt}")


def set_new_tag(z, n, m, d, o, mail=""):
    """Prepare list of tags to be added to items

    We have to add the tags to items at once.
    Otherwise, we will have to update the library!

    This function may update the session_state of some lists
    (if session_state lists are empty)

    These lists are:
    - suspecious_items
    - multpdf_items
    - nopdf_items
    - doi_dupl_items

    :param z: Suspecious items
    :type z: Bool
    :param n: Items with no pdf
    :type n: Bool
    :param m: Items with multiple pdf
    :type m: Bool
    :param d: Duplicate items
    :type d: Bool
    :param o: open-access articles
    :type o: Bool
    :returns: dict of lists

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

        for item in duplicate_items:
            new_tags[item["data"]["key"]].append("duplicate_item")

    if o:
        unpywall_credits(mail)
        items_by_doi = get_items_by_doi(st.session_state.zot_items)
        pl = st.empty()
        with st.spinner("Initializing ..."):
            OA_items, _ = get_oa_ca(items_by_doi, pl)
        
        items = doi_to_item(OA_items)
        
        for item in items:
            new_tags[item["data"]["key"]].append("open-access")

    return new_tags


def add_tag(tags_to_add, _zot, _item):
    """Add tags to Zotero items

    This function changes the online library

    :todo: use zot from session_state
    :param tags_to_add: dict prepared in set_new_tag()
    :type tags_to_add: dict of lists
    :param _zot: A Zotero instance
    :type _zot: pyzotero.zotero.Zotero
    :param _item: Zotero library item
    :type _item: dict
    :returns: True if changes have been made

    """
    if not tags_to_add or is_standalone(_item) and is_file(_item):
        return False

    title = _item["data"]["title"]
    item_tags = [t["tag"] for t in _item["data"]["tags"]]
    new_tags = [t for t in tags_to_add if t not in item_tags]

    if not new_tags:
        return False

    logging.info(f"add tags {new_tags} to {title}")
    _zot.add_tags(_item, *new_tags)
    return True


def update_suspecious_state():
    """update suspecious_items"""
    if not st.session_state.suspecious_items:
        items = get_suspecious_items(st.session_state.zot_items)
        st.session_state.suspecious_items = items


# @todo check if state variable need to be used as input for functions
def update_duplicate_attach_state():
    """First update of lists related to multiple pdfs

    - multpdf_items
    - pdfs
    - init_multpdf_items

    """
    if not st.session_state.init_multpdf_items:
        items, pdfs = get_items_with_duplicate_pdf(
            st.session_state.zot, st.session_state.zot_items
        )

        st.session_state.multpdf_items = items
        st.session_state.pdfs = pdfs
        st.session_state.init_multpdf_items = True


def force_update_duplicate_attach_state():
    """Update of lists related to multiple pdfsrelated to multiple pdfs

    - multpdf_items
    - pdfs
    - init_multpdf_items

    """
    items, pdfs = get_items_with_duplicate_pdf(
        st.session_state.zot, st.session_state.zot_items
    )

    st.session_state.multpdf_items = items
    st.session_state.pdfs = pdfs
    st.session_state.init_multpdf_items = True


def update_duplicate_items_state():
    """First update of duplicate items by doi"""
    if not st.session_state.init_doi_dupl_items:
        duplicates = duplicates_by_doi(st.session_state.zot_items)
        st.session_state.doi_dupl_items = duplicates
        st.session_state.init_doi_dupl_items = True


def force_update_duplicate_items_state():
    """First update of duplicate items by doi"""

    duplicates = duplicates_by_doi(st.session_state.zot_items)
    st.session_state.doi_dupl_items = duplicates
    st.session_state.init_doi_dupl_items = True


def update_without_pdf_state():
    """First update of items without pdf"""
    if not st.session_state.nopdf_items:
        items = get_items_with_no_pdf_attachments2(st.session_state.zot_items)

        st.session_state.nopdf_items = items


def uptodate():
    """Check if library is up to date

    every change in Zotero-Library increments
    the version number by one.
    For example, trash being emptied --> +1
    or note's content changed --> +1

    :return: True if up-to-date
    """

    actual_st_version = st.session_state.zot_version
    last_modified_version = st.session_state.zot.last_modified_version()

    return actual_st_version == last_modified_version


def items_uptodate():
    """Check if items are outdated

    If outdated, don't execute any update-functions

    :todo: not used
    :return: True if all up-to-date
    """

    zot = st.session_state.zot
    vs = zot.item_versions()

    vc = {}
    for item in st.session_state.zot_items:
        vc[item["key"]] = item["data"]["version"]

    vs_reduced = {k: vs[k] for k, _ in vc.items()}
    logging.info("----")
    logging.info(f"vc: {len(vc)}, {vc}")
    logging.info(f"vs: {len(vs)}, {vs}")
    logging.info(f"vs_reduced: {len(vs_reduced)}, {vs_reduced}")
    logging.info(vc == vs_reduced)
    return vc == vs_reduced


def update_tags(pl2, update_tags_z, update_tags_n, update_tags_m, update_tags_d, update_tags_o, mail):
    st.info("update_tags")
    """

    A wrapper function  of add_tag()

    :param pl2: placeholder to print messages
    :type pl2: st.empty()
    :param update_tags_z: Suspecious items
    :type update_tags_z: Bool
    :param update_tags_n: Items with no pdf
    :type update_tags_n: Bool
    :param update_tags_m: Items with multiple pdf
    :type update_tags_m: Bool
    :param update_tags_d: Duplicte items
    :type update_tags_d: Bool
    :param update_tags_o: Open-access articles
    :type update_tags_: Bool
    :param mail: mail necessary to fetch open-access articles

    """
    new_tags = set_new_tag(update_tags_z, update_tags_n, update_tags_m, update_tags_d, update_tags_o, mail)
    changed = []
    msg = st.empty()

    if not new_tags:
        pl2.info(":heavy_check_mark: Tags of the library are not changed.")
    else:
        pl2.warning(":red_circle: Updating tags ...")
        my_bar = st.progress(0)
        for i, item in enumerate(st.session_state.zot_items):            
            msg.info(f"process {i} / {st.session_state.zot_items}")
            progress_by = (i + 1) / st.session_state.num_items
            my_bar.progress(progress_by)
            ch = add_tag(
                new_tags[item["data"]["key"]],
                st.session_state.zot,
                item,
            )
            changed.append(ch)

        if any(changed):
            pl2.warning(
                """:warning: Library updated.
            You may want to sync!"""
            )
        else:
            pl2.info(":heavy_check_mark: Tags of the library are not changed.")


def init_update_delete_lists():
    """Initialize Items to update/delete

    Prepare some lists of items to be updated and deleted

    Note:
    - Duplicates without DOI not ISBN numbers are going to be ignored!
    - Duplicates with different DOI or ISBN will be missed as well!
      (e.g. ISBN=0968-090X and ISBN=0968090X)

    :returns: (update list, delete list)

    """
    DELETE_OWN_ATTACHMENTS = False  # @todo add option to ui
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
        keep_cs = st.session_state.children[keep["key"]]
        duplicates_have_pdf = False
        for item in items[-1:0:-1]:
            cs = st.session_state.children[item["key"]]
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
    """Delete duplicate items

    Uses the update and delete lists
    calculated in init_update_delete_lists()

    if deleted, remove the tag "duplicate_item"

    :param pl2: placeholder to print messages
    :type pl2: st.empty()

    :returns: True if items have been deleted and updated

    """
    update_duplicate_items_state()
    zot = st.session_state.zot
    deleted_or_updated = False
    update_items, delete_items = init_update_delete_lists()

    if update_items:
        st.code("Deleting duplicate items ...")

    # update first, so we don't delete parents of items we want to keep
    for update_item in update_items:
        log_title(update_item)
        zot.update_item(update_item)
        deleted_or_updated = True

    if delete_items:
        st.code("Deleting from library ...")
        logging.info("Deleting from library ...")

    #  now delete: DANGER AREA!
    for delete_item in delete_items:
        log_title(delete_item)
        zot.delete_item(delete_item)
        deleted_or_updated = True

    # remove tag

    if not deleted_or_updated:
        pl2.info(":heavy_check_mark: Library has no duplicates!")
        logging.info(":heavy_check_mark: Library has no duplicates!")
    else:
        zot.delete_tags("duplicate_item")

    force_update_duplicate_items_state()

    return deleted_or_updated


def delete_duplicate_pdf(pl2):
    """Delete duplicate pdf files

    This function is slow since it iterates over the children of the items
    (network traffic)

    If an item has several pdf files with the same name,
    then delete them and keep one. In that case, delete the tag (duplicate_pdf)
    If an item has several pdf files with different names,
    then don't delete anything.

    :param pl2: placeholder to print messages
    :type pl2: st.empty()
    :returns: True if items have been deleted

    """
    pl2.info("check list of items with duplicate pdfs")
    update_duplicate_attach_state()
    deleted_attachment = False
    items_duplicate_attach = st.session_state.multpdf_items
    pdf_attachments = st.session_state.pdfs
    zot = st.session_state.zot
    for item in items_duplicate_attach:
        files = pdf_attachments[item["key"]]
        cs = st.session_state.children[item["key"]]
        if len(set(files)) == 1 and len(files) > 1:
            # some items have different pdf files, like suppl materials.
            # Should not be deleted
            # here attachments are all named the same
            # -->  a sign of duplicates
            st.info(f"Proceed deleting {files} ...")
            logging.info(f"Proceed deleting {files} ...")
            deleted_attachment = delete_pdf_attachments(cs, pl2)

        if deleted_attachment:
            zot.delete_tags("duplicate_pdf")
            force_update_duplicate_attach_state()

    return deleted_attachment


def get_children():
    """Return Zotero children of items

    @todo: optimize the second loop
    :param _items: Zotero items
    :type _items: list of dict
    :returns: list of dict

    """
    _items = st.session_state.zot_items
    diff = defaultdict(list)
    pk = defaultdict(list)
    for i, item in enumerate(_items):
        if is_standalone(item) or is_file(item):
            continue

        key = item["key"]
        if "numChildren" not in item["meta"]:
            item_type = item["data"]["itemType"]
            logging.warning(f"What a type: <{item_type}>")
            continue

        if item["meta"]["numChildren"] == 0:
            pk[key] = []
            diff[key] = 100
            continue

        # children should be near their parents
        # @todo maybe optimize this loop later!
        for k, child in enumerate(_items):
            if "parentItem" in child["data"]:
                if child["data"]["parentItem"] == key:
                    pk[key].append(child)
                    diff[key] = abs(k - i)

    return pk


# https://support.unpaywall.org/support/solutions/articles/44001900286
# Which DOIs does Unpaywall cover?
# The Unpaywall dataset only covers articles issued by one: Crossref.
# We used to include DataCite DOIs, but we don't anymore.
# In practice we added very little value because almost everything
# with a DataCite DOI is OA.
def get_oa_ca(_dois, pl2):
    dois = list(_dois.keys())
    try:
        articles = Unpywall.doi(dois=dois, errors="ignore", progress=True)
    except Exception as e:
        pl2.error(f"Connection error to Unpaywall {str(e)}")
        logging.info(str(e))

    oa_dois = list(articles["doi"][articles["is_oa"]])
    ca_dois = list(articles["doi"][~articles["is_oa"]])    
    return oa_dois, ca_dois
