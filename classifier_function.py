'''
List of function for categorized wikipedia page with ORES classifier
'''

def api_id(title):
    '''
    Building URL for API call to get the available ids of a page
    title: page title
    '''
    url = "https://en.wikipedia.org/w/api.php?action=query&prop=pageprops|revisions&rvprop=ids&format=json&titles="+title
    return url

def get_pageid(risultato):
    '''
    Getting page id from API ids result
    '''
    page_inf = risultato["query"]["pages"]
    page_id = int(list(page_inf.keys())[0])
    return page_id

def get_revid(risultato):
    '''
    Getting the last revision id from API ids result
    '''
    page_inf = risultato["query"]["pages"]
    page_id = list(page_inf.keys())[0]
    rev_id = page_inf[page_id]['revisions'][0]["revid"]
    return rev_id

def get_wikidataid(risultato):
    '''
    Getting page associated wikidata node id from API ids result
    '''
    page_inf = risultato["query"]["pages"]
    page_id = list(page_inf.keys())[0]
    if "pageprops" in list(page_inf[page_id].keys()):
        try:
            wikidata_id = page_inf[page_id]['pageprops']['wikibase_item']
            return wikidata_id
        except KeyError:
            pass
    else:
        pass

def api_nodeid(wikidata_id):
    '''
    Building URL for API call to get the wikidata id node type
    '''
    url = "https://www.wikidata.org/w/api.php?action=wbgetclaims&property=P31&format=json&entity="+wikidata_id
    return url

def get_nodeid(risultato):
    '''
    Getting wikidata id node type from API nodeid result
    '''
    # If wikidata node has not type property (P31) return None
    if len(risultato["claims"]) == 0:
        pass
    else:
        node_type = risultato["claims"]["P31"][0]['mainsnak']['datavalue']['value']['id']
        return node_type

def get_nodetype(node_type):
    '''
    Based on the type of node the function get the type of a page and, if possible, the ORES cat associated
    node_type: wikidata id node type
    return: a list with page_type and ores_cat (optional); page_type can be "biography" or "other"
    '''
    if node_type == "Q5": # human
      page_type = "biography"
      return [page_type]
    elif node_type in ["Q229390", "Q11424", "Q5398426","Q24856","Q526877","Q18011172"]: #film, film series, tv series, web series, 3d film, film project
      page_type = "other"
      ORES_cat  = "Culture.Media.Films"
      return [page_type,ORES_cat]
    elif node_type in ["Q7889","Q7058673"]: # video game, video game series
      page_type = "other"
      ORES_cat  = "Culture.Media.Video games"
      return [page_type,ORES_cat]
    elif node_type in ["Q638", "Q21186480", "Q273057"]: # single, music, discography
      page_type = "other"
      ORES_cat = "Culture.Media.Music"
      return [page_type,ORES_cat]
    elif node_type in ["Q47461344", "Q8261", "Q571", "Q1667921"]: # written work, book , novel series
      page_type = "other"
      ORES_cat  = "Culture.Media.Books"
      return [page_type,ORES_cat]
    else:
      page_type = "other"
      return [page_type]

def clean_cat(cat):
    '''
    Cleaning predicted categories from ores to get a single, plausible, specific and useful category
    cat: ordered list with predicted categories for the page
    return: pred_cat, most likely category

    clean_cat(['Culture.Biography.Biography*','Culture.Media.Media*','Culture.Media.Films',"STEM.STEM*"]) -> return 'Culture.Media.Films'
    '''
    # Delete biographical categories
    if 'Culture.Biography.Biography*' in cat:
        cat.remove('Culture.Biography.Biography*')
    if 'Culture.Biography.Women' in cat:
        cat.remove('Culture.Biography.Women')
    # If there isn't any category then pred_cat is "other"
    if len(cat) == 0:
        pred_cat = "other.category"
    # If there is only one category I take that
    elif len(cat) == 1:
        pred_cat = cat[0]
    # If the first category isn't of geographical type I take that
    elif cat[0][:3] != "Geo":
        pred_cat = cat[0]
    # In the other cases I search a better category if possible
    else:
        result= []
        for categoria in cat:
            if categoria[:3] != "Geo":
                result.append(categoria)
        if len(result) == 0:
            pred_cat = cat[0]
        else:
            pred_cat = result[0]
    return pred_cat

def api_draftcat(rev_id):
    '''
    Building URL for API call to classify the page with ores draft topic method
    '''
    url = 'https://ores.wikimedia.org/v3/scores/enwiki/?models=drafttopic&revids='+str(rev_id)
    return url

def api_articlecat(rev_id):
    '''
    Building URL for API call to classify the page with ores draft topic method
    '''
    url = 'https://ores.wikimedia.org/v3/scores/enwiki/?models=articletopic&revids='+str(rev_id)
    return url

