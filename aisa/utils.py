import json
import os


def search_for_text_files(datadir):
    """
    Searches for all text files in the given dir.
    """
    text_files = []

    # TODO switch to using glob !
    # There are some bugs experienced with this func.
    for root, dirs, files in os.walk(datadir):
        for file in files:
            if file.endswith(".txt"):
                text_files.append(os.path.join(root, file))

    return text_files


def read_os_independent_text(filepath) -> str:
    """
    Reads a text file and uniforms line endings...
    """
    with open(filepath, "rb") as fp:
        print("### Working on: ", filepath)
        text = fp.read()

        # Unixos Windowos formatumok konvertalasa (LF -> CRLF)

        windows_line_ending = b"\r\n"
        unix_line_ending = b"\n"

        text = text.replace(windows_line_ending, unix_line_ending)
        text = text.replace(unix_line_ending, windows_line_ending)
        text = text.decode("utf-8")

    return text


def save_annotation(outputdir, other_dirs_split, filename, annot_data):
    """
    Saves the generated annotation
    """
    if not os.path.exists(os.path.join(outputdir, *other_dirs_split)):
        os.makedirs(os.path.join(outputdir, *other_dirs_split))

    with open(
        os.path.join(outputdir, *other_dirs_split, filename),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump([annot_data], f)
