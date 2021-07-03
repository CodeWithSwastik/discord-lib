import json
import re

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

def apply_func_to_all_strings(dictionary_or_list, func):
    new_dict = {}
    new_list = []
    if isinstance(dictionary_or_list, list):
        for item in dictionary_or_list:
            if isinstance(item, str):
                new_list.append(func(item))
            else:
                new_list.append(apply_func_to_all_strings(item, func))
    elif isinstance(dictionary_or_list, dict):
        for item in dictionary_or_list:
            if isinstance(dictionary_or_list[item], str):
                new_dict[item] = func(dictionary_or_list[item])
            else:
                new_dict[item] = apply_func_to_all_strings(dictionary_or_list[item], func)
    
    return new_dict or new_list or dictionary_or_list

def spformat(string, namespace):
    matcher = re.compile(r"(?:\{\{)([a-zA-Z0-9\.]+)(?:\}\})")
    replacer = "{0.\\1}"
    final = matcher.sub(replacer, string).format(namespace)


    # math nodes
    matcher = re.compile(r"(?:<<)([0-9\. \+\-/\*\(\)]+)(?:>>)")

    for match in re.findall(matcher,final):
        evaled_match = eval(match)
        final = final.replace(f"<<{match}>>", str(evaled_match), 1)
    return final
