
def field_mapping(data, field_mappings):
    """
    Teljes adatsorra alkalmazza a field_mappings szabályokat,
    támogatva: törlés, átnevezés, concat (tetszőleges szeparátorral).
    """
    print("\n======= FIELD_MAPPING DEBUG =======")
    print("FIELD_MAPPINGS:", field_mappings)
    print("INPUT DATA SAMPLE:", data[:1])  # csak egy sort printelünk, ha nagy a data
    transformed = []

    concat_pairs = set()
    for i, row in enumerate(data):
        print(f"\n--- Row {i+1} ---")
        print("INPUT ROW:", row)
        new_row = {}
        '''
        # Concat-olt oszlopok
        for col, props in field_mappings.items():
            concat = props.get("concat", {})
            if concat.get("enabled", False):
                with_col = concat["with"]
                pair = tuple(sorted([col, with_col]))
                if pair in concat_pairs:
                    print(f"[{col}] + [{with_col}] pair ALREADY HANDLED -> SKIP")
                    continue
                concat_pairs.add(pair)
                first = props["newName"] if props.get("rename", False) and props.get("newName") else col
                with_props = field_mappings.get(with_col, {})
                second = with_props["newName"] if with_props.get("rename", False) and with_props.get("newName") else with_col
                sep = concat["separator"]
                concat_col = f"{first}{sep}{second}".strip()
                val1 = row.get(col, "")
                val2 = row.get(with_col, "")
                new_val = f"{val1}{sep}{val2}".strip()
                print(f" -> CONCAT: '{concat_col}' = '{val1}' + '{sep}' + '{val2}' -> '{new_val}'")
                new_row[concat_col] = new_val
                
                '''

        for col, value in row.items():
            props = field_mappings.get(col, {})
            if props.get("delete", False):
                print(f"SKIP [{col}] - marked for delete")
                continue
            if props.get("concat", {}).get("enabled", False):
                print(f"SKIP [{col}] - handled by concat")
                continue
            if props.get("rename", False) and props.get("newName"):
                new_col = props["newName"]
                print(f"RENAME [{col}] -> [{new_col}] = '{value}'")
            else:
                new_col = col
                print(f"KEEP [{col}] = '{value}'")
            new_row[new_col] = value
        print("NEW_ROW:", new_row)
        transformed.append(new_row)
    print("\nALL TRANSFORMED ROWS (first 3):", transformed[:3])
    print("======= FIELD_MAPPING DEBUG END =======\n")
    return transformed


def group_by(data, group_by_columns):
    print("\n======= GROUP_BY DEBUG =======")
    print("GROUP_BY_COLUMNS:", group_by_columns)
    grouped = {}

    for row in data:
        # tuple, hogy hash-elhető legyen
        key = tuple(row[k] for k in group_by_columns)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(row)

    # Kulcsokhoz rendelünk egyértelműen értékeket is vissza
    group_by_columns_result = [
        {
            "group": dict(zip(group_by_columns, key)),
            "items": items
        }
        for key, items in grouped.items()
    ]

    print("GROUPED DATA (first 3 groups):", group_by_columns_result[:3])
    print("======= GROUP_BY DEBUG END =======\n")
    return group_by_columns_result

def flatten_grouped_data(grouped_data):
    """
    A group_by által adott struktúrát (list of dict group + items) laposítja.
    Például:
    [
        {'group': {'region': 'Africa'}, 'items': [{...}, {...}]},
        {'group': {'region': 'Asia'}, 'items': [{...}, {...}]}
    ]
    ->
    [
        {'region': 'Africa', ...},
        {'region': 'Africa', ...},
        {'region': 'Asia', ...},
        ...
    ]
    """
    flattened = []
    for group in grouped_data:
        group_keys = group['group']
        for item in group['items']:
            flat_row = {**group_keys, **item}  # egyesítjük a group értékeit az itemmel
            flattened.append(flat_row)
    return flattened


def order_by(data, order_by_column, order_direction):
    print("\n======= ORDER_BY DEBUG =======")
    print("ORDER_BY_COLUMN:", order_by_column)

    if not order_by_column:
        print("No order_by_columns provided, returning original data.")
        return data

    def sort_key(x):
        # Ha több oszlopra rendezel, mindegyikre alkalmazd
        return tuple((x.get(col) if x.get(col) is not None else "") for col in order_by_column)

    if order_direction == "asc":
        order_by_result = sorted(data, key=sort_key)
    elif order_direction == "desc":
        order_by_result = sorted(data, key=sort_key, reverse=True)

    print("SORTED DATA (first 3 rows):", order_by_result[:3])
    print("======= ORDER_BY DEBUG END =======\n")
    return order_by_result