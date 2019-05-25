import pandas as pd

source = "blog3_output.xlsx"
sheet = 0
#target = "result.xlsx"
target = pd.ExcelWriter('result.xlsx')
for i in range(1, 6):
    sheet = i
    ex1 = pd.read_excel(source)
    ex2 = pd.read_excel("ec2_saps.xlsx")
    merge = ex1.merge(ex2, left_on="type",
                      right_on="Instance Type", how='left')
    merge.drop(['Instance Type', 'vCPU', 'Mem (GiB)'], axis=1, inplace=True)
    merge.rename(columns={'SAPS': 'source_saps'}, inplace=True)
    merge = merge.merge(ex2, left_on="target_type",
                        right_on="Instance Type", how='left')
    merge.drop(['Instance Type', 'vCPU', 'Mem (GiB)'], axis=1, inplace=True)
    merge.rename(columns={'SAPS': 'target_saps'}, inplace=True)

    merge.to_excel(target, sheet_name=str(sheet), index=False)
target.save()
