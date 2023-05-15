from cgitb import lookup
from datetime import datetime
ts=datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
self.configuration['excel_file_name']=f'endpoints_{ts}'
import re

rgx_context=re.compile(r'uni/tn-(.+)/ctx-(.+)/cep-(.+)')
rgx_epg=re.compile(r'uni/tn-(.+)/ap-(.+)/epg-(.+)/cep-(.+)')
rgx_pbr=re.compile(r'uni/tn-(.+)/LDevInst-\[(.+)\]-ctx-(.+)/G-(.+)/cep-(.+)')

lookup_table={
    'epg':{},
    'bd':{}

}
epgs=cisco.aci.query('/api/node/class/fvAEPg.json?rsp-subtree=children&order-by=fvAEPg.name')['imdata']
bds=cisco.aci.query('/api/node/class/fvBD.json?rsp-subtree=children&order-by=fvBD.name')['imdata']
for result in bds:
    k=list(result.keys())[0]
    if k == "fvBD":
        bd=result[k]['attributes']['dn']
        lookup_table['bd'][bd]={ 'name':result[k]['attributes']['name'] ,
                                'subnet':[]}
        for child in result['fvBD']['children']:
            ck=list(child.keys())[0]
            if ck == "fvSubnet":
                ip=child[ck]['attributes']['ip']
                if ip not in lookup_table['bd'][bd]['subnet']:
                    lookup_table['bd'][bd]['subnet'].append(ip)
            if ck == "fvRsCtx":
                ctx=child[ck]['attributes']['tnFvCtxName']
                lookup_table['bd'][bd]['vrf']=ctx


for result in epgs:
    k=list(result.keys())[0]
    if k == "fvAEPg":
        epg=result[k]['attributes']['dn']
        lookup_table['epg'][epg]={'name':result[k]['attributes']['name']}
        for child in result['fvAEPg']['children']:
            ck=list(child.keys())[0]
            if ck == "fvRsBd":
                bd=child[ck]['attributes']['tDn']
                
                lookup_table['epg'][epg]['bd']=lookup_table['bd'][bd]
                lookup_table['bd'][bd]['epg']=epg

# return lookup_table    
data={}
for line in cisco.aci.query('/api/node/class/fvCEp.json?rsp-subtree=children&order-by=fvCEp.encap')['imdata']:
    attrs=line['fvCEp']['attributes']
    mac=attrs['mac']
    if mac not in data:
        data[mac]={
            "MAC Address":attrs["mac"],
            "IP Address":"",
            "Tenant":"",
            "Application Profile": "",
            "EPG": "",
            "VRF":"",
            "Bridge Domain":"",
            "Path":"",
            "Encapsulation":attrs.get("encap",""),
            "Subnet":"",
            "Status": attrs.get("lcC","")
        }

    res=rgx_context.match(attrs["dn"])
    if res:
        data[mac]["Tenant"]=res.group(1)
        data[mac]["VRF"]=res.group(2)
    else:
        res=rgx_epg.match(attrs["dn"])
        
        if res:
            epg_dn=f"uni/tn-{res.group(1)}/ap-{res.group(2)}/epg-{res.group(3)}"
            data[mac]["Tenant"]=res.group(1)
            data[mac]["Application Profile"]=res.group(2)
            data[mac]["EPG"]=res.group(3)
            data[mac]["VRF"]=lookup_table['epg'][epg_dn]['bd']['vrf']
            data[mac]["Subnet"]="\n".join(lookup_table['epg'][epg_dn]['bd']['subnet'])
            data[mac]["Bridge Domain"]=lookup_table['epg'][epg_dn]['bd']['name']
            
            # for qresult in cisco.aci.query(f'/api/node/mo/uni/tn-{data[mac]["Tenant"]}/ap-{data[mac]["Application Profile"]}/epg-{data[mac]["EPG"]}.json?query-target=children&rsp-subtree=children')['imdata']:
            #     k=list(qresult.keys())[0]
            #     if k == "fvRsBd":
            #         data[mac]["Bridge Domain"]=qresult["fvRsBd"]["attributes"]["tnFvBDName"]
            #         for bresult in cisco.aci.query(f'/api/node/mo/{qresult["fvRsBd"]["attributes"]["tDn"]}.json?query-target=children&target-subtree-class=fvRsCtx,fvSubnet')['imdata']:
            #             bk=list(bresult.keys())[0]
            #             if bk == "fvRsCtx":
            #                 data[mac]["VRF"]=bresult["fvRsCtx"]["attributes"]["tnFvCtxName"]
            #             if bk == "fvSubnet":
            #                 data[mac]["Subnet"]=bresult["fvSubnet"]["attributes"]["ip"]

        else:
            res=rgx_pbr.match(attrs["dn"])
            if res:
                data[mac]["Tenant"]=res.group(1)
                data[mac]["VRF"]=res.group(3)
                data[mac]["EPG"]=res.group(2).split()[-1]

    for child in line['fvCEp'].get("children",[]):
        
        child_type=list(child.keys())[0]
        child_attrs=child[child_type]["attributes"]
        if child_type == "fvIp":
            data[mac]["IP Address"]=child_attrs["addr"]
        if child_type == "fvRsCEpToPathEp":
            data[mac]["Path"]=child_attrs["tDn"]
        

    

return list(data.values())