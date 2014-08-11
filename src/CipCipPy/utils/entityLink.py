__author__ = 'Giacomo Berardi <barnets@gmail.com>'


def entities(text, dxtr, link_prob):
    """Returns all the useful information from the entity linking system for a text"""
    dxtr_spots = dxtr.spot(text)
    spots = []
    mentions = {}
    all_entities = set(entity["entity"] for spot in dxtr_spots if spot["linkFrequency"] > 2
                       for entity in spot["candidates"] if entity["commonness"] >= 0.1)
    for spot in dxtr_spots:
        if spot["linkFrequency"] <= 2:
            continue
        spot["candidates"] = [ent for ent in spot["candidates"] if ent["commonness"] >= 0.1]
        for entity in spot["candidates"]:
            ent_id = entity["entity"]
            if ent_id not in mentions:
                # Don not keep entity candidates of mentions
                # mentions[ent_id] = [{key: value for key, value in m.iteritems() if key != "candidates"}
                #                     for m in dxtr.get_spots(ent_id) if m["linkProbability"] > link_prob]
                mentions[ent_id] = [m for m in dxtr.get_spots(ent_id) if m["linkProbability"] >= link_prob
                    and m["linkFrequency "] > 2]
        spots.append(spot)
    for ment in mentions:
        ment["candidates"] = [ent for ent in ment["candidates"] if ent["entity"] in all_entities]
        assert(ment["candidates"])
    return spots, mentions