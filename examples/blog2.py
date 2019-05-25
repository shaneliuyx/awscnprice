from select_ri import *
import pandas as pd
#os.environ['EXCLUDE_EC2_TYPE'] = "5"
input = pd.read_excel("blog2_input_simple.xlsx")
output = pd.DataFrame()

ri = RI()
for index, row in input.iterrows():
    row = row.reset_index(drop=True)
    result = ri.select_ec2_by_config(input_row=row)
    output = output.append(result, ignore_index=True, sort=False)
output = pd.concat([input, output], axis=1, join_axes=[input.index])
print (output)
output.to_excel('blog2_output_simple.xlsx', index=False)
