"""
研究思路：
  股票处于底部转向上升趋势，通过神仙大趋势指标，可以确定趋势向上做多，买入操作，盈利概率极高。
  神仙大趋势：单独以日k线大趋势走势判断涨跌并进行实战买卖操作，适合大众操作长中短皆可
    1.股票按趋势来分就分三种：上涨，下跌，震荡！
    2.神仙大趋势都是非常实用的。适用于国内外的指数，个股，大宗商品等品种。
  下跌趋势：有效规避风险，把损失降到最低，避免深度套牢!
"""

from jqdatasdk import *
import datetime
import pandas as pd

##认证用户,请将10086改为你的手机号，password改为你的密码
auth('10086','password')

#获取所有股票
def get_stocks_code(test):
    #return ['300397']
    if test:
        return ['300442.XSHE']
    else:
        return get_all_securities(types=['stock']).index
#获取股票价格，默认180天    
def get_prices_day(security,price_count=180):
    normalized_security = normalize_code(security)    
    trade_prices = get_price(normalized_security, 
                             frequency='daily', 
                             skip_paused=True, 
                             fq='pre',
                             end_date=datetime.datetime.now(),
                             count=price_count)
    #print(trade_prices[price_count-20:price_count])
    return trade_prices
    
def get_macd_data(prices,short=0,long=0,mid=0):
    if short==0:
        short=12
    if long==0:
        long=26
    if mid==0:
        mid=9
    data = pd.Series()
    #计算短期的ema，使用pandas的ewm得到指数加权的方法，mean方法指定数据用于平均
    data['sema']=prices.ewm(span=short).mean()
    #计算长期的ema，方式同上
    data['lema']=prices.ewm(span=long).mean()
    #填充为na的数据
    data.fillna(0,inplace=True)
    #计算dif，加入新列data_dif
    data['data_dif']=data['sema']-data['lema']
    
    #计算dea
    data['data_dea']=pd.Series(data['data_dif']).ewm(span=mid).mean()
    #计算macd
    data['data_macd']=2*(data['data_dif']-data['data_dea'])
    #填充为na的数据
    data.fillna(0,inplace=True)
    #返回data的三个新列
    return data['data_macd']
    
