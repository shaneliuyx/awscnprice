#!/usr/bin/env python
# see: https://aws.amazon.com/blogs/aws/new-aws-price-list-api/

import requests
import pandas as pd
import os
import json
import awscnpricing
os.environ['AWSPRICING_USE_CACHE'] = "1"
os.environ['AWSPRICING_CACHE_PATH'] = "/tmp/awscnpricing"
os.environ['AWSPRICING_CACHE_MINUTES'] = "1440"
output = 'cn_ec2_standard_price.xlsx'

offering_class = 'standard'

ec2_offer_code = 'AmazonEC2'
ec2_offer = awscnpricing.offer(ec2_offer_code)
ec2_file_path = os.getenv('AWSPRICING_CACHE_PATH')
ec2_file_name = 'offer_{}_current'.format(ec2_offer_code)
ec2_cache_file = os.path.join(ec2_file_path, ec2_file_name)
if os.path.exists(ec2_cache_file):
    with open(ec2_cache_file, 'r') as load_f:
        ec2offer = json.load(load_f)
else:
    offers = requests.get(
        'https://pricing.cn-north-1.amazonaws.com.cn/offers/v1.0/cn/index.json'
    )
    ec2_offer_path = offers.json()['offers']['AmazonEC2']['currentVersionUrl']
    ec2offer = requests.get(
        'https://pricing.cn-north-1.amazonaws.com.cn%s' % ec2_offer_path
    ).json()


on_demand_price = []
r_type = []
r_vcpu = []
r_location = []
r_memory = []
r_operatingSystem = []
r_tenancy = []
r_capacity_status = []
r_preinstalled_software = []
r_license_model = []
PerchaseOption = ['All Upfront', 'Partial Upfront', 'No Upfront']
LeaseContractLength = ['1yr', '3yr']
reserve_price = {}
reserve_price['1yr_all'] = []
reserve_price['1yr_no'] = []
reserve_price['1yr_partial'] = []
reserve_price['3yr_all'] = []
reserve_price['3yr_no'] = []
reserve_price['3yr_partial'] = []
for sku, data in ec2offer['products'].items():
    if data['productFamily'] != 'Compute Instance':
        # skip anything that's not an EC2 Instance
        continue
    ec2_type = data['attributes']['instanceType']

    ec2_os = data['attributes']['operatingSystem']

    site = data['attributes']['location']
    ec2_region = ""
    if site == "China (Beijing)":
        ec2_region = "cn-north-1"
    if site == "China (Ningxia)":
        ec2_region = "cn-northwest-1"

    for yr in LeaseContractLength:
        for p_option in PerchaseOption:
            try:
                a_price = ec2_offer.reserved_upfront(
                    ec2_type,
                    operating_system=ec2_os,
                    lease_contract_length=yr,
                    tenancy=data['attributes']['tenancy'],
                    license_model=data['attributes']['licenseModel'],
                    preinstalled_software=data['attributes']['preInstalledSw'],
                    offering_class=offering_class,
                    purchase_option=p_option,
                    region=ec2_region,
                    capacity_status=data['attributes']['capacitystatus']
                )
            except:
                a_price = "0"
            try:
                o_price = ec2_offer.ondemand_hourly(
                    ec2_type,
                    operating_system=ec2_os,
                    tenancy=data['attributes']['tenancy'],
                    preinstalled_software=data['attributes']['preInstalledSw'],
                    license_model=data['attributes']['licenseModel'],
                    region=ec2_region,
                    capacity_status=data['attributes']['capacitystatus']
                )
            except:
                o_price = "0"
            on_demand_price.append(o_price)
            r_type.append(ec2_type)
            r_vcpu.append(data['attributes']['vcpu'])
            r_location.append(site)
            r_memory.append(data['attributes']['memory'].replace(
                " GiB", "").replace(",", ""))
            r_operatingSystem.append(ec2_os)
            r_tenancy.append(data['attributes']['tenancy'])
            r_capacity_status.append(data['attributes']['capacitystatus'])
            r_preinstalled_software.append(
                data['attributes']['preInstalledSw'])
            r_license_model.append(data['attributes']['licenseModel'])

            if p_option == 'All Upfront':
                if yr == '1yr':
                    reserve_price['1yr_all'].append(a_price)
                    reserve_price['1yr_no'].append('0')
                    reserve_price['1yr_partial'].append('0')
                    reserve_price['3yr_all'].append('0')
                    reserve_price['3yr_no'].append('0')
                    reserve_price['3yr_partial'].append('0')
                else:
                    reserve_price['3yr_all'].append(a_price)
                    reserve_price['1yr_all'].append('0')
                    reserve_price['1yr_no'].append('0')
                    reserve_price['1yr_partial'].append('0')
                    reserve_price['3yr_no'].append('0')
                    reserve_price['3yr_partial'].append('0')
            elif p_option == 'No Upfront':
                if yr == '1yr':
                    reserve_price['1yr_no'].append(a_price)
                    reserve_price['1yr_all'].append('0')
                    reserve_price['1yr_partial'].append('0')
                    reserve_price['3yr_no'].append('0')
                    reserve_price['3yr_partial'].append('0')
                    reserve_price['3yr_all'].append('0')
                else:
                    reserve_price['3yr_no'].append(a_price)
                    reserve_price['1yr_no'].append('0')
                    reserve_price['1yr_all'].append('0')
                    reserve_price['1yr_partial'].append('0')
                    reserve_price['3yr_partial'].append('0')
                    reserve_price['3yr_all'].append('0')
            else:
                if yr == '1yr':
                    reserve_price['1yr_partial'].append(a_price)
                    reserve_price['3yr_no'].append('0')
                    reserve_price['1yr_no'].append('0')
                    reserve_price['1yr_all'].append('0')
                    reserve_price['3yr_partial'].append('0')
                    reserve_price['3yr_all'].append('0')

                else:
                    reserve_price['3yr_partial'].append(a_price)
                    reserve_price['1yr_partial'].append('0')
                    reserve_price['3yr_no'].append('0')
                    reserve_price['1yr_no'].append('0')
                    reserve_price['1yr_all'].append('0')
                    reserve_price['3yr_all'].append('0')

