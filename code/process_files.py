"""
process_files.py — Part 3: many files, one after another, with a running total.

The same job as process_file.py, but the app now remembers what it has already
done: how many files have been processed, how many packages that came to, and a
one-line summary of each file — and it keeps remembering across uploads.

That is the hard part, and it is hard for a specific reason: every interaction
reruns this whole script from the top, so an ordinary variable like
`files_processed = 0` is reset to zero on every rerun. Anything that has to
survive a rerun lives in `st.session_state` instead, and is initialised only
once — the first time the script runs.

The other trap is the uploader itself. Once a file has been chosen it stays
chosen on every rerun, so an app that processes "whenever there is a file" would
count the same file again on every interaction. Processing happens on a button
click instead: `st.button` is True only on the one rerun the click caused.

Run it:  Run and Debug -> "Streamlit Run: Current File"   (see README Reference #1)
Test it: pytest tests/test_streamlit.py -k process_files
"""

# --- The page ---------------------------------------------------------------------
#
# No scaffolding. You have written two of these now, and this one does the same
# processing as process_file.py — the difference is that it remembers.
#
# What you have to work out for yourself:
#
#   - the three parts of the session-state pattern: initialise once, update on the
#     click, display from state — README Reference #6
#   - a button, key="process", so that choosing a file and clicking are two
#     different things
#   - two st.metric cards, "Files processed" and "Packages processed", side by side
#     in st.columns(2), on the page from the first run
#   - one st.info line per file processed so far, kept in a list
#
# README Step 7 names the two traps. The tests are built around them: choosing a
# file without clicking must change nothing, and a rerun with the same file still
# chosen must not count it again.

import os
import json
import streamlit as st
from packaging_parser import calc_total_units, get_unit, parse_packaging

def reset_uploads():
    '''
    Resets counters and deletes all previous json files uploaded
    '''
    st.session_state['tot_packages'] = 0
    st.session_state['tot_uploads'] = 0
    st.session_state['file_history'] = {}

    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            os.remove(os.path.join(data_dir, filename))


if 'tot_packages' not in st.session_state:
    st.session_state['tot_packages'] = 0

if 'tot_uploads' not in st.session_state:
    st.session_state['tot_uploads'] = 0

if 'file_history' not in st.session_state:
    st.session_state['file_history'] = {}

st.title("Process Package Files")

user_upload = st.file_uploader(
    "Upload file package:",
    key="package_file"
)

if st.button(
    "Process file",
    type="primary",
    key="process"):
    if user_upload is not None and user_upload not in st.session_state['file_history']:
        text = user_upload.getvalue().decode("utf-8")
        packages = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue

            package = parse_packaging(line)
            packages.append(package)
            st.session_state['tot_packages'] += 1

        new_file = user_upload.name.replace(".txt", ".json")
        display_path = os.path.join("data", new_file)
        abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", new_file))

        with open(abs_path, "w", encoding="utf-8") as json_file:
            json.dump(packages, json_file, indent=4)

        st.session_state['file_history'][user_upload] = (f"{len(packages)} packages written to {display_path}")
        st.session_state['tot_uploads'] += 1

st.button(
    "Reset",
    key="reset",
    on_click=reset_uploads
)

col1, col2 = st.columns(2)
with col1:
    st.metric(
        "Files processed",
        st.session_state['tot_uploads']
    )
with col2:
    st.metric(
        "Packages processed",
        st.session_state['tot_packages']
    )

for summary in st.session_state['file_history'].values():
    st.info(summary)