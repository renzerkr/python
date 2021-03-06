import time
import pyupbit
import datetime
import telegram

access = "your-access-upbit" #upbit access key
secret = "your-secret-upbit" #upbit secrect key
token = "your-token-telegram" #telegram api token

#telegram init
bot = telegram.Bot(token = token)
chat_id = "your-telegram-chat-id" #telegram chat id

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# log in upbit
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# start msg telegram send
text = 'autotrade start'
bot.sendMessage(chat_id = chat_id , text=text)
tmp_target_price = get_target_price("KRW-BTC", 0.5)
tmp_ma15 = get_ma15("KRW-BTC")
text="BTC targe_price:"+str(tmp_target_price)+"ma15:"+str(tmp_ma15)
bot.sendMessage(chat_id = chat_id , text=text)

while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", 0.5)
            ma15 = get_ma15("KRW-BTC")
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price and ma15 < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    buy_result = upbit.buy_market_order("KRW-BTC", krw*0.9995)
                    text="BTC(BTC) buy : " +str(buy_result)
                    bot.sendMessage(chat_id = chat_id , text=text)
        else:
            btc = get_balance("BTC")
            #starting new day

            if btc > 0.00008:
                sell_result = upbit.sell_market_order("KRW-BTC", btc*0.9995)
                text="BTC(BTC) sell : " +str(sell_result)
                bot.sendMessage(chat_id = chat_id , text=text)
        time.sleep(1)
    except Exception as e:
        print(e)
        text="exc error=" + str(e)
        bot.sendMessage(chat_id = chat_id , text=text)
        time.sleep(1)