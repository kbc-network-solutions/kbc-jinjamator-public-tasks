retval = []

for filter_dn in [
    item["vzFilter"]["attributes"]["dn"]
    for item in cisco.aci.query("/api/node/class/vzFilter.json")["imdata"]
]:
    log.info(f"working on dn {filter_dn}")
    orphaned = "no"
    relns = cisco.aci.query(
        f"/api/node/mo/{filter_dn}.json?query-target=children&target-subtree-class=relnFrom"
    )["imdata"]
    relns_count = len(relns)

    # log.debug(relns)
    if relns_count == 0:
        orphaned = "yes"
    retval.append(
        {"dn": filter_dn, "used_by_object_count": relns_count, "orphaned": orphaned}
    )

return retval
