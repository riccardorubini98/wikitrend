def get_topart(year, month, day, limit):
    
    '''
    Getting cleaned top pages for the desired period
    year: year of interest
    month: month of interest
    day: day of interest; with "all-days" value get top pages by month
    limit: number of pages to get (theoretical MAX is 1000)
    return: ordered list of the top pages without pages like Main Page, Special:Page and other like that

    get_topart("2016","01","01",10) -> first ten pages for January 1st 2016
    '''
    import requests
    URL = api_top(year,month,day)
    # Start session
    S = requests.Session()
    # Start API call
    headers = {'User-Agent': "<r.rubini3@campus.unimibi.it> University project"}
    page = requests.get(URL, headers=headers)
    # Save result in json format
    risultato = page.json()
    # clean result
    ris_clean = clean_topart(risultato)
    # Select desired pages
    output = ris_clean[0:limit]
    return output

def api_top(year, month, day):
    '''
    Building URL for API call to get the top pages from desired period
    year: year of interest
    month: month of interest
    day: day of interest; with "all-days" value get top pages by month
    return: api url

    api_top("2016","01","01") -> api url for the first ten pages for January 1st 2016
    '''
    end_point = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia"
    access = "all-access"
    URL = "/".join([end_point, access, year, month, day])
    return URL

def clean_topart(risultato):
    '''
    Cleaning API top result, deleting pages like Main Page, Special:Page and other like that
    return: ordered and cleaned list
    '''
    page_list = risultato["items"][0]['articles']
    # Delete usless page
    output = []
    for articolo in page_list:
        if (articolo["article"] == "Main_Page" or articolo["article"].startswith("Special:") or
            articolo["article"].startswith("Portal:") or articolo["article"].startswith("Template:") or
            articolo["article"].startswith("File:") or articolo["article"].startswith("Help:") or
            articolo["article"].startswith("User:") or articolo["article"].startswith("Wikipedia:") or
            articolo["article"] == "Null"):
            pass
        else:
            del articolo["rank"]
            output.append(articolo)
    return output

def get_topday(year,month,day_list):
    '''
    Getting the most viewed page for each day in a month with page_id
    year: year of interest
    month: month of interest
    day_list: list of the day in a month
    return: ordered list with the top page for each single day with page_id

    day_31 = ["01","02",...,"30","31"]
    get_topday("2016","01",day_31) -> top page for each day in January 2016
    '''
    top_day = []
    urls = []
    for day in day_list:
        url = api_top(year,month,day)
        urls.append(url)
        risultato = async_call(urls,size=10)
    for r in risultato:
        ris = r.json()
        ris_clean = clean_topart(ris)
        first_page = ris_clean[0]
        top_day.append(first_page)
        # get page_id
        urls = []
        for articolo in top_day:
            url = api_id(articolo["article"])
            urls.append(url)
        result = async_call(urls,10)
        i=0
        for r in result:
            page_id = get_pageid(r.json())
            top_day[i]["page_id"] = page_id 
            top_day[i]["day_of_month"] = i+1
            i+=1
    return top_day

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

def async_call(urls,size=10):
    '''
    Making parallel API requests
    urls: list of urls to make API calls
    size: number of requests at the same time
    return: list of API calls results
    '''
    import grequests
    import requests
    session = requests.Session()
    headers = {'User-Agent': "<r.rubini3@campus.unimibi.it> University project"}
    reqs = [grequests.get(link, headers=headers,session=session) for link in urls]
    resp = grequests.map(reqs,size=size)
    return resp