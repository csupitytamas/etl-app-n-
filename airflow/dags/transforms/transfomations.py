def field_mapping(data, field_mappings):
    """
    Egy teljes adatsorra alkalmazza a field_mappings-ben megadott szabályokat.
    """
    transformed = []
    for row in data:
        new_row = {}
        for col, value in row.items():
            props = field_mappings.get(col, {})
            # Ha törlendő, ugorjuk!
            if props.get("delete", False):
                continue
            # Ha át kell nevezni
            if props.get("rename", False) and props.get("newName"):
                new_col = props["newName"]
            else:
                new_col = col
            new_row[new_col] = value
        transformed.append(new_row)
    return transformed