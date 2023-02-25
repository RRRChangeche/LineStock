'''
Usage:
    python getStockCodes.py [-n|-a|-h]

Options:
    -n    Insert new stock codes.
    -a    Update all stock codes, including its stock name, market_type,...etc.
    -h    Help.
'''

from utility import connect_to_mongodb, handle_error
import requests
import pandas as pd
from pymongo import UpdateOne
import sys


def update_new_stockCodes(collection):
    try:
        # get old data
        old_codes = set()
        result = collection.find({})
        while result.alive:
            old_codes.add(result.next()['code'])
        
        # get new data
        # get html table from url
        res = requests.get("http://isin.twse.com.tw/isin/C_public.jsp?strMode=2")
        df = pd.read_html(res.text)[0]
        df.drop([0, 1], axis=0, inplace=True)   # remove useless cols and rows 
        df.drop([1,2,5,6], axis=1, inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Create a new document to update "stock.tw_market" collection by iterating rows in df
        docs_to_update = []
        for i, row in df.iterrows():
            code_name = row[0].split('\u3000')
            if len(row) < 2 or len(code_name) < 2: continue
            code, name = code_name[:2]
            market_type = row[3]
            industry_type = row[4]
            
            # check if exists in old_codes
            if code in old_codes: continue

            # if not exists, then insert into database
            new_doc = {
                "code": code,
                "name": name,
                "market_type": market_type,
                "industry_type": industry_type
            }

            # Update stock codes list in MongoDB
            query = {"code": code}
            update = {"$set": new_doc }
            docs_to_update.append(UpdateOne(query, update, upsert=True))

        # Update all differences 
        if docs_to_update != []:
            result = collection.bulk_write(docs_to_update)
            print("INFO: Update new codes completed!")
            print("Documents modified: " + str(result.modified_count))
            print("Documents upserted: " + str(result.upserted_count))
            print("Documents upserted_ids: " + str(result.upserted_ids))
        else:
            print("INFO: No new codes to update!")

        # Disconnect db
        client.close()

    except Exception as e:
        handle_error(e)
        client.close()


def update_all_stockInfo(collection):
    try:
        # get new data
        # get html table from url
        res = requests.get("http://isin.twse.com.tw/isin/C_public.jsp?strMode=2")
        df = pd.read_html(res.text)[0]
        df.drop([0, 1], axis=0, inplace=True)   # remove useless cols and rows 
        df.drop([1,2,5,6], axis=1, inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Create a new document to update "stock.tw_market" collection by iterating rows in df
        docs_to_update = []
        for i, row in df.iterrows():
            code_name = row[0].split('\u3000')
            if len(row) < 2 or len(code_name) < 2: continue
            code, name = code_name[:2]
            market_type = row[3]
            industry_type = row[4]
   
            # if not exists, then insert into database
            new_doc = {
                "code": code,
                "name": name,
                "market_type": market_type,
                "industry_type": industry_type
            }

            # Update stock codes list in MongoDB
            query = {"code": code}
            update = {"$set": new_doc }

            # Update and compare data difference
            old_doc = collection.find_one(query)
            if old_doc is None:
                # if doc not exists in db, insert it
                docs_to_update.append(UpdateOne(query, update, upsert=True))
            else:
                # if doc exists, but has difference, update it
                old_doc.pop("_id", None)    # ignore "_id" column
                if old_doc != new_doc:
                    docs_to_update.append(UpdateOne(query, update))
            
        # Update all differences 
        if docs_to_update != []:
            result = collection.bulk_write(docs_to_update)
            print("INFO: Update all codes completed!")
            print("Documents modified: " + str(result.modified_count))
            print("Documents upserted: " + str(result.upserted_count))
            print("Documents upserted_ids: " + str(result.upserted_ids))
        else:
            print("INFO: No new codes to update!")

        # Disconnect db
        client.close()

    except Exception as e:
        handle_error(e)
        client.close()


if __name__ == '__main__':
    # Set Mongo DB connection
    client = connect_to_mongodb()

    # Refer to "stock.tw_market" collection
    tw_market_collection = client.stock.tw_market
    print(f'INFO: connect to collection "{client.stock.name}.{tw_market_collection.name}"')

    # Execute 
    if len(sys.argv) > 1: 
        if sys.argv[1] == '-n':
            print("INFO: Insert new stock codes!")
            update_new_stockCodes(tw_market_collection)
        elif sys.argv[1] == '-a':
            print("INFO: Update all stock codes!")
            update_all_stockInfo(tw_market_collection)
        elif sys.argv[1] == '-h':
            print("INFO: Please try: python getStockCodes.py [-n|-a|-h]")
            print("INFO: ")
            print(" -n : Insert new stock codes.")
            print(" -a : Update all stock codes, including its stock name, market_type,...etc.")
            print(" -h : Help.")
        else:
            print("INFO: Invalid argument!")
            print("INFO: Please try: python getStockCodes.py [-n|-a|-h]")
    else:
        print("INFO: Please try: python getStockCodes.py [-n|-a|-h]")


'''
update one by one takes 8m49s.

To improve performance, update using bulk_write:
- get old_codes from database
- get new codes from html table of given url
- compare new and old codes
- if it has new codes, then insert those new codes into database
- using bulk_write to update all differences in one time

update only new codes takes 19s.
'''
    