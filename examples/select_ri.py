from pandasql import *
import pandas as pd
import os


class RI:

    def __init__(self):
        try:
            exclude_list = os.getenv('EXCLUDE_EC2_TYPE').split(",")
        except:
            exclude_list = []
        self.exclude = ""
        if exclude_list != []:
            for exclude_type in exclude_list:
                self.exclude = self.exclude + f'(type NOT LIKE \'%{exclude_type}%\') and '
        price_file_name = "cn_ec2_standard_price.xlsx"
        price_file_path = "."
        price_file = os.path.join(price_file_path, price_file_name)
        if os.path.exists(price_file):
            self.df = pd.read_excel(price_file)
        else:
            print ("There is no file (cn_ec2_standard_price.xlsx) in current directory")
            exit

    def select_ec2_by_type(self, input_row,
                           location='China (Beijing)',
                           ec2_os='Linux',
                           tenancy='Shared',
                           preInstalledSw='',
                           licenseModel='No License required'):
        price_table = self.df

        try:
            ec2_os = input_row['source_os'][0]
            if pd.isnull(input_row['source_os'])[0]:
                ec2_os = 'Linux'
        except:
            ec2_os = 'Linux'
        try:
            preInstalledSw = input_row['preInstalledSw'][0]
            if pd.isnull(input_row['preInstalledSw'])[0]:
                preInstalledSw = ''
        except:
            preInstalledSw = ''

        if preInstalledSw != '':
            preInstalledSw_option = f'(preInstalledSw == {preInstalledSw})'
        else:
            preInstalledSw_option = '(preInstalledSw isNull)'

        q = "select DISTINCT vcpu, memory, all_upfront_price_1yr from price_table where (type == '{}') and (tenancy == '{}') and (location == '{}') and (os == '{}') and (all_upfront_price_1yr > 0) and {} and  (license_model=='{}')".format(
            input_row['type'][0], tenancy, location, ec2_os, preInstalledSw_option, licenseModel)

        try:
            base = sqldf(q, locals())
        except:
            base = pd.DataFrame()
            base.columns = ['vcpu', 'memory', 'all_upfront_price_1yr']

        vcpu_col = [base['vcpu'][0]]
        input_row['vcpu'] = vcpu_col
        input_row['memory'] = [base['memory'][0]]

        t_vcpu = self.caculate_cpu(input_row)
        t_memory = self.caculate_mem(input_row)

        q = "SELECT type,vcpu, memory,min(all_upfront_price_1yr) FROM price_table  WHERE (vcpu >= {}) and (memory>={}) and (tenancy == '{}') and (location == '{}') and (os == '{}') and (all_upfront_price_1yr <= {}) and (all_upfront_price_1yr > 0) and (license_model == '{}') and {} {};".format(
            float(t_vcpu), float(t_memory), tenancy, location, ec2_os, float(base.all_upfront_price_1yr), licenseModel, self.exclude, preInstalledSw_option)

        try:
            target = sqldf(q, locals())
        except:
            target = pd.DataFrame()
            target.columns = ['type', 'vcpu',
                              'memory', 'min(all_upfront_price_1yr)']

        if pd.isnull(target['type'])[0]:
            target = self.select_ec2_by_config(input_row)

        target['s_vcpu'] = base['vcpu']
        target['s_mem'] = base['memory']
        target['s_all_upfront_price'] = base['all_upfront_price_1yr']

        target = target.rename(index=str, columns={"type": "target_type", "vcpu": "target_vcpu", "memory": "target_memory",
                                                   "min(all_upfront_price_1yr)": "target_price", "s_vcpu": "source_vcpu", "s_mem": "source_memory", "s_all_upfront_price": "source_price"})

        target['savings'] = target['source_price'] - target['target_price']
        target['source_ondemand'] = self.get_ondemand_price(
            input_row['type'][0], ec2_os, tenancy, location, licenseModel, preInstalledSw, price_table)

        target['target_ondemand'] = self.get_ondemand_price(
            target.target_type[0], ec2_os, tenancy, location, licenseModel, preInstalledSw, price_table)
        return target

    def select_ec2_by_config(self, input_row,
                             location='China (Beijing)',
                             ec2_os='Linux',
                             tenancy='Shared',
                             preInstalledSw='NA',
                             licenseModel='No License required'):
        price_table = self.df
        try:
            ec2_os = input_row['source_os'][0]
            if pd.isnull(input_row['source_os'])[0]:
                ec2_os = 'Linux'
        except:
            ec2_os = 'Linux'
        try:
            preInstalledSw = input_row['preInstalledSw'][0]
            if pd.isnull(input_row['preInstalledSw'])[0]:
                preInstalledSw = ''
        except:
            preInstalledSw = ''

        t_vcpu = self.caculate_cpu(input_row)
        t_memory = self.caculate_mem(input_row)

        if preInstalledSw != '':
            preInstalledSw_option = f'(preInstalledSw == {preInstalledSw})'
        else:
            preInstalledSw_option = '(preInstalledSw isNull)'

        q = "SELECT type,vcpu, memory,min(all_upfront_price_1yr) FROM price_table  WHERE (vcpu >= {}) and (memory>={}) and (tenancy == '{}') and (location == '{}') and (os == '{}') and (all_upfront_price_1yr > 0) and {}{} and (license_model=='{}');".format(
            t_vcpu, t_memory, tenancy, location, ec2_os, self.exclude, preInstalledSw_option, licenseModel)

        try:
            target = sqldf(q, locals())
        except:
            target = pd.DataFrme()
            target.columns = ['type', 'vcpu',
                              'memory', 'min(all_upfront_price_1yr)']

        target.columns = ['target_type', 'target_vcpu',
                          'target_memory', 'target_price']

        target['target_ondemand'] = self.get_ondemand_price(
            target.target_type[0], ec2_os, tenancy, location, licenseModel, preInstalledSw, price_table)

        return target

    def caculate_cpu(self, df):
        try:
            cpu_base = df['vcpu'][0]
        except:
            return 0
        try:
            cpu_rate = df['cpu_rate'][0]
            if pd.isnull(df['cpu_rate'])[0]:
                cpu_rate = 100
        except:
            cpu_rate = 100
        try:
            prefer = df['prefer'][0]
            if pd.isnull(df['prefer'])[0]:
                prefer = 'c'
        except:
            prefer = 'c'
        try:
            target_cpu_rate = df['target_cpu_rate'][0]
            if pd.isnull(df['target_cpu_rate'])[0]:
                target_cpu_rate = 0.9
        except:
            target_cpu_rate = 0.9

        if (prefer.lower() == 'c') | (prefer.lower() == 'c+m') | (prefer.lower() == 'm+c'):
            try:
                return float(cpu_base) * float(cpu_rate) / 100 / target_cpu_rate
            except TypeError:
                return float(cpu_base)
        else:
            return 0

    def caculate_mem(self, df):
        try:
            mem_base = df['memory'][0]
        except:
            return 0
        try:
            mem_rate = df['memory_rate'][0]
            if pd.isnull(df['memory_rate'])[0]:
                mem_rate = 100
        except:
            mem_rate = 100
        try:
            prefer = df['prefer'][0]
            if pd.isnull(df['prefer'])[0]:
                prefer = 'm'
        except:
            prefer = 'm'
        try:
            target_mem_rate = df['target_mem_rate'][0]
            if pd.isnull(df['target_mem_rate'])[0]:
                target_mem_rate = 0.90
        except:
            target_mem_rate = 0.90
        if mem_rate == 100:
            target_mem_rate = 1
        if (prefer.lower() == 'm') | (prefer.lower() == 'c+m') | (prefer.lower() == 'm+c'):
            try:
                return float(mem_base) * float(mem_rate) / 100 / target_mem_rate
            except TypeError:
                return float(mem_base)
        else:
            return 0

    def get_ondemand_price(self, instance_type, operating_system, tenancy, location, licenseModel, preInstalledSw, price):

        if preInstalledSw != '':
            preInstalledSw_option = f'(preInstalledSw == {preInstalledSw})'
        else:
            preInstalledSw_option = '(preInstalledSw isNull)'

        q = "select DISTINCT on_demand_price from price where (type == '{}') and (tenancy == '{}') and (location == '{}') and (os == '{}') and (on_demand_price > 0) and {} and (license_model=='{}');".format(
            instance_type, tenancy, location, operating_system, preInstalledSw_option, licenseModel)

        try:
            o_price = sqldf(q, locals())
        except:
            o_price = pd.DataFrame()
            o_price.columns = ['on_demand_price']

        return (o_price['on_demand_price'].tolist())
