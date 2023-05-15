from pprint import pformat
from netmiko import NetMikoTimeoutException
import re
from decimal import Decimal
from collections import OrderedDict
from datetime import datetime
ts=datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
self.configuration['excel_file_name']=f'dom_statistics_{ts}'

ipn_data={}
self.hostname_cache={}

for node in cisco.aci.query('/api/node/class/fabricNode.json?order-by=fabricNode.modTs|desc')['imdata']:
    self.hostname_cache[node['fabricNode']['attributes']['id']]=node['fabricNode']['attributes']['name']
    

def get_link_budget_status_text(data, item_type, severity='warn', percent_high = 90, percent_low = 10):
    
    item_high_name = '{0}_{1}_high'.format(item_type,severity)
    item_low_name = '{0}_{1}_low'.format(item_type,severity)
    item_value_name = '{0}_value'.format(item_type)
    status='n/a'
    high=0

    if data[item_low_name] < 0 and data[item_high_name] > 0: 
        high = (data[item_low_name] * -1) + data[item_high_name]
        low = 0
        value = data[item_value_name] + data[item_low_name] * -1
    else:
        low = data[item_low_name]
        high = data[item_high_name]
        value = data[item_value_name] - low
    
    budget = high - low


    if budget == Decimal(0):
        return 'link not connected'
 

    percent = (100/budget * value)

    # log.info('{2} {1} budget: {0} val: {3} percent: {4}'.format(budget, item_type, data['interface'],value, percent))
        
    if percent <= percent_high and percent >= percent_low:
        status = 'optimal'
    if percent < percent_low and percent > 0:
        status = 'pre weak warning(<{0}% to warning_low) but ok for production environment'.format(percent_low)
    if percent > percent_high:
        status = 'pre strong warning (<{0}% to warning_high) but ok for production environment'.format(100 - percent_high)
    if percent <= 0:
        status = 'too weak, please check link'
    if percent > 100:
        status = 'too strong, please check link'
    return status



def try_decimal(val):
    try:
        val=Decimal(val)
    except:
        pass
    return val

def transform_aci_to_fsm2text_format(self,aci_obj):
    
    current_lane = 1

    interface_rgx = re.compile(r'.*\[(eth.+)\].*')
    switch_id_rgx = re.compile(r'.*node-(\d+).*')
    
    interface = interface_rgx.match(aci_obj['ethpmDOMStats']['attributes']['dn']).group(1).replace('eth','Ethernet')
    switch_id = switch_id_rgx.match(aci_obj['ethpmDOMStats']['attributes']['dn']).group(1)
    hostname = self.hostname_cache[switch_id]

    retval = {}
    for child in aci_obj['ethpmDOMStats']['children']:
        obj_type = list(child.keys())[0]
        lanes = int(child[obj_type]['attributes']['lanes'])

        for lane in range(1, lanes + 1):
            if lane > 1:
                lane_postfix = str(lane)
            else:
                lane_postfix = ''
            if lane not in retval.keys():
                retval[lane]={}
            retval[lane]['lane'] = lane
            retval[lane]['interface'] = interface
            retval[lane]['hostname'] = hostname
            

            if obj_type == 'ethpmDOMRxPwrStats':
                retval[lane]['rx_alarm_high'] = child[obj_type]['attributes']['hiAlarm{0}'.format(lane_postfix)]
                retval[lane]['rx_alarm_low'] = child[obj_type]['attributes']['loAlarm{0}'.format(lane_postfix)]
                retval[lane]['rx_value'] = child[obj_type]['attributes']['value{0}'.format(lane_postfix)]
                retval[lane]['rx_warn_high'] = child[obj_type]['attributes']['hiWarn{0}'.format(lane_postfix)]
                retval[lane]['rx_warn_low'] = child[obj_type]['attributes']['loWarn{0}'.format(lane_postfix)]
            elif obj_type == 'ethpmDOMTxPwrStats':
                retval[lane]['tx_alarm_high'] = child[obj_type]['attributes']['hiAlarm{0}'.format(lane_postfix)]
                retval[lane]['tx_alarm_low'] = child[obj_type]['attributes']['loAlarm{0}'.format(lane_postfix)]
                retval[lane]['tx_value'] = child[obj_type]['attributes']['value{0}'.format(lane_postfix)]
                retval[lane]['tx_warn_high'] = child[obj_type]['attributes']['hiWarn{0}'.format(lane_postfix)]
                retval[lane]['tx_warn_low'] = child[obj_type]['attributes']['loWarn{0}'.format(lane_postfix)]
            elif obj_type ==  'ethpmDOMCurrentStats':
                retval[lane]['amps_alarm_high'] = child[obj_type]['attributes']['hiAlarm{0}'.format(lane_postfix)]
                retval[lane]['amps_alarm_low'] = child[obj_type]['attributes']['loAlarm{0}'.format(lane_postfix)]
                retval[lane]['amps_value'] = child[obj_type]['attributes']['value{0}'.format(lane_postfix)]
                retval[lane]['amps_warn_high'] = child[obj_type]['attributes']['hiWarn{0}'.format(lane_postfix)]
                retval[lane]['amps_warn_low'] = child[obj_type]['attributes']['loWarn{0}'.format(lane_postfix)]

            elif obj_type == 'ethpmDOMTempStats':
                retval[lane]['temperature_alarm_high'] = child[obj_type]['attributes']['hiAlarm']
                retval[lane]['temperature_alarm_low'] = child[obj_type]['attributes']['loAlarm']
                retval[lane]['temperature_value'] = child[obj_type]['attributes']['value']
                retval[lane]['temperature_warn_high'] = child[obj_type]['attributes']['hiWarn']
                retval[lane]['temperature_warn_low'] = child[obj_type]['attributes']['loWarn']

            elif obj_type == 'ethpmDOMVoltStats':
                retval[lane]['voltage_alarm_high'] = child[obj_type]['attributes']['hiAlarm']
                retval[lane]['voltage_alarm_low'] = child[obj_type]['attributes']['loAlarm']
                retval[lane]['voltage_value'] = child[obj_type]['attributes']['value']
                retval[lane]['voltage_warn_high'] = child[obj_type]['attributes']['hiWarn']
                retval[lane]['voltage_warn_low'] = child[obj_type]['attributes']['loWarn']
    return retval


