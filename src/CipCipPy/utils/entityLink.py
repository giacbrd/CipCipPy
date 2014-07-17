__author__ = 'Giacomo Berardi <barnets@gmail.com>'


def entities(text, dxtr, link_prob):
    """Returns all the useful information from the entity linking system for a text"""
    spots = dxtr.spot(text)
    mentions = {}
    for spot in spots:
        for entity in spot["candidates"]:
            ent_id = entity["entity"]
            if ent_id not in mentions:
                # Don not keep entity candidates of mentions
                mentions[ent_id] = [{key: value for key, value in m.iteritems() if key != "candidates"}
                                    for m in dxtr.get_spots(ent_id) if m["linkProbability"] > link_prob]
    return spots, mentions