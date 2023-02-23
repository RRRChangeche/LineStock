import requests
from lxml import etree
from twstock import realtime
import pandas as pd
import traceback, sys

    
def is_valid_stockNumber(msg):
    return True

def get_all_stock_codes():
    # get 
    res = requests.get("http://isin.twse.com.tw/isin/C_public.jsp?strMode=2")
    df = pd.read_html(res.text)[0]
    # remove useless cols and rows 
    df = df.drop([0, 1], axis=0)
    df = df.drop([1,2,5,6], axis=1)


def handle_error(error):
    error_class = type(error)
    detail = error.args[0] # details
    cl, exc, tb = sys.exc_info() # get Call Stack
    lastCallStack = traceback.extract_tb(tb)[-1] # get latest Call Stack
    fileName = lastCallStack[0]
    lineNum = lastCallStack[1]
    funcName = lastCallStack[2]
    errMsg = f"File {fileName}, line {lineNum}, in {funcName}: [{error_class}] {detail}" # .format(fileName, lineNum, funcName, error_class, detail)
    print(errMsg)

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
    # https://zys-notes.blogspot.com/2020/01/api.html
    # 5秒內超過3次會鎖IP一段時間
    apiUrl = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{stockNum}.tw|otc_{stockNum}.tw"
    response = requests.get(apiUrl)
    data = response.json()["msgArray"]
    if not data:
        return "代號輸入錯誤"
    else: data = data[0]

    currentValue = float(data["z"]) if data['z'] != '-' else 0.0
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

    return reply

def get_stockValue_from_sinopacAPI(apiObj, stockNum):
    try:
        # get stock name 
        stockName = realtime.get(stockNum)['info']['name']
        stockName = stockName if stockName else ""

        # get current stock value from sinopac api
        contracts = [apiObj.Contracts.Stocks[stockNum]]
        if not contracts: return ""
        snapshots = apiObj.snapshots(contracts)[0]
        
        # format reply 
        current_price = snapshots.close
        change_price = snapshots.change_price
        change_rate = snapshots.change_rate
        prev_price = current_price - change_price
        upDown = "📈" if change_price > 0 else "📉"
        sign = "+" if change_price >= 0 else "-"
        change_price = sign + str(change_price)
        change_rate = sign + str(change_rate)
        reply = f"{stockNum} {stockName:<5}\n{'昨收價':<5} {prev_price}\n{'漲跌幅':<5}{change_price} ({change_rate}%){upDown}\n{'當前價':<5} {current_price}"
        return reply
        
    except Exception as e:
        print(f"Failed in sinopac api: {str(e)}")
        handle_error(e)


# get_stockValue_from_anue(3034)
# get_stock_Value_from_yahoo(1101)
# r = get_stockValue_from_twseAPI(2330)[0]
# print(r)
