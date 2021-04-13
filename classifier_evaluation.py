'''
Script to test the classifier used in this project
For each category we evaluate 100 random pages 
'''

import random
import csv

# Connect to MongoDB atlas
from pymongo import MongoClient
accesstoken = ""
client = MongoClient(accesstoken)
# Seleect DB
db = client.get_database('wikitrend')
# Select single pages collection
pages = db.page_topic

categories = ["arts, culture and entertainment", "history and geography", "internet and game", "sport", "STEM","other"]

# CSV file with the results
with open('test_category.csv', 'w', newline='', encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Articolo","Description","Category","Check"])
    for cat in categories[5:]:
        pages_cat = pages.find({"category": cat})
        pages_cat = list(pages_cat)
        pages_sample = random.sample(pages_cat,100)
        for articolo in pages_sample:
            name = articolo["article"]
            if "description" in articolo.keys():
                description = articolo["description"]
            else:
                description = ""
            category = articolo["category"]
            print(name,"\t",description,"\t",category)
            # type yes if is the right category, otherwise type no
            check = input("Right? y or n \t")
            writer.writerow([name,description,category,check])
file.close()
