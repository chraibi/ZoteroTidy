import configparser
import logging
import time

import streamlit as st
from pyzotero import zotero

import mylogging as mylog
import utils as util

st.set_page_config(
    page_title="ZotMain",
    page_icon=":orange_book:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/chraibi/maintain-zotero",
        "Report a bug": "https://github.com/chraibi/maintain-zotero/issues",
        "About": "# Maintain a Zotero library",
    },
)


def demo_function(max_run):
    """
    Just a sample function to show how it works.
    :return:
    """

    step = int(100 / max_run)
    for i in range(max_run):
        logging.info(f"Counting... {i}")
        my_bar.progress(i * step + max_run)
        time.sleep(1)


# @st.cache(suppress_st_warning=True)
if __name__ == "__main__":
    # UI --------------------------------
    left_col, right_col = st.columns(2)  # c2 for logs. c1 for important info
    # Info
    about = "## Maintain a Zotero library"
    with left_col:
        st.markdown(about, True)
        with st.expander("", expanded=False): #  @todo: more
            st.markdown("This app reports the following:")
            st.markdown("- **duplicate_pdf**: Items with duplicate pdf-files")
            st.markdown("- **nopdf**: Items with *no*  pdf-files")

    st.sidebar.markdown(":point_down:")
    config_file = st.sidebar.file_uploader(
        "Choose a file:",
        type=["txt", "cfg"],
        help="Load config file with group ID, API-key and library type",
    )

    with right_col:
        pl = st.empty()
    if config_file:
        configFilePath = config_file.name
        try:
            confParser = configparser.RawConfigParser()
            confParser.read(configFilePath)
            library_id = int(confParser.get("zotero-config", "library_id"))
            api_key = confParser.get("zotero-config", "api_key")
            library_type = confParser.get("zotero-config", "library_type")
        except confParser.Error:
            with right_col:
                pl.error(
                    """Can't parse the config file.
                    Try uploading another file!"""
                )
            st.stop()

        zot = zotero.Zotero(library_id, library_type, api_key)
        num_items = zot.num_items()
        with right_col:
            pl.success(f"File loaded! Library got {num_items} items.")

        with left_col:
            config = st.form("config_form")
            config.markdown("# Options")
            items_to_retrieve = config.slider(
                "Select items to retrieve from library",
                min_value=1,
                max_value=num_items,
                help="Items to retrieve at once? (the more the slower!)",
            )
            update_tags = config.checkbox(
                "Update Tags", help="add special tags to items"
            )

            report_duplicates = config.checkbox(
                "Report Duplicate Items",
                help="""Report duplicate items based on
                DOI/ISBN and title""",
            )

            delete_duplicates = config.checkbox(
                "Merge Duplicate Items",
                help="""Identify duplicate items based on
                DOI/ISBN and merge them""",
            )

            report_duplicate_pdf = config.checkbox(
                "Report Items with Multiple PDF",
                help="""Report items having more than
                one pdf file""",
            )

            report_standalone = config.checkbox(
                "Report Standalone items",
                help="""Report standlalone items like
                PDF or Notes""",
            )

            delete_duplicate_pdf = config.checkbox(
                "Delete Multiple PDF",
                help="""If item has multiple pdf files
                with expr as alias:
                the same name, then keep only
                one.""",
            )

            start = config.form_submit_button("Start")

            if start:
                with right_col:
                    pl2 = st.empty()
                    my_bar = pl.progress(0)
                    with mylog.st_stdout("success"), mylog.st_stderr("code"):
                        demo_function(items_to_retrieve)

                    pl.success("Done!")
