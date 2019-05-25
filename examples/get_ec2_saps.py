import pandas as pd
saps_table = pd.read_html('https://aws.amazon.com/cn/sap/instance-types/')
new_table = saps_table[0]
old_table = saps_table[1]

new = new_table[['Instance Type', 'vCPU', 'Mem (GiB)', 'SAPS']]
old = old_table[['Instance Type', 'vCPU', 'Mem (GiB)', 'SAPS']]
ec2_saps = pd.concat([new, old])
ec2_saps.replace({'\*': ''}, regex=True, inplace=True)
ec2_saps['vCPU'] = pd.to_numeric(
    ec2_saps['vCPU'], downcast='integer', errors='coerce')
ec2_saps['Mem (GiB)'] = pd.to_numeric(
    ec2_saps['Mem (GiB)'], downcast='float', errors='coerce')
ec2_saps['SAPS'] = pd.to_numeric(
    ec2_saps['SAPS'], downcast='float', errors='coerce')
ec2_saps.to_excel('ec2_saps.xlsx', index=False)
