from datetime import datetime

ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
self.configuration["excel_file_name"] = f"epgs_{ts}"

retval = []
for epg_dn in [
    item["fvAEPg"]["attributes"]["dn"]
    for item in cisco.aci.query("/api/node/class/fvAEPg.json")["imdata"]
]:
    log.info(f"working on dn {epg_dn}")
    orphaned = "no"
    endpoints = cisco.aci.query(
        f"/api/node/mo/{epg_dn}.json?query-target=children&target-subtree-class=fvCEp&rsp-subtree=children&rsp-subtree-class=fvRsToVm,fvRsVm,fvRsHyper,fvRsCEpToPathEp,fvIp,fvPrimaryEncap&order-by=fvCEp.mac"
    )["imdata"]
    endpoint_count = len(endpoints)
    # log.debug(endpoint_count)
    if endpoint_count == 0:
        orphaned = "yes"
    retval.append(
        {"dn": epg_dn, "endpoint_count": endpoint_count, "orphaned": orphaned}
    )
return retval
