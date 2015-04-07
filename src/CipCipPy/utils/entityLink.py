__author__ = 'Giacomo Berardi <barnets@gmail.com>'


def entities(text, dxtr, link_prob):
    """Returns all the useful information from the entity linking system for a text"""
    dxtr_spots = dxtr.spot(text)
    spots = []
    mentions = {}
    all_entities = set(entity["entity"] for spot in dxtr_spots if spot["linkFrequency"] > 2
                       for entity in spot["candidates"] if entity["commonness"] >= 0.1 and entity["freq"] > 2)
    for spot in dxtr_spots:
        if spot["linkFrequency"] <= 2:
            continue
        spot["candidates"] = [ent for ent in spot["candidates"] if ent["commonness"] >= 0.1 and ent["freq"] > 2]
        for entity in spot["candidates"]:
            ent_id = entity["entity"]
            if ent_id not in mentions:
                # Do not keep entity candidates of mentions
                # mentions[ent_id] = [{key: value for key, value in m.iteritems() if key != "candidates"}
                #                     for m in dxtr.get_spots(ent_id) if m["linkProbability"] > link_prob]
                mentions[ent_id] = [m for m in dxtr.get_spots(ent_id) if m["linkProbability"] >= link_prob
                                    and m["linkFrequency"] > 2]
        spots.append(spot)
    # Clean up mentions
    for ent_id in mentions.keys():
        to_delete = set()
        for i, ment in enumerate(mentions[ent_id]):
            ment["candidates"] = [ent for ent in ment["candidates"] if ent["entity"] in all_entities
                                  and ent["commonness"] >= 0.1 and ent["freq"] > 2]
            if not ment["candidates"]:
                to_delete.add(i)
        mentions[ent_id] = [ment for i, ment in enumerate(mentions[ent_id]) if i not in to_delete]
        if not mentions[ent_id]:
            del mentions[ent_id]
    return spots, mentions