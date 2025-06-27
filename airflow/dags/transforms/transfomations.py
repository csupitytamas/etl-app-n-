
def field_mapping(data, col_rename_map, final_columns):
    """
    Kifejezetten úgy írjuk meg, hogy:
      - csak a végleges oszlopneveket tartalmazza a visszaadott dict
      - csak azok a kulcsok maradnak, amik a final_columns-ban vannak
      - minden átnevezés, törlés, sorrend kezelve
    """
    print("\n======= FIELD_MAPPING (pro) =======")
    print("RENAME_MAP:", col_rename_map)
    print("FINAL_COLUMNS:", final_columns)
    print("INPUT DATA SAMPLE:", data[:1])
    transformed = []

    for i, row in enumerate(data):
        new_row = {}
        for orig_col, final_col in col_rename_map.items():
            if final_col in final_columns:
                value = row.get(orig_col, row.get(final_col))
                new_row[final_col] = value
        # Csak a végleges sorrenddel
        ordered_row = {col: new_row.get(col) for col in final_columns}
        print(f"TRANSFORMED ROW {i+1}:", ordered_row)
        transformed.append(ordered_row)
    print("======= FIELD_MAPPING END =======\n")
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