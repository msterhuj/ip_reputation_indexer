import ipaddress

def subnet_to_ip_list(subnet_str):
    network = ipaddress.ip_network(subnet_str, strict=False)
    return [str(ip) for ip in network.hosts()]

subnet_list = ["127.0.0.0/24"]

for subnet in subnet_list:
    for ip in subnet_to_ip_list(subnet):
        print("- " + ip)
