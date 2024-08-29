"""
    Converts LabelStudio annotation files 
    (and their accompanying text files) to a viewable HTML file
"""

import copy
import json
import os
import urllib.parse
from typing import List, Union


def search_for_annotation_files(datadir: Union[str, os.PathLike]):
    """
    Searches for all annotation files in the given dir.
    """
    annotation_files = []

    # TODO switch to using glob !
    # There are some bugs experienced with this func.
    for root, dirs, files in os.walk(datadir):
        for file in files:
            if file.endswith(".json"):
                annotation_files.append(os.path.join(root, file))

    return annotation_files


def read_os_independent_text(filepath: Union[str, os.PathLike]) -> str:
    """
    Reads a text file and uniforms line endings...
    """
    # TODO source for this method... (somewhere on stackoverflow)
    with open(filepath, "rb") as fp:
        print("### Working on: ", filepath)
        text = fp.read()

    text = replace_win_lineendings(text)

    return text


def replace_win_lineendings(text: Union[str, bytes]) -> str:
    # Unixos Windowos formatumok konvertalasa (LF -> CRLF)
    windows_line_ending = b"\r\n"
    unix_line_ending = b"\n"

    if not isinstance(text, bytes):
        text = text.encode("utf-8")
    text = text.replace(windows_line_ending, unix_line_ending)
    text = text.replace(unix_line_ending, windows_line_ending)
    text = text.decode("utf-8")
    return text


def convert_entity_list_to_annotated_html(
    entity_list, text, ent_class_to_classname_map
):
    # Azt feltetelezve, hogy nincsenek intervallum utkozesek
    # Visszafele haladva helyettesitjuk a szovegreszeket,
    # igy nem kell az eltolasokkal foglalkozni...
    new_text = copy.copy(text)

    print(entity_list)

    for span, label, ent_text in sorted(entity_list, key=lambda x: x[0], reverse=True):
        new_ent_text = (
            '<span class="'
            + ent_class_to_classname_map[label]
            + '">'
            + ent_text
            + "</span>"
        )
        new_text = new_text[: span[0]] + new_ent_text + new_text[span[1] :]

    new_text = new_text.replace("\n", "<br>")

    return new_text


class AnnotationReaderBase:
    @staticmethod
    def load_annotations(annotation_file: Union[str, os.PathLike]):
        """
        Loads the JSON annotations file
        """
        with open(annotation_file, encoding="utf-8") as afp:
            print("#" * 50)
            print("##### Opened annotation file:", annotation_file)
            print("#" * 50)
            try:
                json_data = json.load(afp)
                return json_data
            except ValueError as error:  # includes JSONDecodeError
                print("ERROR: The file is not a valid JSON:", annotation_file)
                print("\t", error)
                return None


