import configparser
import time
from collections import defaultdict

import streamlit as st
from PIL import Image
from pyzotero import zotero

import utils

st.set_page_config(
    page_title="Zotero Sanity Checks",
    page_icon=":mortar_board:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/chraibi/maintain-zotero",
        "Report a bug": "https://github.com/chraibi/maintain-zotero/issues",
        "About": "## Zotero Sanity Checks\n :copyright: Mohcine Chraibi",
    },
)


def progress(max_run, my_bar):
    """
    progress bar

    :return:
    """

    step = int(100 / max_run)
    for i in range(max_run):
        progress_by = (i + 1) * step
        if i == max_run - 1:
            progress_by = 100

        my_bar.progress(progress_by)


def update_session_state():
    # st.session_state.versions = {}
    # {key:version} of all elements (items+children)
    st.session_state.zot_version = st.session_state.zot.last_modified_version()
    st.session_state.num_items = st.session_state.zot.num_items()
    st.session_state.multpdf_items = []
    st.session_state.init_multpdf_items = False
    st.session_state.pdfs = defaultdict(list)
    st.session_state.nopdf_items = []
    st.session_state.suspecious_items = []
    st.session_state.doi_dupl_items = []
    st.session_state.init_doi_dupl_items = False
    st.session_state.no_doi_isbn_items = []