df = pd.DataFrame({'type': r_type, 'vcpu': r_vcpu, 'memory': r_memory, 'location': r_location, "tenancy": r_tenancy, "os": r_operatingSystem,
                   "all_upfront_price_1yr": reserve_price['1yr_all'], "partial_upfront_price_1yr": reserve_price['1yr_partial'], "no_upfront_price_1yr": reserve_price['1yr_no'], "all_upfront_price_3yr": reserve_price['3yr_all'], "partial_upfront_price_3yr": reserve_price['3yr_partial'], "no_upfront_price_3yr": reserve_price['3yr_no'], "on_demand_price": on_demand_price, 'capacity_status': r_capacity_status, 'preInstalledSw': r_preinstalled_software, 'license_model': r_license_model})
df[['vcpu', 'memory', 'all_upfront_price_1yr', 'partial_upfront_price_1yr', 'no_upfront_price_1yr', 'all_upfront_price_3yr', 'partial_upfront_price_3yr', 'no_upfront_price_3yr', 'on_demand_price']] = df[[
    'vcpu', 'memory', 'all_upfront_price_1yr', 'partial_upfront_price_1yr', 'no_upfront_price_1yr', 'all_upfront_price_3yr', 'partial_upfront_price_3yr', 'no_upfront_price_3yr', 'on_demand_price']].astype('float')
df.drop_duplicates(subset=['type', 'vcpu', 'memory', 'location', 'tenancy', 'os', 'all_upfront_price_1yr', 'partial_upfront_price_1yr', 'no_upfront_price_1yr', 'all_upfront_price_3yr',
                           'partial_upfront_price_3yr', 'no_upfront_price_3yr', 'on_demand_price', 'capacity_status', 'preInstalledSw', 'license_model'], keep='first', inplace=True)
df = df[(df.all_upfront_price_1yr > 0) | (df.partial_upfront_price_1yr > 0) | (df.no_upfront_price_1yr > 0) | (
    df.all_upfront_price_3yr > 0) | (df.partial_upfront_price_3yr > 0) | (df.no_upfront_price_3yr > 0) | (df.on_demand_price > 0)]
df = df.reset_index(drop=True)
print (df)
df.to_excel(output, sheet_name='price')
