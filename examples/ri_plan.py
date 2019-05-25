import pandas as pd
from datetime import *
from datetime import date
from datetime import datetime

table = pd.read_excel("blog5_output.xlsx")
start_day = min(table['ri_expired_date']).date()
end_day = max(table['ri_expired_date']).date()
duration = (end_day - start_day).days
total_item = table.shape[0]
cost = []
for x in range(0, duration + 1):
    sub_total = 0
    for i in range(0, total_item):
        current_item_date = (table.loc[[i]].ri_expired_date)[i].date()
        # old price duration
        op_day = ((current_item_date - start_day).days) - x
        # on demand price duration
        od_day = x - ((current_item_date - start_day).days)
        # new price duration
        np_day = (duration - x)
        if op_day < 0:
            op_day = 0
        if od_day < 0:
            od_day = 0
        sub_total += ((table.loc[[i]].source_price)[i] / 365 * op_day + (table.loc[[i]].target_price)[
                      i] / 365 * np_day + (table.loc[[i]].source_ondemand) * od_day * 24)[i]
    cost.append(sub_total)
optimize_cost = min(cost)

print("{}   {}".format('    Date', '    Cost'))
for i in range(0, len(cost)):
    if cost[i] == optimize_cost:
        recommand_date = start_day + timedelta(days=i)
    current_date = start_day + timedelta(days=i)
    current_date = datetime.combine(current_date, datetime.min.time())
    print("{}   {:.2f}".format(current_date.strftime('%Y-%m-%d'), cost[i]))
print ('\nRecommended date to buy RI is {}'.format(recommand_date))