def get_draftcat(risultato):
    '''
    Getting predicted categories from API draftcat result
    return: ordered list with most likely categories for the page
    '''
    if "enwiki" in risultato.keys():
        cat_prob = risultato["enwiki"]["scores"]
        rev_id = list(cat_prob.keys())[0]
        cat_prob = cat_prob[str(rev_id)]["drafttopic"]["score"]["prediction"]
    else:
        cat_prob = []
    return cat_prob

def get_articlecat(risultato):
    '''
    Getting predicted categories from API articlecat result
    return: ordered list with most likely categories for the page
    '''
    if "enwiki" in risultato.keys():
        cat_prob = risultato["enwiki"]["scores"]
        rev_id = list(cat_prob.keys())[0]
        cat_prob = cat_prob[str(rev_id)]["articletopic"]["score"]["prediction"]
    else:
        cat_prob = []
    return cat_prob

def ores_converter (ores_cat):
  '''
  Converting ORES category in new taxonomy
  return: new category

  new category:
    art, culture and entertainment
    history and geography 
    internet and game
    sport
    STEM
    other
  '''
  diz_cat = {
  "Culture.Food and drink": "other",
  "Culture.Internet culture": "internet and game",
  "Culture.Linguistics": "arts, culture and entertainment",
  "Culture.Literature": "arts, culture and entertainment",
  "Culture.Media.Books": "arts, culture and entertainment",
  "Culture.Media.Entertainment": "arts, culture and entertainment",
  "Culture.Media.Films": "arts, culture and entertainment",
  "Culture.Media.Media*": "arts, culture and entertainment",
  "Culture.Media.Music": "arts, culture and entertainment",
  "Culture.Media.Radio": "arts, culture and entertainment",
  "Culture.Media.Software": "STEM",
  "Culture.Media.Television": "arts, culture and entertainment",
  "Culture.Media.Video games": "internet and game",
  "Culture.Performing arts": "arts, culture and entertainment",
  "Culture.Philosophy and religion": "arts, culture and entertainment",
  "Culture.Sports": "sport",
  "Culture.Visual arts.Architecture": "arts, culture and entertainment",
  "Culture.Visual arts.Comics and Anime": "arts, culture and entertainment",
  "Culture.Visual arts.Fashion": "arts, culture and entertainment",
  "Culture.Visual arts.Visual arts*": "arts, culture and entertainment",
  "Geography.Geographical": "history and geography",
  "Geography.Regions.Africa.Africa*": "history and geography",
  "Geography.Regions.Africa.Central Africa": "history and geography",
  "Geography.Regions.Africa.Eastern Africa": "history and geography",
  "Geography.Regions.Africa.Northern Africa": "history and geography",
  "Geography.Regions.Africa.Southern Africa": "history and geography",
  "Geography.Regions.Africa.Western Africa": "history and geography",
  "Geography.Regions.Americas.Central America": "history and geography",
  "Geography.Regions.Americas.North America": "history and geography",
  "Geography.Regions.Americas.South America": "history and geography",
  "Geography.Regions.Asia.Asia*": "history and geography",
  "Geography.Regions.Asia.Central Asia": "history and geography",
  "Geography.Regions.Asia.East Asia": "history and geography",
  "Geography.Regions.Asia.North Asia": "history and geography",
  "Geography.Regions.Asia.South Asia": "history and geography",
  "Geography.Regions.Asia.Southeast Asia": "history and geography",
  "Geography.Regions.Asia.West Asia": "history and geography",
  "Geography.Regions.Europe.Eastern Europe": "history and geography",
  "Geography.Regions.Europe.Europe*": "history and geography",
  "Geography.Regions.Europe.Northern Europe": "history and geography",
  "Geography.Regions.Europe.Southern Europe": "history and geography",
  "Geography.Regions.Europe.Western Europe": "history and geography",
  "Geography.Regions.Oceania": "history and geography",
  "History and Society.Business and economics": "history and geography",
  "History and Society.Education": "history and geography",
  "History and Society.History": "history and geography",
  "History and Society.Military and warfare": "history and geography",
  "History and Society.Politics and government": "history and geography",
  "History and Society.Society": "history and geography",
  "History and Society.Transportation": "history and geography",
  "STEM.Biology": "STEM",
  "STEM.Chemistry": "STEM",
  "STEM.Computing": "STEM",
  "STEM.Earth and environment": "STEM",
  "STEM.Engineering": "STEM",
  "STEM.Libraries & Information": "STEM",
  "STEM.Mathematics": "STEM",
  "STEM.Medicine & Health": "STEM",
  "STEM.Physics": "STEM",
  "STEM.STEM*": "STEM",
  "STEM.Space": "STEM",
  "STEM.Technology": "STEM",
  "other.category": "other"
}
  return diz_cat[ores_cat]