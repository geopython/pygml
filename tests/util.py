def compare_trees(e1, e2):
    # from https://stackoverflow.com/a/24349916/746961
    if e1.tag != e2.tag:
        raise AssertionError(f'Tag: {e1.tag} != {e2.tag}')
    if (e1.text or '').strip() != (e2.text or '').strip():
        raise AssertionError(f'Text: {e1.text} != {e2.text}')
    if (e1.tail or '').strip() != (e2.tail or '').strip():
        raise AssertionError(f'Tail: {e1.tail} != {e2.tail}')
    if e1.attrib != e2.attrib:
        raise AssertionError(f'Attributes: {e1.attrib} != {e2.attrib}')
    if len(e1) != len(e2):
        raise AssertionError(f'Child nodes: {len(e1.tag)} != {len(e2.tag)}')
    return all(compare_trees(c1, c2) for c1, c2 in zip(e1, e2))
