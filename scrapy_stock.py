import requests, re, io, sys
from bs4 import BeautifulSoup
from lxml import etree


def getSotckInfo(keyword):
    try:
        t2 = time.time()
        rtStock = twstock.realtime.get(keyword)
        t3 = time.time()
        preStock = twstock.Stock(keyword)
        t4 = time.time()
        if not rtStock['success']:
            return '代號輸入錯誤'
    except:
        return '代號輸入錯誤'
    
    # identify market close time
    cTime = datetime.datetime.now()
    openTime = datetime.datetime(cTime.year, cTime.month, cTime.day, 9, 0)
    closeTime = datetime.datetime(cTime.year, cTime.month, cTime.day, 14, 30)
    if openTime < cTime < closeTime:
        t5 = time.time()
        rtPrice = float(rtStock['realtime']['latest_trade_price'])
        prePrice = preStock.price[-1] 
        t6 = time.time()
    else:
        t5 = time.time()
        rtPrice = preStock.price[-1]
        prePrice = preStock.price[-2]
        t6 = time.time()

    diff = round(rtPrice-prePrice, 2)
    percentage = round((rtPrice-prePrice)/prePrice*100, 2)
    upDown = "📈+" if diff > 0 else "📉"
    upDown = "(-)" if float(diff) == 0.0 else upDown
    reply = f"{keyword} {rtStock['info']['name']}  {rtPrice}\n漲跌幅 {upDown}{diff} ({percentage}%)"
    return reply, (t2,t3,t4,t5,t6)

def get_stockValue_from_anue(stockNum):
    url = f"https://invest.cnyes.com/twstock/tws/{stockNum}"
    web = requests.get(url) # get the website request
    selector = etree.HTML(web.text) #將源碼轉化為能被XPath匹配的格式
    elem = selector.xpath("/html/body/div[1]/div/div[2]/div[3]/div[2]/div[1]/div[3]/div[1]/div/span")[0] #返回為一列表
    print(elem.text)

def get_stock_table_from_yahoo(stockNum):
    from io import StringIO
    import pandas as pd
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{stockNum}.TW?period1=0&period2=1549258857&interval=1d&events=history&crumb=hP2rOschxO0"
    response = requests.get(url)
    df = pd.read_csv(StringIO(response.text))
    print(df)

def get_stockValue_from_twseAPI(stockNum):
    from io import StringIO
    import pandas as pd
    apiUrl = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{stockNum}.tw"
    response = requests.get(apiUrl)
    data = response.json()["msgArray"]
    if not data:
        return ['代號輸入錯誤']
    else: data = data[0]
    # df = pd.json_normalize(data)

    currentValue = float(data["z"]) if data['z'] is not '-' else 0.0
    preValue = float(data["y"])
    stockName = data["n"]

    diff = round(currentValue-preValue, 2)
    percentage = round(diff/preValue*100, 2)
    preValue = round(preValue, 2)
    
    upDown = "📈" if diff > 0 else "📉"
    upDown = "(-)" if float(diff) == 0.0 else upDown
    diff = "+"+str(diff) if diff >= 0 else "-"+str(diff)
    percentage = "+"+str(percentage) if percentage >= 0 else "-"+str(percentage)
    reply = f"{stockNum} {stockName:<5}\n{'昨收價':<5} {preValue}\n{'漲跌幅':<5}{diff} ({percentage}%){upDown}\n{'當前價':<5} {currentValue}"

    return [reply]

    

# get_stockValue_from_anue(3034)
# get_stock_Value_from_yahoo(1101)
# r = get_stockValue_from_twseAPI(2330)[0]
# print(r)
