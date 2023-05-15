#!/usr/bin/env -S jinjamator -t
import socket


def lookup_mac(hostname):
    try:
        ip_address = socket.gethostbyname(hostname.strip())
        log.info(f"resolved {hostname.strip()} to {ip_address}")
    except socket.gaierror:
        log.warning(f"Cannot resolve {hostname}")
        return None, None
    try:
        data = ssh.query(
            f"show ip arp {ip_address} vrf {vrf}",
            ssh_username=ssh_username,
            ssh_password=ssh_password,
            ssh_host=ssh_host,
        )[0]
        log.info(
            f"found mac {data['mac']} for ip {ip_address} in vrf {vrf} on device {ssh_host}"
        )
        return (mac.to_unix(data["mac"]), ip_address)
    except IndexError:
        log.warning(f"Cannot find ip {ip_address} in arp table of {ssh_host}")
        return None, ip_address


mac_address, ip_address = lookup_mac(hostname)
if not ip_address:
    raise ValueError(f"Cannot find ip address for hostname {hostname} -> aborting")
if mac_address:
    log.info(
        f"Adding {hostname.lower()} with mac {mac_address} to ise group id {endpoint_group}"
    )
    result = cisco.ise.connect().add_endpoint(
        name=hostname.lower(),
        mac=mac_address.upper(),
        group_id=endpoint_group,
        description=description,
    )
    if not result["success"]:
        raise Exception(result["response"])
else:
    raise ValueError(f"Cannot find mac address for ip {ip_address} -> aborting")
return {"status": "success"}