if __name__ == "__main__":
    # if "items_versions" not in st.session_state:
    #     st.session_state.items_versions = {}

    if "zot" not in st.session_state:
        st.session_state.zot = ""

    if "zot_version" not in st.session_state:
        st.session_state.zot_version = 0

    if "num_items" not in st.session_state:
        st.session_state.num_items = 0

    if "lib_loaded" not in st.session_state:
        st.session_state.lib_loaded = False

    if "zot_items" not in st.session_state:
        st.session_state.zot_items = []

    if "suspecious_items" not in st.session_state:
        st.session_state.suspecious_items = []

    if "nopdf_items" not in st.session_state:
        st.session_state.nopdf_items = []

    if "multpdf_items" not in st.session_state:
        st.session_state.multpdf_items = []

    if "init_multpdf_items" not in st.session_state:
        st.session_state.init_multpdf_items = False

    if "pdfs" not in st.session_state:
        st.session_state.pdfs = defaultdict(list)

    if "doi_dupl_items" not in st.session_state:
        st.session_state.doi_dupl_items = []

    if "init_doi_dupl_items" not in st.session_state:
        st.session_state.init_doi_dupl_items = []

    if "no_doi_isbn_items" not in st.session_state:
        st.session_state.no_doi_isbn_items = []

    # UI --------------------------------
    image = Image.open("logo.png")
    st.sidebar.image(image, use_column_width=True)
    gh = "https://badgen.net/badge/icon/GitHub?icon=github&label"
    repo = "https://github.com/chraibi/maintain-zotero"
    report_name = f"[![Repo]({gh})]({repo})"
    st.sidebar.markdown(report_name, unsafe_allow_html=True)
    st.sidebar.markdown("-------")
    st.title(":mortar_board: Maintaining Zotero libraries")
    st.header("")
    h1, _, h2, _, h3 = st.columns((7, 1, 7, 1, 7))
    h1.markdown("##### :information_source: About")
    with h1.expander("", expanded=False):
        utils.about()

    h2.markdown("##### 	:speech_balloon: How to use")
    with h2.expander("", expanded=False):  # @todo: more
        utils.howto()

    h3.markdown("##### :round_pushpin: Features")
    with h3.expander("", expanded=False):  # @todo: more
        utils.manual()

    config_file = st.sidebar.file_uploader(
        "📙Choose a config file ",
        type=["cfg", "txt"],
        help="Load config file with group ID, API-key and library type",
    )
    placeholder = st.sidebar.empty()
    st.sidebar.markdown("-------")
    msg_status = st.sidebar.empty()
    if config_file:
        configFilePath = config_file.name
        try:
            confParser = configparser.RawConfigParser()
            confParser.read(configFilePath)
            library_id = int(confParser.get("zotero-config", "library_id"))
            api_key = confParser.get("zotero-config", "api_key")
            library_type = confParser.get("zotero-config", "library_type")
        except Exception as e:
            msg_status.error(
                f"""Can't parse the config file.
                Error: {e}"""
            )
            st.stop()

        if not st.session_state.num_items:
            st.session_state.zot = zotero.Zotero(library_id, library_type, api_key)

            st.session_state.num_items = st.session_state.zot.num_items()
            st.session_state.zot_version = st.session_state.zot.last_modified_version()
            msg_status.success("Config loaded!")


        update_library = placeholder.button("🔁 Sync Library")
        if update_library:
            placeholder.empty()
            msg_status.info(
                """:heavy_check_mark: Library synced!
                You can load items!"""
            )
            update_session_state()

        lf = st.form("load_form")
        max_items = lf.slider(
            "Select items to retrieve from library",
            min_value=1,
            max_value=st.session_state.num_items,
            value=st.session_state.num_items,
            key="config_form",
            help="""Number of the most recently modified library items
            to retrieve (the more the slower!)""",
        )
        load_library = lf.form_submit_button(label="➡️ Load library")
        if load_library:
            # update num of items when load
            update_session_state()
            msg_status.info(f"Retrieving {max_items} items from library ...")
            t1 = time.process_time()
            with st.spinner("Loading ..."):
                st.session_state.zot_items = utils.retrieve_data(
                    st.session_state.zot, max_items
                )

            t2 = time.process_time()
            st.session_state.lib_loaded = True
            msg_time = utils.get_time(t2 - t1)
            msg_status.info(f"Items loaded in {msg_time}")

        if st.session_state.lib_loaded:
            config = st.form("config_form")
            with config:
                c1, c2 = st.columns((1, 1))
                c1.write("**Report options**")
                c2.write("**Update options**")
                update_tags_z = c2.checkbox(
                    "Update Tags of suspecious items", help="add tag todo_catalog"
                )
                update_tags_n = c2.checkbox(
                    "Update Tags of items with no pdf", help="add tag nopdf"
                )
                update_tags_m = c2.checkbox(
                    "Update Tags of items with multiple pdf",
                    help="add tag duplicate_pdf",
                )
                update_tags_d = c2.checkbox(
                    "Update Tags of duplicate items",
                    help="add tag duplicate_item",
                )
                head = c1.checkbox(
                    "Head", help="""Show titles of at most the first 10 items"""
                )
                report_duplicates = c1.checkbox(
                    "Duplicate Items (DOI/ISBN)",
                    help="""Duplicate items based on
                    DOI/ISBN""",
                )
                report_duplicates_title = c1.checkbox(
                    "Duplicate Items (Title)",
                    help="""Duplicate items based on
                    title""",
                )

                delete_duplicates = c2.checkbox(
                    "Merge Duplicate Items",
                    help="""Duplicate items based on
                    DOI/ISBN and merge them""",
                )
                report_duplicate_pdf = c1.checkbox(
                    "Items with Multiple PDF",
                    help="""Items having more than
                    one pdf file (first run is slow!)""",
                )
                report_without_pdf = c1.checkbox(
                    "Items without PDF",
                    help="""Items having no pdf files""",
                )
                report_standalone = c1.checkbox(
                    "Standalone items",
                    help="""Standlalone items like
                    PDF or Notes""",
                )
                delete_duplicate_pdf = c2.checkbox(
                    "Delete Multiple PDF",
                    help="""If item has multiple pdf files
                    with
                    the same name, then keep only
                    one pdf.""",
                )
                report_no_doi_isbn = c1.checkbox(
                    "DOI & ISBN", help="Show items with no doi and no isbn"
                )

                suspecious = c1.checkbox(
                    "Suspecious items",
                    help="""Items with libraryCatalog = Zotero""",
                )
                trash = c1.checkbox(
                    "Trash status", help="""Does not require reloading library"""
                )
                start = config.form_submit_button(label="🚦Start")
                pl2 = st.empty()
                if start:
                    if not utils.uptodate():
                        msg_status.error(":fire: Library is out of sync.")

                    if head:
                        num_head = 10
                        st.info(f"Top {num_head} items")
                        for item in st.session_state.zot_items[:num_head]:
                            utils.log_title(item)

                    if trash:
                        trash_empty = utils.trash_is_empty(st.session_state.zot)
                        if trash_empty:
                            st.info(":heavy_check_mark: Trash is empty!")
                        else:
                            st.warning(":x: Trash is not empty!")

                    if report_duplicates_title:
                        duplicates = utils.duplicates_by_title(
                            st.session_state.zot_items
                        )

                        if duplicates:
                            st.warning(f":x: Duplicate items: {len(duplicates)}")
                        else:
                            st.info(":heavy_check_mark: No duplicate items found.")

                        for d in duplicates:
                            st.code(d)

                    if report_no_doi_isbn:
                        fields = ["DOI", "ISBN"]
                        if not st.session_state.no_doi_isbn_items:
                            st.session_state.no_doi_isbn_items = (
                                utils.get_items_with_empty_doi_and_isbn(
                                    st.session_state.zot_items, fields
                                )
                            )

                        if st.session_state.no_doi_isbn_items:
                            st.warning(
                                f""":x: Items with no doi and no isbn:
                                {len(st.session_state.no_doi_isbn_items)}"""
                            )
                        else:
                            st.info(
                                """:heavy_check_mark: No items without
                            doi and isbn"""
                            )

                        for d in st.session_state.no_doi_isbn_items:
                            utils.log_title(d)

                    if report_duplicates:
                        with st.spinner("processing ..."):
                            utils.update_duplicate_items_state()

                        duplicates = st.session_state.doi_dupl_items
                        if duplicates:
                            st.warning(f":x: Duplicate items: {len(duplicates)}")
                        else:
                            st.info(":heavy_check_mark: No duplicate items found.")

                        for d in duplicates:
                            utils.log_title(d)

                    # Functionalities
                    if report_standalone:
                        standalones = utils.get_standalone_items(
                            st.session_state.zot_items
                        )

                        if not standalones:
                            st.info(":heavy_check_mark: No standalone items")
                        else:
                            st.warning(
                                f"""
                            :x: Standalone item(s): {len(standalones)}"""
                            )

                        for d in standalones:
                            utils.log_title(d)

                    if report_duplicate_pdf:
                        t1 = time.process_time()
                        with st.spinner("processing ..."):
                            utils.update_duplicate_attach_state()

                        t2 = time.process_time()
                        msg_time = utils.get_time(t2 - t1)
                        msg_status.info(f"Items loaded in {msg_time}")
                        num_duplicates = len(st.session_state.multpdf_items)
                        if num_duplicates:
                            st.warning(
                                f"""":x: Items with duplicate pdf files found:
                                {num_duplicates}"""
                            )
                            for item in st.session_state.multpdf_items:
                                item_key = item["key"]
                                utils.log_title(item)
                                st.code(f"> {st.session_state.pdfs[item_key]}")
                        else:
                            st.info(
                                """:heavy_check_mark: No items with duplicate pdf attachments
                                found"""
                            )

                    if report_without_pdf:
                        t1 = time.process_time()
                        utils.update_without_pdf_state()
                        t2 = time.process_time()
                        msg_time = utils.get_time(t2 - t1)
                        msg_status.info(f"Items loaded in {msg_time}")
                        num_duplicates = len(st.session_state.nopdf_items)
                        if num_duplicates:
                            st.warning(
                                f"""
                                :x: Items with no pdf attachments:
                                {num_duplicates}"""
                            )

                            for item in st.session_state.nopdf_items:
                                utils.log_title(item)
                        else:
                            st.info(
                                """:heavy_check_mark: Items without pdf
                                attachments not found"""
                            )

                    if suspecious:
                        utils.update_suspecious_state()
                        num_suspecious = len(st.session_state.suspecious_items)

                        if num_suspecious:
                            st.warning(f":x: Suspecious items: {num_suspecious}")
                        else:
                            st.info(":heavy_check_mark: No suspecious items found")

                        for item in st.session_state.suspecious_items:
                            item_key = item["key"]
                            ttt = item["data"]["title"]
                            st.code(f"""{ttt}""")

                    if update_tags_z or update_tags_n or update_tags_m or update_tags_d:

                        if not utils.uptodate():
                            st.error(
                                """:skull_and_crossbones: Library is not
                            up-to-date."""
                            )
                        else:
                            utils.update_tags(
                                pl2,
                                update_tags_z,
                                update_tags_n,
                                update_tags_m,
                                update_tags_d,
                            )

                    if delete_duplicates:
                        if not utils.uptodate():
                            st.error(
                                """:skull_and_crossbones: Library is
                            not up-to-date."""
                            )
                        else:
                            with st.spinner("processing ..."):
                                res = utils.delete_duplicate_items(pl2)

                            if res:
                                pl2.warning(
                                    """:warning: Library updated.
                                    You may want to sync!"""
                                )
                            else:
                                st.info(
                                    """:heavy_check_mark: No duplicates to
                                delete!"""
                                )

                    if delete_duplicate_pdf:
                        if not utils.uptodate():
                            st.error(
                                """:skull_and_crossbones:
                            Library is not up-to-date."""
                            )
                        else:
                            with st.spinner("processing ..."):
                                res = utils.delete_duplicate_pdf(pl2)

                            if res:
                                pl2.warning(
                                    """:warning: Library updated.
                                    You may want to sync!"""
                                )
                            else:
                                st.info(
                                    """:heavy_check_mark:
                                Nothing to delete!"""
                                )