ips_ipn_devices={}

if collect_ipn:
    configured_spine_uplinks=cisco.aci.get_all_configured_spine_uplinks()
    for node_id in list(configured_spine_uplinks.keys()):
        pod_id=cisco.aci.get_podid_by_switch_id(node_id)
        for card,interface in configured_spine_uplinks[node_id]:
            lldp_adj_eps=cisco.aci.query('/api/node/mo/topology/pod-{}/node-{}/sys/lldp/inst/if-[eth{}/{}].json?query-target=subtree&target-subtree-class=lldpAdjEp&order-by=lldpAdjEp.name'.format(pod_id,node_id,card,interface))['imdata']
            for lldp_adj_ep in lldp_adj_eps:
                ips_ipn_devices[lldp_adj_ep['lldpAdjEp']['attributes']['sysName']]=lldp_adj_ep['lldpAdjEp']['attributes']['mgmtIp']
    ipn_data={}
    self._log.info('found following IPN devices:\n{}'.format(pformat(ips_ipn_devices)))
    for sys,ip in ips_ipn_devices.items():
        try:
            from copy import deepcopy
            cfg=deepcopy(self.configuration)
            cfg["ssh_username"]=ipn_username
            cfg["ssh_password"]=ipn_password
            cfg["ssh_host"]=ip
            ipn_data[sys]=cisco.nxos.query('show interface transceiver details',**cfg)
        except NetMikoTimeoutException:
            self._log.warning('cannot connect device {} via IP {} -> skipping'.format(sys,ip))

stats=cisco.aci.query('/api/node/class/ethpmDOMStats.json?rsp-subtree=children')['imdata']
retval=[]

order_of_keys = [  
                "hostname", 
                "interface", 
                "lane", 
                "rx_alarm_high",
                "rx_alarm_low",
                "rx_warn_high",
                "rx_warn_low",
                "rx_value",
                "tx_alarm_high",
                "tx_alarm_low",
                "tx_warn_high",
                "tx_warn_low",
                "tx_value",
                "amps_alarm_high",
                "amps_alarm_low",
                "amps_warn_high",
                "amps_warn_low",
                "amps_value",
                "temperature_alarm_high",
                "temperature_alarm_low",
                "temperature_warn_high",
                "temperature_warn_low",
                "temperature_value",
                "voltage_alarm_high",
                "voltage_alarm_low",
                "voltage_warn_high",
                "voltage_warn_low",
                "voltage_value"
                ]





for obj in stats:
    for lane,value in transform_aci_to_fsm2text_format(self,obj).items():
        list_of_tuples = [(key, try_decimal(value[key])) for key in order_of_keys]

        retval.append(OrderedDict(list_of_tuples))
for hostname,data in ipn_data.items():
    for lane in data:
        lane['hostname']=hostname
        list_of_tuples = [(key, try_decimal(lane[key])) for key in order_of_keys]
        retval.append(OrderedDict(list_of_tuples))



for idx,data in enumerate(retval):
    retval[idx]['rx_status'] = get_link_budget_status_text(data,'rx')
    retval[idx]['tx_status'] = get_link_budget_status_text(data,'tx')
    retval[idx]['voltage_status'] = get_link_budget_status_text(data,'voltage','warn',95,5)
    retval[idx]['temperature_status'] = get_link_budget_status_text(data,'temperature')
    retval[idx]['amps_status'] = get_link_budget_status_text(data,'amps','warn',95,5)
    

return retval
