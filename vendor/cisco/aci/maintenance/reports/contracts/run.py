from datetime import datetime

ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
self.configuration["excel_file_name"] = f"contracts_{ts}"

retval = []
for dn in [
    item["vzBrCP"]["attributes"]["dn"]
    for item in cisco.aci.query("/api/node/class/vzBrCP.json")["imdata"]
]:
    children = cisco.aci.query(f"/api/node/mo/{dn}.json?query-target=children")[
        "imdata"
    ]
    consumers = [
        item["vzRtCons"]["attributes"]["tDn"] for item in children if "vzRtCons" in item
    ]
    providers = [
        item["vzRtProv"]["attributes"]["tDn"] for item in children if "vzRtProv" in item
    ]
    vz_any_consumers = [
        item["vzRtAnyToCons"]["attributes"]["tDn"]
        for item in children
        if "vzRtAnyToCons" in item
    ]
    vz_any_providers = [
        item["vzRtAnyToProv"]["attributes"]["tDn"]
        for item in children
        if "vzRtAnyToProv" in item
    ]
    orphaned = "no"
    if (len(consumers) == 0 and len(vz_any_consumers) == 0) or (
        len(providers) == 0 and len(vz_any_providers) == 0
    ):
        log.info(f"orphaned contract found: {dn}")
        orphaned = "yes"
    else:
        log.info(
            "contract {0} in use by:\n\tproviders:{1}\n\tconsumers:{2}".format(
                dn, "\n".join(providers), "\n".join(consumers)
            )
        )
    retval.append(
        {
            "contract_dn": dn,
            "consumers": "\r\n".join(consumers),
            "vz_any_providers": "\r\n".join(vz_any_providers),
            "vz_any_consumers": "\r\n".join(vz_any_consumers),
            "providers": "\r\n".join(providers),
            "providers_count": len(providers),
            "consumers_count": len(consumers),
            "vz_any_consumers_count": len(vz_any_consumers),
            "vz_any_providers_count": len(vz_any_providers),
            "orphaned": orphaned,
        }
    )

return retval