if __name__ == "__main__":
    stocks = get_stocks_code(False)
    print("股票数量：",len(stocks))
    all_days =180
    days = 180
    #底部突破股票
    stocks_selected_low = []
    #强势股票
    stocks_selected_median = []
    #超强势股票
    stocks_selected_high = []
    try:
        for stock in stocks:
            print("开始处理股票 : ",stock)
            day_prices = get_prices_day(stock,all_days)            
            info = get_security_info(stock)    
            if (datetime.datetime.now()-pd.to_datetime(day_prices.index[-1])).days>7:
                print('股票停牌',stock)
                continue
            minus = info.end_date - datetime.date(2200,1,1)
            minux = minus.days
            if minux <0:
                print('股票退市',stock)
                continue
            if info.display_name.find('ST')>=0:
                print('股票ST',stock)
                continue
            minus = datetime.date.today()-info.start_date
            minux = minus.days
            if minux<80:
                print('股票不到80天',stock)
                continue
            length_prices = len(day_prices)
            
            price_close = day_prices['close'][0:length_prices-(all_days-days)]
            length_prices = len(price_close)
            #price_close = day_prices['high']
            ma50 = price_close.rolling(window=60,center=False,min_periods=60).mean()
            ma50_tp = [x>y for (x,y) in zip(price_close,ma50)]
            length_ma50_tp = len(ma50_tp)
            #print("--------------股票%s收盘与50日均值比较结果------------" % stock)
            #print(ma50_tp[length_ma50_tp-10:])
            ema6 = price_close.ewm(span=6).mean()
            ema18 = price_close.ewm(span=18).mean()
            ema108 = price_close.ewm(span=108).mean()

            prices_open10 = day_prices['open'][days-12:days]
            prices_close10 = day_prices['close'][days-12:days]
            #股票红盘数量
            red = [x>=y for (x,y) in zip(prices_close10,prices_open10)]            
            red_count = 0
            if_red_ok = False
            count = 0
            for i in range(11,-1,-1):
                count = count+1                
                if red[i]:
                    red_count = red_count+1
                    if count == 8 and red_count>=6:
                        if_red_ok = True 
                    if count == 10 and red_count>=7:
                        if_red_ok = True
                    if count == 12 and red_count>=8:
                        if_red_ok = True
                        
            false_count = 0
            for mt in ma50_tp[length_prices-30:]:
                if not mt:
                    false_count += 1
            #print('股票30天内底部滞留天数',false_count)            
            print('股票是否满足红盘比例',if_red_ok,red)
            ema_result1 = [x>y for (x,y) in zip(ema6,ema18)]
            length_ema_result1 = len(ema_result1)
            #print("--------------股票%s 6日与18日移动均值比较结果------------" % stock)
            #print(ema_result1[days-10:])                    
            ema_result2 = [x>y for (x,y) in zip(ema18,ema108)]
            
            length_ema_result2 = len(ema_result2)
            #print("--------------股票%s 18日与108日移动均值比较结果------------ " % stock) 
            #print(ema_result2[days-10:])
            ema_result3 = [x>y for (x,y) in zip(ema6,ema108)]
            length_ema_result3 = len(ema_result3)
            if_weak = False
            #大阴线-5.5%，阴线-3%2天，实质为下跌3天
            weak_count = 0
            minus_count = 0
            for i in range(1,7) : 
                if  price_close[length_prices-i]<price_close[length_prices-i-1]*0.945:
                    if_weak =  True
                if price_close[length_prices-i]<price_close[length_prices-i-1]*0.97:
                    weak_count += 1
                    if weak_count>1:
                        if_weak =  True
                if price_close[length_prices-i]<price_close[length_prices-i-1]:
                    minus_count += 1
                    if minus_count>2:
                        if_weak =  True
            #超过3日处于10日均线下方，判为弱势
            ma10 = price_close.rolling(window=10,center=False,min_periods=10).mean()
            ma10_tp = [x>y for (x,y) in zip(price_close,ma10)]
            length_ma10_tp = len(ma10_tp)
            weak6_count = 0
            for i in range(1,6):
                if not ma10_tp[length_ma10_tp-i]: 
                    weak6_count += 1
                    if weak6_count>2:
                        if_weak = True
            print('股票是否弱势',stock,if_weak)
            #去掉macd下行
            if false_count>=20: #确认由下向上趋势，均值突破1-3日
                if ma50_tp[length_ma50_tp-1] or (ma50_tp[length_ma50_tp-1] and ma50_tp[length_ma50_tp-2]) or (ma50_tp[length_ma50_tp-1] and ma50_tp[length_ma50_tp-2] and ma50_tp[length_ma50_tp-3]):
                    
                    #print("--------------股票%s 6日与108日移动均值比较结果------------ " % stock)
                    #print(ema_result3[length_ema_result3-10:])
                    #底部突破
                    if ema_result1[length_ema_result1-1] and not ema_result2[length_ema_result2-1] and not ema_result3[length_ema_result3-1]:
                        ema_true_count = 0
                        for result in ema_result1[length_ema_result1-14:]:
                            if result:
                                ema_true_count += 1 
                        ma_true_count = 0
                        for mt in ma50_tp[length_ma50_tp-10:]:
                            if mt:
                                ma_true_count += 1
                        if ema_true_count>1 and ema_true_count<6 and ma_true_count>1 and ma_true_count<6:  #突破小于一定时间                             
                            if not if_weak and if_red_ok: #
                                stocks_selected_low.append(stock)
                            else:
                                print("股票太弱",stock)
                        else:
                            print("股票还未突破",stock,'ema6-18:',ema_result1[length_ema_result1-14:],'ma50_tp',ma50_tp[length_ma50_tp-10:])
                                
                    
                else:
                    print('股票未满足50日突破条件',stock,',ma50_tp：',ma50_tp[length_ma50_tp-10:])  
            else:
                print('股票未满足底部滞留天数20/30',stock,',天数：',false_count) 
            
            #强势判定
            if if_red_ok:
                ema6_18_true_count = 0
                for result in ema_result1[length_ema_result1-10:]:
                    if result:
                        ema6_18_true_count += 1
                ema6_108_true_count = 0
                for result in ema_result3[length_ema_result3-5:]:
                    if result:
                        ema6_108_true_count += 1
                macd = get_macd_data(price_close)
                length_macd = len(macd)
                if_up = False
                if (macd[length_macd-1]>macd[length_macd-2] and macd[length_macd-2]>macd[length_macd-3] and macd[length_macd-3]>macd[length_macd-4]) \
                    or (macd[length_macd-1]>0 and macd[length_macd-2]<0 and  macd[length_macd-3]>0)  \
                    or (macd[length_macd-1]>1 and macd[length_macd-2]>1 and  macd[length_macd-3]>1):
                        if_up = True
                if if_up and ema_result1[length_ema_result1-1] and not if_weak and (ema6_18_true_count>6 or  (ema_result3[length_ema_result3-1] and ema6_108_true_count>0 and ema6_108_true_count<4)):
                    print('股票满足强势条件ema6>18:6,ema6>108:3',stock,',ema6-18：',ema_result1[length_ema_result1-10:],'ema6-108',ema_result3[length_ema_result3-6:])  
                    stocks_selected_median.append(stock)                    
                else:
                    print('股票未满足强势条件ema6>18:6,ema6>108:3',stock,',ema6-18：',ema_result1[length_ema_result1-10:],'ema6-108',ema_result3[length_ema_result3-6:])  
            else:
                print('股票未满足红盘条件6/8|8/10|9/12:',stock,',红盘：',red_count,red) 
            #超强势算法            
            ema6_18_true_count = 0
            for result in ema_result1[length_ema_result1-20:]:
                if result:
                    ema6_18_true_count += 1
            ema18_108_true_count = 0
            for result in ema_result2[length_ema_result2-20:]:
                if result:
                    ema18_108_true_count += 1
            if ema_result1[length_ema_result1-1] and ema6_18_true_count>12  and ema18_108_true_count>12 :
                print('股票满足超级强势条件ema6>18:30/50,ema18>108:30/50：',stock,'ema6>18：',ema6_18_true_count,'ema18>108：',ema18_108_true_count)
                stocks_selected_high.append(stock)
            else:                
                print('股票未满足超级强势条件ema6>18:30/50,ema18>108:30/50：',stock,'ema6>18：',ema6_18_true_count,'ema18>108：',ema18_108_true_count)
            
            print('已选择股票，底部突破：',stocks_selected_low,'强势：',stocks_selected_median,'超强势：',stocks_selected_high)
    except Exception as e:
        print(e)
    finally:
        print("选择的底部突破股票：",stocks_selected_low)
        print("选择的强势股票：",stocks_selected_median)
        print("选择的超强势股票：",stocks_selected_high)
