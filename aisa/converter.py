from abc import ABC, abstractmethod
from typing import Dict, List

from .namedentity import NamedEntity


class AnnotationConverter(ABC):
    @abstractmethod
    def annotation_to_entities(annotation: Dict) -> List[NamedEntity]:
        pass

    def entities_to_annotation(entities: List[NamedEntity]) -> Dict:
        pass


class LabelStudioConverter(AnnotationConverter):

    @staticmethod
    def entities_to_annotation(entities: List[NamedEntity], text: str) -> Dict:
        """
        Converts a list of NamedEntities to LabelStudio annotations

        Parameters
        ----------
        entities: List[NamedEntity]

        Returns
        -------
        dict
            a dictionary corresponding a LabelStudio annotation
        """
        # TODO annotation ID generation
        annot = {
            "id": 0,
            "annotations": [{"result": []}],
            "data": {"text": ""},
        }

        for entity in entities:
            annot["annotations"][-1]["result"].append(
                {
                    "value": {
                        "start": entity.char_span[0],
                        "end": entity.char_span[1],
                        "labels": [entity.label],
                    },
                    "from_name": "label",
                    "to_name": "text",
                    "type": "labels",
                }
            )

        annot["data"]["text"] = text

        return annot
