import json
import os
from typing import Dict, List

import spacy

from . import converter
from .namedentity import NamedEntity


def get_entities_with_char_spans(doc: spacy.language.Doc) -> List[NamedEntity]:
    """
    Extracts character spans, labels and the text itself
    for all named entities in the passed in spaCy document

    Parameters
    ----------
    doc: spacy.language.Doc

    Returns
    -------
    list
        a list of tuples, where the first element is the char span
        the second is the entity label, and the third is the text
    """
    entities = []
    for ent in doc.ents:
        entities.append(
            NamedEntity((ent.start_char, ent.end_char), ent.label_, ent.text)
        )

    return entities


class AISA:
    def __init__(self):
        self.nlp = spacy.load(
            "hu_core_news_trf",
            exclude=[
                "experimental_arc_predicter",
                "experimental_arc_labeler",
                "lookup_lemmatizer",
                "trainable_lemmatizer",
            ],
        )

        with open(os.path.join("assets", "entity_rules.json")) as rules_file:
            entity_rules = json.load(rules_file)

        ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        ruler.add_patterns(entity_rules)

    def __call__(self, text: str) -> Dict:
        doc = self.nlp(text)

        return get_entities_with_char_spans(doc)
