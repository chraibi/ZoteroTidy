import sys
import configparser
import logging
import time
import streamlit as st
from PIL import Image
from pyzotero import zotero

import mylogging as mylog
from collections import defaultdict
import utils
import datetime as dt

st.set_page_config(
    page_title="Zotero Sanity Checks",
    page_icon=":mortar_board:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/chraibi/maintain-zotero",
        "Report a bug": "https://github.com/chraibi/maintain-zotero/issues",
        "About": "# Sanity Checks to Maintain a Zotero Library",
    },
)
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)


def demo_function2(max_run, my_bar):
    """
    Just a sample function to show how it works.
    :return:
    """

    step = int(100 / max_run)
    for i in range(max_run):
        progress_by = (i + 1) * step
        if i == max_run - 1:
            progress_by = 100

        my_bar.progress(progress_by)
        time.sleep(1)


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
    st.session_state.num_items = st.session_state.zot.num_items()
    st.session_state.lib_loaded = False
    st.session_state.multpdf_items = []
    st.session_state.pdfs = defaultdict(list)
    st.session_state.nopdf_items = []
    st.session_state.suspecious_items = []
    st.session_state.doi_dupl_items = []
    st.session_state.no_doi_isbn_items = []


if __name__ == "__main__":
    if "zot" not in st.session_state:
        st.session_state.zot = ""

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

    if "pdfs" not in st.session_state:
        st.session_state.pdfs = defaultdict(list)

    if "doi_dupl_items" not in st.session_state:
        st.session_state.doi_dupl_items = []

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
    st.title(":mortar_board: Sanity checks to maintain Zotero libraries")
    st.header("")
    st.markdown("## :information_source: About this app (expand for more)")
    with st.expander("", expanded=False):  # @todo: more
        st.header("This app reports and/or updates an online Zotero library")
        # Sanity checks
        utils.intro()

    config_file = st.sidebar.file_uploader(
        "📙Choose a config file ",
        type=["cfg", "txt"],
        help="Load config file with group ID, API-key and library type",
    )
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
            msg_status.success("Config loaded!")
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
            placeholder = st.empty()
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
                report_duplicates = c1.checkbox(
                    "Show Duplicate Items",
                    help="""Duplicate items based on
                    DOI/ISBN""",
                )
                report_duplicates_title = c1.checkbox(
                    "Show Duplicate Items (Title)",
                    help="""Duplicate items based on
                    title""",
                )

                delete_duplicates = c2.checkbox(
                    "Merge Duplicate Items",
                    help="""Duplicate items based on
                    DOI/ISBN and merge them""",
                )
                report_duplicate_pdf = c1.checkbox(
                    "Show Items with Multiple PDF",
                    help="""Items having more than
                    one pdf file (first run is slow!)""",
                )
                report_without_pdf = c1.checkbox(
                    "Show Items without PDF",
                    help="""Items having no pdf files""",
                )
                report_standalone = c1.checkbox(
                    "Show Standalone items",
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

                head = c1.checkbox(
                    "Show items", help="""Show titles of at most the first 10 items"""
                )
                suspecious = c1.checkbox(
                    "Show suspecious items",
                    help="""Items with libraryCatalog = Zotero""",
                )
                trash = c1.checkbox("Show trash status", help="""Trash empty?""")
                start = config.form_submit_button(label="🚦Start")
                pl2 = st.empty()
                if start:
                    if head:
                        num_head = 10
                        with mylog.st_stdout("success"), mylog.st_stderr("code"):
                            for item in st.session_state.zot_items[:num_head]:
                                utils.log_title(item)

                    if trash:
                        trash_empty = utils.trash_is_empty(st.session_state.zot)
                        if trash_empty:
                            pl2.info("trash is empty!")
                        else:
                            pl2.warning("trash is not empty!")

                    if report_duplicates_title:
                        duplicates = utils.duplicates_by_title(
                            st.session_state.zot_items
                        )

                        if len(duplicates):
                            pl2.warning(f"Duplicate items: {len(duplicates)}")
                        else:
                            pl2.info("Duplicate items found.")

                        for d in duplicates:
                            with mylog.st_stdout("success"), mylog.st_stderr("code"):
                                logging.info(d)

                    if report_no_doi_isbn:
                        fields = ["DOI", "ISBN"]
                        if not st.session_state.no_doi_isbn_items:
                            st.session_state.no_doi_isbn_items = (
                                utils.get_items_with_empty_doi_and_isbn(
                                    st.session_state.zot_items, fields
                                )
                            )

                        if st.session_state.no_doi_isbn_items:
                            pl2.warning(
                                f"Items with no doi and no isbn: {len(st.session_state.no_doi_isbn_items)}"
                            )
                        else:
                            pl2.info("Found no items without doi and isbn")


                        for d in st.session_state.no_doi_isbn_items:
                            with mylog.st_stdout("success"), mylog.st_stderr("code"):
                                logging.info(f"Title: {d}")

                    if report_duplicates:
                        utils.update_duplicate_items()
                        
                        if len(duplicates):
                            pl2.warning(f"Duplicate items: {len(duplicates)}")
                        else:
                            pl2.info("No duplicate items found.")
                            
                        for d in duplicates:
                            with mylog.st_stdout("success"), mylog.st_stderr("code"):
                                logging.info(f"Title: {d}")

                    ## Functionalities
                    if report_standalone:
                        standalones = utils.get_standalone_items(
                            st.session_state.zot_items
                        )

                        if not standalones:
                            pl2.info("No standalone items")
                        else:
                            pl2.warning(f"Standalone item(s): {len(standalone)}")

                        for d in standalones:
                            with mylog.st_stdout("success"), mylog.st_stderr("code"):
                                logging.info(f"Type: {d}")

                    if report_duplicate_pdf:
                        t1 = time.process_time()                        
                        with st.spinner('processing ...'):
                            utils.update_duplicate_attach_state()

                        t2 = time.process_time()
                        pl2.info(t2 - t1)
                        msg_time = utils.get_time(t2 - t1)
                        msg_status.info(f"Items loaded in {msg_time}")
                        num_duplicates = len(st.session_state.multpdf_items)
                        if num_duplicates:
                            pl2.warning(
                                f"Items with duplicate pdf files found: {num_duplicates}"
                            )
                            for item in st.session_state.multpdf_items:
                                item_key = item["key"]
                                with mylog.st_stdout("success"), mylog.st_stderr(
                                    "code"
                                ):
                                    ttt = item["data"]["title"]
                                    logging.info(f"""Title: {ttt}""")
                                    logging.info(
                                        f"PDF: {st.session_state.pdfs[item_key]}"
                                    )
                        else:
                            pl2.info(
                                "No items with duplicate pdf attachments found"
                            )

                    if report_without_pdf:
                        t1 = time.process_time()
                        utils.update_without_pdf_state()
                        t2 = time.process_time()
                        pl2.write(t2 - t1)
                        msg_time = utils.get_time(t2 - t1)
                        msg_status.info(f"Items loaded in {msg_time}")
                        num_duplicates = len(st.session_state.nopdf_items)
                        if num_duplicates:
                            pl2.warning(f"Items with no pdf attachments: {num_duplicates}")
                            for item in st.session_state.nopdf_items:
                                item_key = item["key"]
                                with mylog.st_stdout("success"), mylog.st_stderr(
                                    "code"
                                ):
                                    ttt = item["data"]["title"]
                                    logging.info(f"""Title: {ttt}""")
                        else:
                            pl2.info("Items without pdf attachments not found")

                    if suspecious:
                        utils.update_suspecious_state()
                        num_suspecious = len(st.session_state.suspecious_items)

                        if num_suspecious:
                            pl2.warning(f"Suspecious items: {num_suspecious}")
                        else:
                            pl2.info("No suspecious items found")

                        for item in st.session_state.suspecious_items:
                            item_key = item["key"]
                            with mylog.st_stdout("success"), mylog.st_stderr("code"):
                                ttt = item["data"]["title"]
                                logging.info(f"""Title: {ttt}""")

                    if update_tags_z or update_tags_n or update_tags_m:
                        if not utils.uptodate():
                            pl2.error("Library not up-to-date. Reload!")
                        else:
                            utils.update_tags(pl2,
                                              update_tags_z,
                                              update_tags_n,
                                              update_tags_m)

                    if delete_duplicates:
                        # deleting attachments does not update the version of the lib.
                        # weird!
                        # todo: find out why?
                        if not utils.uptodate():
                            pl2.error("Library not up-to-date. Reload!")
                        else:
                            utils.delete_duplicate_items(pl2)

                    if delete_duplicate_pdf:
                        if not utils.uptodate():
                            pl2.error("Library not up-to-date. Reload!")
                        else:
                            res = utils.delete_duplicate_pdf(pl2)
                            if res:
                                pl2.info("Done!")
                            else:
                                pl2.info("Nothing to delete!")

