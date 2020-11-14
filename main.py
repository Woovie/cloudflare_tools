import configparser, requests
from dns_tools import DnsQuery, UpdateDomains

config = configparser.ConfigParser()
config.read('config.ini')

def main():
    dnsq = DnsQuery()
    ud = UpdateDomains(dnsq, config['personal']['domain'], config['personal']['domain_filter'])
    domain_id = ud.get_zone_id()
    if domain_id:
        dns_records = ud.get_dns_records(domain_id)
        if len(dns_records) > 0:
            ip = requests.get("https://api.ipify.org").text
            for record in dns_records:
                payload = {
                    "type": record['type'],
                    "name": record['name'],
                    "content": ip,
                    "ttl": record['ttl']
                }
                result = ud.update_record(domain_id, record['id'], payload)
                print(result)

main()