class AnnotationReaderLabelStudio(AnnotationReaderBase):
    """
    Reads named entities into a list
    from a LabelStudio annotation file
    """

    def __init__(self):
        self.ent_classes = set()

    def __call__(self, annotation_file: Union[str, os.PathLike]):
        datadir = annotation_file.split(os.sep)[0]
        other_dirs_split = annotation_file.split(os.sep)[1:-1]

        # One annotation (project) file could contain annotations for more texts
        annot_list = AnnotationReaderLabelStudio.load_annotations(annotation_file)

        if not annot_list:
            print("ERROR: No annotations can be found in the file", annotation_file)
            return

        for annot in annot_list:
            fname = None
            text = None
            annot_id = annot["id"] if "id" in annot.keys() else None

            if "file_upload" in annot.keys():
                fname = AnnotationReaderLabelStudio.try_to_get_annot_filename(
                    datadir, other_dirs_split, annot
                )

                if not fname:
                    print("Continuing...")
                    continue

                text = read_os_independent_text(fname)
            else:
                if "data" in annot.keys():
                    if "text" in annot["data"]:
                        # text = replace_win_lineendings(annot["data"]["text"])
                        text = annot["data"]["text"]

            if not text:
                print(
                    "Error was unable to get text for annotation ID:",
                    annot["id"],
                    "in",
                    annotation_file,
                )
                print("Continuing...")
                continue

            # Entitas lista meghatarozasa
            annot_entity_list, text_classes = (
                AnnotationReaderLabelStudio.read_entity_list_from_annotation(
                    text, annot
                )
            )

            self.ent_classes.update(text_classes)

            yield annot_id, annot_entity_list, text

    @staticmethod
    def try_to_decode_annot_text_filename(
        filename: Union[str, os.PathLike],
        datadir: Union[str, os.PathLike],
        other_dirs_split: Union[str, os.PathLike],
        annot: dict,
    ):
        """
        Some filenames could percent encoded,
        sometimes they are present in an other attribute
        """
        # TODO this could be an instance method...

        fname = filename

        if not os.path.exists(fname):
            # Az annot["data"]["text"] a label studio altal % encode-olt fajl utvonala
            # Ha ott nem talalhato a fajl, akkor megprobaljuk eloszor parse-olni
            fname = urllib.parse.unquote(fname)

            if not os.path.exists(fname):
                # Es ha ez sem sikerul, akkor az eredeti neven keressuk
                fname = os.path.join(datadir, *other_dirs_split, annot["file_upload"])
                # Ha egyeltalan nem talalhato a fajl
                if not os.path.exists(fname):
                    print(
                        "Nem talalhato a kovetkezo fajl:",
                        fname,
                    )
                    return None

        return fname

    @staticmethod
    def try_to_get_annot_filename(
        datadir: Union[str, os.PathLike],
        other_dirs_split: List[Union[str, os.PathLike]],
        annot: dict,
    ):
        fname_to_decode = os.path.join(
            datadir, *other_dirs_split, os.path.basename(annot["data"]["text"])
        )
        fname = AnnotationReaderLabelStudio.try_to_decode_annot_text_filename(
            fname_to_decode, datadir, other_dirs_split, annot
        )

        if fname:
            return fname
        else:
            # LabelStudio could append an unique id seperated by a dash to uploaded files
            alt_basename = "".join(
                os.path.basename(annot["data"]["text"]).split("-")[1:]
            )
            fname_to_decode = os.path.join(datadir, *other_dirs_split, alt_basename)

            return AnnotationReaderLabelStudio.try_to_decode_annot_text_filename(
                fname_to_decode, datadir, other_dirs_split, annot
            )

    @staticmethod
    def read_entity_list_from_annotation(text: str, annotation_data: dict):
        """
        Reads the list of entities from a LabelStudio annotation data object

        Returns with a list of ents. consisting of their start and end idx,
        respective label and exact text.

        Also returns the list of labels found in the annotation.
        """
        # TODO -1 means it only reads the last/latest annotation
        entity_list = []
        text_classes = []

        for rec in annotation_data["annotations"][-1]["result"]:
            if "value" not in rec:
                continue  # XXX hot fix a hiányzó kulccsal kapcsolatos hiba kiküszöbölésére
            val = rec["value"]
            entity_list.append(
                (
                    (val["start"], val["end"]),
                    val["labels"][0],
                    text[val["start"] : val["end"]],
                )
            )
            text_classes.append(val["labels"][0])

        return entity_list, text_classes


def create_css_style(ent_classes):
    ent_class_to_classname_map = {}

    style_start = """body {
                width: 1200px;
            }
            .p {
                word-wrap: break-word;
            }
            """
    for idx, ent_class in enumerate(ent_classes):
        ent_class_to_classname_map[ent_class] = "_class" + str(idx)

        style_start += "._class" + str(idx)
        style_start += """
            {
                background: lightgreen;
                font-weight: bold;
            }
            """
        style_start += "._class" + str(idx) + "::after "
        style_start += '{ content: "' + ent_class + '";'
        style_start += """
                color: white;
                background: lightgreen;
                font-variant: small-caps;
            }
            """

    style_end = "}"

    style = style_start + style_end
    return style, ent_class_to_classname_map


def create_full_html(title: str, annotated_html: str, stylesheet):
    html_before = """
    <!DOCTYPE html>
    <html>
    
    <head>
        <meta charset="UTF-8">
        <title>TestPage</title>
        <style>
    """

    html_before += stylesheet
    html_before += """
        </style>
    </head>
    
    <body>
        <div class="content">
            <b>test</b>

    <div class="p">
    """

    html_after = """</div></div>"""

    return html_before + annotated_html + html_after


def save_html(filepath, html):
    with open(filepath, "w", encoding="utf-8") as fp:
        fp.write(html)


def process_annotation_file(annot_reader, filepath: Union[str, os.PathLike]):
    import pprint

    for annot_id, entity_list, text in annot_reader(filepath):
        stylesheet, ent_class_to_classname_map = create_css_style(
            list(annot_reader.ent_classes)
        )
        annotated_html = convert_entity_list_to_annotated_html(
            entity_list, text, ent_class_to_classname_map
        )
        full_html = create_full_html(
            filepath + str(annot_id), annotated_html, stylesheet
        )
        save_html(filepath + ".html", full_html)


def main(path: Union[str, os.PathLike]) -> None:
    annot_reader = AnnotationReaderLabelStudio()

    abspath = os.path.abspath(path)

    if not os.path.exists(abspath):
        print("ERROR: The given filepath does not exists", abspath)
        return

    if os.path.isfile(abspath):
        process_annotation_file(annot_reader, path)
    else:
        annotation_files = search_for_annotation_files(path)
        if not annotation_files:
            print("No annotation files found in the directory")
        for annotation_file in annotation_files:
            process_annotation_file(annot_reader, annotation_file)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()

    main(args.path)
