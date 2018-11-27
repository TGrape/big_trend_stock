from jqdatasdk import *
import datetime
import pandas as pd

##认证用户,请将10086改为你的手机号，password改为你的密码
auth('10086','password')

#获取所有股票
def get_stocks_code():
    return get_all_securities(['stock']).index
#获取股票价格，默认180天    
def get_prices_day(security,price_count=180):
    normalized_security = normalize_code(security)    
    trade_prices = get_price(normalized_security, 
                             frequency='daily', 
                             skip_paused=True, 
                             fq='pre',
                             end_date=datetime.datetime.now(),
                             count=price_count)
    print(trade_prices[price_count-2:price_count])
    return trade_prices
    
    
if __name__ == "__main__":
    stocks = get_stocks_code()
    print("股票数量：",len(stocks))
    days = 180
    stocks_selected = []
    try:
        for stock in stocks:
            print("开始处理股票 : ",stock)
            day_prices = get_prices_day(stock,days)
            price_close = day_prices['close']
            #price_close = day_prices['high']
            ma50 = price_close.rolling(window=50,center=False,min_periods=50).mean()
            ma50_tp = [x>y for (x,y) in zip(price_close,ma50)]
            print("--------------股票%s收盘与50日均值比较结果------------" % stock)
            print(ma50_tp[days-10:])
            ema6 = price_close.ewm(span=6).mean()
            ema18 = price_close.ewm(span=18).mean()
            ema108 = price_close.ewm(span=108).mean()
                     
                        
            false_count = 0
            for mt in ma50_tp[120:170]:
                if not mt:
                    false_count += 1
            if false_count>45: #均值突破1-3日
                if ma50_tp[days-1] or (ma50_tp[days-1] and ma50_tp[days-2]) or (ma50_tp[days-1] and ma50_tp[days-2] and ma50_tp[days-3]):
                    ema_result1 = [x>y for (x,y) in zip(ema6,ema18)]
                    print("--------------股票%s 6日与18日移动均值比较结果------------" % stock)
                    print(ema_result1[days-10:])                    
                    ema_result2 = [x>y for (x,y) in zip(ema18,ema108)]
                    print("--------------股票%s 18日与108日移动均值比较结果------------ " % stock)                    
                    ema_result3 = [x>y for (x,y) in zip(ema6,ema108)]
                    print("--------------股票%s 6日与108日移动均值比较结果------------ " % stock)
                    print(ema_result3[days-10:])
                    if ema_result1[days-1] and not ema_result2[days-1] and not ema_result3[days-1]:
                        ema_true_count = 0
                        for result in ema_result1[days-10:]:
                            if result:
                                ema_true_count += 1 
                        ma_true_count = 0
                        for mt in ma50_tp[days-10:]:
                            if mt:
                                ma_true_count += 1
                        if ema_true_count<3 and  ma_true_count<6:  #突破但还没有大涨      
                            stocks_selected.append(stock)
            
    except Exception as e:
        print(e)
    finally:
        print("选择的股票：",stocks_selected)
