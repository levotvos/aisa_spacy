import json
import os
from typing import Dict, List


def generate_org_rules_with_tail(tails: List[str]) -> Dict:
    """
    Generates regex patterns for various ORG tails,
    So they are recognized as one unit of an entity.
    """
    patterns = []
    for tail in tails:
        pattern_line = {
            "label": "ORG",
            "pattern": [{"ENT_TYPE": "ORG", "OP": "+"}, {"TEXT": " ", "OP": "?"}],
        }
        regex_part = r""
        # Example for Kft.
        # K\s?f\s?t\s?[.]?|K\s?f\s?t\s?[-]+\s?\w*
        for char in tail:
            if char != ".":
                regex_part += char + r"\s?"

        regex_full = regex_part + r"[.]|" + regex_part + r"[-]+\s?\w*"

        pattern_line["pattern"].append({"TEXT": {"REGEX": regex_full}})

        patterns.append(pattern_line)

    return patterns


def generate_rules_file(
    manual_rules_file_path: os.PathLike, rules_file_path: os.PathLike
):
    with open(manual_rules_file_path, encoding="utf-8") as manual_rules_file:
        manual_rules = json.load(manual_rules_file)

    org_rules = generate_org_rules_with_tail(["Bt.", "Kft.", "Zrt.", "Rt.", "Nyrt."])
    manual_rules.extend(org_rules)

    with open(rules_file_path, "w", encoding="utf-8") as rules_file:
        json.dump(manual_rules, rules_file, indent=4)


generate_rules_file(
    os.path.join("assets", "manual_entity_rules.json"),
    os.path.join("assets", "entity_rules.json"),
)
