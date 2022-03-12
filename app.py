import configparser
import logging
import os
import sys
import timeit
from collections import defaultdict
from io import StringIO
from pathlib import Path
import datetime as dt

import streamlit as st
from pyzotero import zotero
from pyzotero.zotero_errors import UserNotAuthorised
import utils

path = Path(__file__)
ROOT_DIR = path.parent.absolute()


def init_logger():
    logging.info("Init Logger")
    logfile = os.path.join(ROOT_DIR, 'logfile.log')
    logging.basicConfig(
        level=logging.INFO,
        force=True,
        format="%(levelname)s - %(asctime)s - %(message)s",
        handlers=[logging.FileHandler(filename=logfile),
                  logging.StreamHandler(sys.stdout)],
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger()

    return logfile, logger


st.set_page_config(
    page_title="ZoteroTidy",
    page_icon=":mortar_board:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/chraibi/ZoteroTidy",
        "Report a bug": "https://github.com/chraibi/ZoteroTidy/issues",
        "About": "## ZooteroTidy is an App for Zotero Sanity Checks\n :copyright: Mohcine Chraibi",
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
    st.session_state.num_items = st.session_state.zot.count_items()
    st.session_state.multpdf_items = []
    st.session_state.init_multpdf_items = False
    st.session_state.pdfs = defaultdict(list)
    st.session_state.nopdf_items = []
    st.session_state.suspecious_items = []
    st.session_state.doi_dupl_items = []
    st.session_state.init_doi_dupl_items = False
    st.session_state.no_doi_isbn_items = []


if __name__ == "__main__":

    if "init_logger" not in st.session_state:
        st.session_state.init_logger = False

    if "logger" not in st.session_state:
        st.session_state.logger = ""

    if "logfile" not in st.session_state:
        st.session_state.logfile = ""

    if "old_configs" not in st.session_state:
        st.session_state.old_configs = ""

    if "children" not in st.session_state:
        st.session_state.children = {}

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

    if not st.session_state.init_logger:
        logfile, logger = init_logger()
        st.session_state.logger = logger
        st.session_state.logfile = logfile
        open(logfile, 'w').close()  # filemode in config does not work!
        st.session_state.init_logger = True

    logger = st.session_state.logger
    logfile = st.session_state.logfile

    #  UI --------------------------------
    st.sidebar.image("logo.png", use_column_width=True)
    yt_video = "https://www.youtube.com/watch?v=P_YeNXEOINk"
    gh = "https://badgen.net/badge/icon/GitHub?icon=github&label"
    repo = "https://github.com/chraibi/ZoteroTidy"

    sc1, _, sc2 = st.sidebar.columns((2, 1, 2))
    repo_name = f"[![Repo]({gh})]({repo})"
    sc1.markdown(repo_name, unsafe_allow_html=True)
    sc2.markdown(f"[![YT]({utils.yt_icon()})]({yt_video})",
                 unsafe_allow_html=True)
    st.sidebar.markdown("-------")
    st.title(":mortar_board: Maintaining Zotero libraries")
    st.header("")
    st.markdown("##### :information_source: About")
    with st.expander("", expanded=False):
        utils.about()

    st.markdown("##### 	:speech_balloon: How to use")
    with st.expander("", expanded=False):  # @todo: more
        utils.howto()

    st.markdown("##### :round_pushpin: Features")
    with st.expander("", expanded=False):  # @todo: more
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
        configFilePath = os.path.join(ROOT_DIR, config_file.name)
        confParser = configparser.RawConfigParser()
        stringio = StringIO(config_file.getvalue().decode("utf-8"))
        string_data = stringio.read()
        try:
            confParser.read_string(string_data)
            # Maybe file's content or even the file itself changed?
            if string_data != st.session_state.old_configs:
                st.session_state.num_items = 0
                st.session_state.old_configs = string_data

        except Exception as e:
            logging.error(f"can not read file {configFilePath} with error {str(e)}")
        try:
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
            try:
                st.session_state.num_items = st.session_state.zot.count_items()
                if st.session_state.num_items == 1:
                    st.warning(f"Not enough items in library. num_items = {st.session_state.num_items}")
                    st.stop()
            except UserNotAuthorised:
                st.error("Connection refused. Invalid key ..")
                st.stop()

            st.session_state.zot_version = st.session_state.zot.last_modified_version()
            msg_status.success("Config loaded!")

        update_library = placeholder.button("🔁 Sync Library")
        if update_library:
            placeholder.empty()
            msg_status.info(
                """:heavy_check_mark: Library synced!\n
                🔴 Load items!"""
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
            time_start = timeit.default_timer()
            st.session_state.zot_version = st.session_state.zot.last_modified_version()

            st.session_state.zot_items = utils.retrieve_data(
                st.session_state.zot, max_items)

            msg_status.info(f"Initialize children of {max_items} items ...")
            with st.spinner("Initializing ..."):
                st.session_state.children = utils.get_children()

            logging.info(f"num_items {st.session_state.zot.num_items()}, Num children: {len(st.session_state.children)}")
            time_end = timeit.default_timer()

            st.session_state.lib_loaded = True

            msg_time = utils.get_time(time_end - time_start)
            msg_status.success(f":clock8: Finished in {msg_time}")

        if st.session_state.lib_loaded:
            config = st.form("config_form")
            with config:
                c1, c2 = st.columns((1, 1))
                c1.write("**Report options**")
                c2.write("**Update options**")
                update_tags_z = c2.checkbox(
                    "Tag suspecious items", help="todo_catalog"
                )
                update_tags_n = c2.checkbox(
                    "Tag items with no pdf", help="nopdf"
                )
                update_tags_m = c2.checkbox(
                    "Tag items with multiple pdf",
                    help="duplicate_pdf",
                )
                update_tags_d = c2.checkbox(
                    "Tag duplicate items",
                    help="duplicate_item",
                )
                head = c1.checkbox(
                    "Head",
                    value=True,
                    help="""Show titles of at most the first 10 items"""
                )
                report_duplicates = c1.checkbox(
                    "Duplicate Items (DOI/ISBN)",
                    help="""Duplicate items based on
                    DOI/ISBN""",
                )
                OA = c1.checkbox(
                    "Open-Access",
                    help="""Return Items that are not OA""",
                )
                mail = c1.text_input("Enter an Email-adress",
                                     placeholder="mail@box.com",
                                     help="""An email that is necessary for using the Unpaywall API service.""",
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
                    "DOI & ISBN", help="Articles with no doi and Books with no isbn"
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
                    # check write-options
                    update_tags = update_tags_d \
                        or update_tags_m \
                        or update_tags_n \
                        or update_tags_z

                    if update_tags + \
                       delete_duplicates + \
                       delete_duplicate_pdf > 1:

                        st.error("Can not have more than one write-opration")
                        st.stop()

                    if not utils.uptodate():
                        msg_status.error(":fire: Library is out of sync.")

                    if head:
                        num_head = 10
                        st.info(f"Top {num_head} items")
                        logging.info(f"Top {num_head} items")
                        logger.info(f"Top {num_head} items")
                        count = 0
                        for item in st.session_state.zot_items:
                            if not utils.is_standalone(item):
                                utils.log_title(item)
                                count += 1
                                if count >= num_head:
                                    break

                    if trash:
                        trash_empty = utils.trash_is_empty(st.session_state.zot)
                        if trash_empty:
                            st.info(":heavy_check_mark: Trash is empty!")
                        else:
                            st.warning(":x: Trash is not empty!")

                    if OA:
                        utils.unpywall_credits(mail)
                        time_start = timeit.default_timer()
                        items_by_doi = utils.get_items_by_doi(st.session_state.zot_items)
                        with st.spinner("Initializing ..."):
                            OA_items, CA_items = utils.get_oa_ca(items_by_doi, pl2)

                        time_end = timeit.default_timer()
                        msg_time = utils.get_time(time_end - time_start)
                        msg_status.success(f":clock8: Finished in {msg_time}")
                        total = len(items_by_doi)
                        st.info(f":heavy_check_mark: found {len(OA_items)} / {total} open-access articles")
                        if CA_items:
                            st.warning(f":x: found {len(CA_items)} / {total} close-access articles")

                        logging.info(f"Open-Access dois ({len(OA_items)} / {total})\n")
                        for i in OA_items:
                            logging.info(f"doi: {i}")

                        logging.info(f"Not Open-Access dois {len(CA_items)} / {total}\n")
                        for i in CA_items:
                            logging.info(f"doi: {i}")

                        if total - len(OA_items) - len(CA_items):
                            st.warning(f":interrobang: {total - len(OA_items) - len(CA_items)} DOIs could not be found by Unpaywall.")
                            logging.warning(f"{total - len(OA_items) - len(CA_items)} DOIs could not be found by Unpaywall.\n")
                            for doi, item in items_by_doi.items():
                                doi = doi.lower()
                                if doi not in OA_items and doi not in CA_items:
                                    logging.info(f"doi: <{doi}>")

                    if report_no_doi_isbn:

                        st.session_state.no_doi_isbn_items = (
                            utils.get_items_with_empty_doi_or_isbn(
                                st.session_state.zot_items))

                        if st.session_state.no_doi_isbn_items:
                            st.warning(
                                f""":x: Items with no doi / isbn:
                                {len(st.session_state.no_doi_isbn_items)}"""
                            )
                        else:
                            st.info(
                                """:heavy_check_mark: No items without
                            doi / isbn"""
                            )

                        logging.info("Items with no doi or no isbn: \n")
                        for d in st.session_state.no_doi_isbn_items:
                            utils.log_title(d)


                    if report_duplicates:
                        utils.update_duplicate_items_state()
                        duplicates = st.session_state.doi_dupl_items
                        if duplicates:
                            st.warning(f":x: Duplicate items: {len(duplicates)}")
                        else:
                            st.info(":heavy_check_mark: No duplicate items found.")

                        logging.info("Duplicate items: \n")
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

                        logging.info("Standalone items:\n")
                        for d in standalones:
                            utils.log_title(d)

                    if report_duplicate_pdf:
                        utils.update_duplicate_attach_state()
                        num_duplicates = len(st.session_state.multpdf_items)
                        if num_duplicates:
                            st.warning(f":x: Items with duplicate pdf files found: {num_duplicates}")
                            logging.info("Items with duplicate pdf files:\n")
                            for item in st.session_state.multpdf_items:
                                item_key = item["key"]
                                utils.log_title(item)
                                st.code(f"> {st.session_state.pdfs[item_key]}")
                        else:
                            st.info(
                                """ :heavy_check_mark: No items with duplicate pdf attachments
                                found"""
                            )

                    if report_without_pdf:
                        utils.update_without_pdf_state()
                        num_duplicates = len(st.session_state.nopdf_items)
                        if num_duplicates:
                            st.warning(
                                f":x: Items with no pdf attachments: {num_duplicates}")
                            logging.info("Items with not pdf attachments:\n")
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

                        logging.info("Suspecious items:\n")
                        for item in st.session_state.suspecious_items:
                            utils.log(item)

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
                    # offer to downlod log after start                    
                    logging.info(f"logfile: {logfile}")
                    logging.info(f"Size of file: {os.path.getsize(logfile)}")
                    with open(logfile, encoding='utf-8') as f:
                        data = f.read()
                        T = dt.datetime.now()
                        logging.info(f"data: {len(data)}")
                        # zot.groups() does not work, for reasons I dont know!
                        group_name = st.session_state.zot.collections()[0]['library']['name']
                        log_file = f"{group_name}_{T.year}-{T.month:02}-{T.day:02}_{T.hour:02}-{T.minute:02}-{T.second:02}.log"
                        download = st.sidebar.download_button('Download log', data, file_name=log_file)
