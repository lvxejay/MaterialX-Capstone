def enumItemsFromList(itemData):
    items = []
    for _id, element in enumerate(itemData):
        items.append((element, element, "", "NONE", _id))
    if len(items) == 0:
        items = [("NONE", "NONE", "")]
    return items
