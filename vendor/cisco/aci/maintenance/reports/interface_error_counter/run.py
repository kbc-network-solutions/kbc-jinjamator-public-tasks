from datetime import datetime
ts=datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
self.configuration['excel_file_name']=f'interface_error_counters_{ts}'

def has_error(item):
    for attr,value in item['rmonDot3Stats']['attributes'].items():
        if attr in ['dn','clearTs','modTs','childAction','status']:
            continue
        if value != '0':
            return True
    return False

def get_formatted_entry(item):
    data={'dn':item['dn']}
    for k in ['clearTs','modTs','childAction','status']:
        del item[k]
    data.update(item)
    return data 
retval = []

for node_id in nodes_to_collect:
    pod_id = cisco.aci.get_podid_by_switch_id(node_id)
    for obj in cisco.aci.query(f'/api/node/mo/topology/pod-{pod_id}/node-{node_id}/sys.json?query-target=subtree&target-subtree-class=rmonDot3Stats&order-by=rmonDot3Stats.dn|desc')['imdata']:
        if not has_error(obj) and exclude_empty:
            continue
        for int_type in include_interface_types:
            if int_type in obj['rmonDot3Stats']['attributes']['dn']:
                retval.append(get_formatted_entry(obj['rmonDot3Stats']['attributes']))
if not retval and exclude_empty:
    log.info('All interfaces clean')
return retval
