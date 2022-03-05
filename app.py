import configparser
import logging
import time

import streamlit as st
from PIL import Image
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


def demo_function(max_run, my_bar):
    """
    Just a sample function to show how it works.
    :return:
    """

    step = int(100 / max_run)
    for i in range(max_run):
        progress_by = (i + 1) * step
        if i == max_run - 1:
            progress_by = 100

        logging.info(f"Counting... step {step}  {i} - {(i+1) * step}")
        my_bar.progress(progress_by)
        time.sleep(1)


# @st.cache(suppress_st_warning=True)
if __name__ == "__main__":
    if "num_items" not in st.session_state:
        st.session_state.num_items = 0

    if "lib_loaded" not in st.session_state:
        st.session_state.lib_loaded = False

    # UI --------------------------------
    image = Image.open("logo.png")
    st.sidebar.image(image, use_column_width=True)
    report_name = "[![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/chraibi/maintain-zotero)"
    st.sidebar.markdown(report_name, unsafe_allow_html=True)
    st.sidebar.markdown("-------")

    about = ":sos: Maintain a Zotero library"

    st.title(about)
    st.header("")
    st.markdown("## About this app")
    with st.expander("", expanded=False):  # @todo: more
        st.markdown("This app reports the following:")
        st.markdown("- **duplicate_pdf**: Items with duplicate pdf-files")
        st.markdown("- **nopdf**: Items with *no*  pdf-files")

    config_file = st.sidebar.file_uploader(
        "📙Choose a file",
        type=["cfg", "txt"],
        help="Load config file with group ID, API-key and library type",
    )
    st.sidebar.markdown("-------")
    pl = st.sidebar.empty()
    if config_file:
        configFilePath = config_file.name
        try:
            confParser = configparser.RawConfigParser()
            confParser.read(configFilePath)
            library_id = int(confParser.get("zotero-config", "library_id"))
            api_key = confParser.get("zotero-config", "api_key")
            library_type = confParser.get("zotero-config", "library_type")
        except Exception as e:
            pl.error(
                f"""Can't parse the config file.
                Error: {e}"""
            )
            st.stop()

        if not st.session_state.num_items:
            zot = zotero.Zotero(library_id, library_type, api_key)
            st.session_state.num_items = zot.num_items()
            pl.success("Config loaded!")

        load_library = st.button(
            "➡️ Load library",
            key="load_library",
            help="""
                                 Depending on the size of the library,
                                 this operation may take some time!""",
        )
        print("before", st.session_state.lib_loaded)
        if load_library:
            st.session_state.lib_loaded = False
            print("inside button", st.session_state.lib_loaded)
            with st.spinner("Wait for it..."):
                time.sleep(5)

            st.session_state.lib_loaded = True
            pl.success("Library loaded!")

        print("after", st.session_state.lib_loaded)

        if st.session_state.lib_loaded:
            config = st.form("config_form")
            with config:
                c1, c2, c3 = st.columns((1, 1, 2))
                c1.write("**Report options**")

                c2.write("**Update options**")

                update_tags = c2.checkbox(
                    "Update Tags",
                    key="config_form",
                    help="add special tags to items"
                )
                report_duplicates = c1.checkbox(
                    "Report Duplicate Items",
                    key="config_form",
                    help="""Duplicate items based on
                    DOI/ISBN and title""",
                )

                delete_duplicates = c2.checkbox(
                    "Merge Duplicate Items",
                    help="""Duplicate items based on
                    DOI/ISBN and merge them""",
                )

                report_duplicate_pdf = c1.checkbox(
                    "Report Items with Multiple PDF",
                    help="""Items having more than
                    one pdf file""",
                )

                report_standalone = c1.checkbox(
                    "Report Standalone items",
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

                items_to_retrieve = c1.slider(
                    "Select items to retrieve from library",
                    min_value=1,
                    max_value=st.session_state.num_items,
                    key="config_form",
                    help="Items to retrieve at once? (the more the slower!)",
                )
                start = config.form_submit_button(label="🚦Start")
                pl2 = st.empty()
                if start:
                    my_bar = pl2.progress(0)
                    with mylog.st_stdout("success"), mylog.st_stderr("code"):
                        demo_function(items_to_retrieve, my_bar)

                    pl.success("Done!")
