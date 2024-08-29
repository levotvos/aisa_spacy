import argparse
import os
import time

import aisa

print("AISA ver.:", aisa.__version__)

start_time = time.time()

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("datadir", default="data")
args = arg_parser.parse_args()

if not os.path.exists(args.datadir):
    print("The given path does not exist!")
else:

    annotator = aisa.aisa.AISA()

    text_paths = aisa.utils.search_for_text_files("data")
    for text_path in text_paths:
        other_dirs_split = text_path.split(os.sep)[1:-1]
        filename = os.path.basename(text_path)

        text = aisa.utils.read_os_independent_text(text_path)
        entities = annotator(text)
        annot = aisa.converter.LabelStudioConverter.entities_to_annotation(
            entities, text
        )

        aisa.utils.save_annotation(
            "output", other_dirs_split, filename + ".json", annot
        )

print("DONE. --- %.2f seconds" % (time.time() - start_time))
