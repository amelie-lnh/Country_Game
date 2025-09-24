# Test for duplicates inside json file
import json
from pathlib import Path

def find_assets_json(file_name="Capitals_and_Categories.json", assets_dir_name="Assets", max_up=5):
    """
    Search upward from this file's directory to find Assets/Capitals_and_Categories.json.
    Returns a Path if found, else raises FileNotFoundError with helpful message.
    """
    start = Path(__file__).resolve().parent
    for p in (start, *start.parents[:max_up]):
        candidate = p / assets_dir_name / file_name
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"Could not find {assets_dir_name}/{file_name} searching from {start} upwards.\n"
        "Make sure the JSON file is at Assets/Capitals_and_Categories.json relative to your project root,\n"
        "or move this test file to a location where the Assets folder is reachable."
    )

def test_json_loads_and_has_difficulties():
    path = find_assets_json()
    with open(path, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    assert isinstance(all_data, dict), "Top-level JSON should be a dictionary (difficulties)"
    for diff in ("Easy", "Medium", "Hard"):
        assert diff in all_data, f"Missing difficulty level: {diff}"
        assert isinstance(all_data[diff], list), f"{diff} should contain a list"

def test_country_entries_structure_and_count():
    path = find_assets_json()
    with open(path, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    total = 0
    seen_codes = set()
    for diff, entries in all_data.items():
        assert isinstance(entries, list), f"{diff} must be a list"
        total += len(entries)
        for e in entries:
            assert isinstance(e, dict), "Each entry should be an object/dict"
            assert "country_code" in e and e["country_code"], "Missing or empty country_code"
            assert "country_name" in e and e["country_name"], "Missing or empty country_name"
            assert "capital" in e and e["capital"], "Missing or empty capital"
            # check duplicates across difficulties (typically each country appears once)
            code = e["country_code"].upper()
            assert code not in seen_codes, f"Duplicate country_code found across difficulties: {code}"
            seen_codes.add(code)

    # Basic sanity check — adjust threshold if you know a different expected size
    assert total >= 150, f"Total countries ({total}) seems too small; check your JSON."

test_json_loads_and_has_difficulties()
test_country_entries_structure_and_count()