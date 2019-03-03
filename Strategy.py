# -*- coding: utf-8 -*-
#  Created on Fri Oct 27
import numpy as np
import pandas as pd
#  moving average time period
ma_period = 5
long_ma_period = 60


def handle_bar(counter,  # a counter for number of minute bars that have already been tested
               time,  # current time in string format such as "2018-07-30 00:30:00"
               data,  # data for current minute bar (in format 2)
               init_cash,  # your initial cash, a constant
               transaction,  # transaction ratio, a constant
               cash_balance,  # your cash balance at current minute
               crypto_balance,  # your crpyto currency balance at current minute
               total_balance,  # your total balance at current minute
               position_current,  # your position for 4 crypto currencies at this minute
               memory  # a class, containing the information you saved so far
               ):
    '''Our strategy:
        Our strategy divided into four parts: 
        1. Find suitable timestamp to add four cryptocurrencies.
            For a type of crypto, think about all "Down" timestamp: a.k.a closeprice is smaller than openprice.
            In these Down timestamp, let's assume the outcome of "openprice minus closeprice" obbeys the normal distrbution.
            Hence, it's less likely happened that the gap between open and close price is larger than mean plus 3 times std. 
            ("Three Sigma")
            If this situation really happens, the average price will have a significant down performance.
            We can update mean and std every mimute and compare with curent gap, helping do adding positions strategy.

            If: 
            1). current timestamp is a "Down" timestamp, also the gap between openprice and closeprice is larger than "Three Sigma",
            2). what's more, the closeprice is smaller than short-term Simplfied Moving Average(5 mimutes),
                which means a relative low price in a short time period, 
            3). and the closeprice is smaller than long-term Exponential Moving Average(60 mimutes), which means a down trend,
            4). our cash is available to add this positons including transaction costs, 
                even if next minute the average_price increase 0.02 time.
            we will add positions of the actuall crypto (The change is now 0.1 unit for BTC and 1 unit for other three cryptos.),
            and change the "changing position" signal of this crypto to 1.
        2. Check and record what we did in last minute.
            At the start of every mimute, check four cryptos' "changing position" signial equals to 1 or 0.
            If it equals 1, we maked a decision to change our positions in last minute. (increase or decrease)
            Update our record sheet in memory.holding_record.
                Sample DataFrame:
                    timecounter        | cryptoindex | change           |  unitprice     | hopereturn  | passtime
                    ---------------------------------------------------------------------------------------------
                    (changing counter) | (0,1,2,3)   | (positive_value) | (buying price) | (1.002)     | (how many mimutes passed) 
    
            If we added position, we will add a row into the DataFrame, 
            else we will refresh our oldest record(decrease the value of 'change').
            Each time we will drop records whose 'change' equals to zero.
            After update the dataframe, change the "changing position" signal to 0.

        3. Update our hopereturn ratio in memory.holding_record.
            Since it's a short term investment, we will change our hopereturn as time going by.
            For every row in the record DataFrame, if in current mimute the long-EMA is larger than close price of the actual crypto,
            'passtime' add 1.
            Then update 'hopereturn' column as 1.002 - 'passtime' * 0.001 / 1440 (decrease 0.001 for 12 hours.)

        4. Check it's suitable time to release our position.
            If current price satisifies our hope return, even the price decrease 0.01 time, release the position.
            For detail calculations, please check the comment in that block, an example is provided.
            Change the 'changing position signal' of the actual crypto to 1.
            Add our availablecash at the same time.

        The order of these four parts in every minute is: 2-3-4-1, namely:
            -- check last minute change 
            -- update holding record dataframe 
            -- update hope return ratio 
            -- check whether add position or not.
        Attention: decreasing positions is superior to increasing postions.
    '''
    # 1. initialization
    if counter == 0:
        memory.closeprice = data[:, 0]  # type: numpy.darray
        memory.movingaverage = np.zeros(shape=(4,), dtype='float64')
        memory.long_movingaverage = np.zeros(shape=(4, ), dtype='float64')
        # calculate: Open Price - Close Price
        candlestick_length = data[:, 3] - data[:, 0]
        memory.negativecounter = np.zeros(shape=(4,), dtype='int')
        memory.clength_mean = [max(i, 0) for i in candlestick_length]
        memory.cl_mean_last = memory.clength_mean
        memory.clength_sigma = np.zeros(shape=(4,), dtype='float64')
        memory.cl_sigma_last = memory.clength_sigma
        #  if we dicide to changing our position, change the change_statue at this mimute
        #  and every mimute checking the change_statue to record what we did last mimute
        memory.holding_record = pd.DataFrame(
            columns=['timecounter', 'cryptoindex', 'change', 'unitprice', 'hopereturn', 'passtime'])
        memory.position_old = np.zeros(shape=(4,))
        memory.change_statue = np.zeros(shape=(4,), dtype='int')
    else:
        candlestick_length = data[:, 3] - data[:, 0]
        if counter < (long_ma_period - 1):
            pass
        else:
            average_price = np.mean(data[:, :4], axis=1)
            # 2. Check last mimute our position was changed or not.
            for index in range(4):
                position_change = 0.0
                if memory.change_statue[index] != 1:
                    continue
                position_change = position_current[index] - \
                    memory.position_old[index]
                if position_change == 0.0:
                    continue
                for i, rowi in memory.holding_record.iterrows():
                    if rowi['cryptoindex'] != index:
                        continue
                    record = rowi['change']
                    if record * position_change > 0.0:
                        continue
                    if record * position_change < 0.0:
                        new_record = 0.0
                        if record > 0.0:
                            new_record = max(position_change + record, 0.0)
                            position_change = min(
                                position_change + record, 0.0)
                        else:
                            new_record = min(position_change + record, 0.0)
                            position_change = max(
                                position_change + record, 0.0)
                        memory.holding_record.loc[i, 'change'] = new_record
                if position_change != 0.0:
                    memory.holding_record.loc[len(memory.holding_record)] = [counter, int(
                        index), position_change, average_price[index], 1.002, 0]
                memory.change_statue[index] = 0

            memory.holding_record = memory.holding_record.drop(
                memory.holding_record[memory.holding_record['change'] == 0.0].index)
            memory.holding_record = memory.holding_record.reset_index(
                drop=True)

            # availablecash is used to make sure our cash won't be lower than limit_cash.
            availablecash = cash_balance - 10000

            # 3. update our hopereturn (reduce 0.001 per day)
            for i in range(4):
                if memory.long_movingaverage[i] < data.item((i, 0)):
                    #  if it's a up tendency now, we won't decrease our hope return ratio.
                    pass
                else:
                    #  decrease holp return only when it passed half day.
                    memory.holding_record.loc[memory.holding_record.cryptoindex ==
                                              i, 'passtime'] += 1
                    new_hopereturn = 1.002 - \
                        0.001 * memory.holding_record.loc[:, 'passtime'] / 1440
                    memory.holding_record['hopereturn'] = new_hopereturn

            # 4. check memory.holding_record if current price satisfies our hopereturn and change our position
            for i in range(4):
                record = memory.holding_record[memory.holding_record['cryptoindex'] == i]
                if len(record) == 0:
                    continue
                '''
                Example: 
                Couter == 500, add position 0.5 unit at average price $6500, hopereturn is 1.0020.
                With the extra transaction cost ratio 0.0005, the actual buying price is 6500 * 1.0005 = 6503.25.
                When counter == 600, the new hopereturn is 1.0020 - 0.001*(600-500)/1440 = 1.0019
                With the extra transaction cost ration, the hope return price should be 6503.25*1.0019/(1-0.0005)=6507.7394
                '''
                current_return = record.loc[:, 'hopereturn'] * \
                    record.loc[:, 'unitprice'] * \
                    (1+transaction) / (1-transaction)
                change_oldposition = 0
                for j, rowj in record.iterrows():
                    # even if next minute the average_price decrease 0.01 time.
                    if average_price[i] * 0.99 >= current_return[j] \
                            and record.loc[j].timecounter < counter:
                        if change_oldposition == 0:
                            memory.position_old[i] = position_current[i]
                            change_oldposition = 1
                        position_current[i] -= record.loc[j].change
                        availablecash += average_price[i] * 0.99 * \
                            record.loc[j].change * (1 - transaction)
                        memory.change_statue[i] = 1


            # 5. decide whether to add our position or not
            #  calculate movering average for cuttent mimute
            memory.movingaverage = np.mean(memory.closeprice, axis=0)
            #  delete the (counter - 4) mimute closeprice and add a new close price
            memory.closeprice = np.delete(memory.closeprice, 0, 0)
            #  buy less BTC
            adding_position = [1, 0.1, 1, 1]
            for index in range(4):
                if memory.movingaverage[index] > data.item((index, 3)) \
                        and data.item((index, 3)) > data.item((index, 0)) \
                        and candlestick_length[index] > memory.clength_mean[index]+3*memory.clength_sigma[index] \
                        and data.item((index, 0)) < memory.long_movingaverage[index] \
                        and availablecash > average_price[index]*1.02*adding_position[index]*(1+transaction)\
                        and memory.change_statue[index] == 0:
                        #  we will buy adding_position[index] currency[index]
                        #  even if next mimute the average price of currency[index] will increase 0.02 time
                    memory.position_old[index] = position_current[index]
                    position_current[index] += adding_position[index]
                    #  set the position changing flag
                    memory.change_statue[index] = 1
                    availablecash -= average_price[index] * \
                        1.02*adding_position[index]*(1+transaction)

        # refleshment variables
        memory.closeprice = np.vstack((memory.closeprice, data[:, 0]))
        memory.cl_mean_last = memory.clength_mean
        memory.cl_sigma_last = memory.clength_sigma
        for index, value in enumerate(memory.cl_mean_last):
            if candlestick_length[index] > 0:
                memory.clength_mean[index] = (memory.negativecounter[index] * value +
                                              candlestick_length[index]) / (memory.negativecounter[index]+1)
                memory.clength_sigma[index] = (((value ** 2 + memory.cl_mean_last[index] ** 2)
                                                * memory.negativecounter[index] + candlestick_length[index] ** 2) /
                                               (memory.negativecounter[index]+1) - memory.clength_mean[index]**2)**0.5
                memory.negativecounter[index] += 1
        memory.long_movingaverage = (
            memory.long_movingaverage * counter + data[:, 0]) / (counter + 1)
    position_new = position_current
    # End of strategy
    return position_new, memory
