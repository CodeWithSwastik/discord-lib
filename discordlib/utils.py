import json


def change_case(string):
    return "".join(["_" + i.lower() if i.isupper() else i for i in string]).lstrip("_")


def change_case_for_dict_keys(dictionary):
    new_dict = {}
    for key in dictionary:
        if isinstance(dictionary[key], dict):
            dictionary[key] = change_case_for_dict_keys(dictionary[key])
        elif isinstance(dictionary[key], list):
            for possible_dictionary in [
                x for x in dictionary[key] if isinstance(x, dict)
            ]:
                dictionary[key].remove(possible_dictionary)
                dictionary[key].append(change_case_for_dict_keys(possible_dictionary))
        new_dict[change_case(key)] = dictionary[key]

    return new_dict


def convert_string_bools_to_bools(item):
    if isinstance(item, dict):
        return {key:convert_string_bools_to_bools(value) for key, value in item.items()}
    if isinstance(item, list):
        return [convert_string_bools_to_bools(element) for element in item]
    if isinstance(item, str):
        return {"false": False, "true": True}.get(item.lower(), item)
    if item is None:
        return ""
    raise RuntimeError

def parse_xml_to_dict(xml_bytes):
    try:
        import xmltodict
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            "Unable to import xmltodict. "
            "xmltodict is required for using xml files, install using\n"
            "pip install xmltodict"
        )
    parsed_xml = xmltodict.parse(xml_bytes)
    parsed_xml = json.loads(json.dumps(parsed_xml))
    final_dict = convert_string_bools_to_bools(change_case_for_dict_keys(parsed_xml))
    return final_dict.get("root")
