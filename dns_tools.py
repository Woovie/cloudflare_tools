import configparser, json, requests, re

config = configparser.ConfigParser()
config.read('config.ini')

class DnsQuery():
    def __init__(self):
        self.api_url = config['cloudflare']['endpoint']
        self.token = config['cloudflare']['token']
        pass

    def verify_token(self) -> bool:
        verify_endpoint = "user/tokens/verify"
        verify_url = f"{self.api_url}{verify_endpoint}"
        return self.request(verify_url, "get", self.get_headers())

    def get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def request(self, url: str, method: str, headers: dict, payload: dict = None) -> dict:
        methods = {
            "get": requests.get,
            "post": requests.post,
            "put": requests.put
        }
        if method in methods:
            r = methods[method](url, headers=headers, data = payload)
            return json.loads(r.text)

class UpdateDomains():
    def __init__(self, dnsq: DnsQuery, domain: str, domain_filter: str):
        self.dnsq = dnsq
        self.domain = domain
        self.domain_filter = domain_filter

    def get_zone_id(self):
        query = self.dnsq.request(f"{self.dnsq.api_url}zones", "get", self.dnsq.get_headers())
        for domain in query['result']:
            if domain['name'] == self.domain:
                return domain['id']

    def get_dns_records(self, domain_id):
        query = self.dnsq.request(f"{self.dnsq.api_url}zones/{domain_id}/dns_records", "get", self.dnsq.get_headers())
        records = []
        pattern = re.compile(self.domain_filter)
        for record in query['result']:
            if re.match(pattern, record['name']):
                records.append(record)
        return records

    def update_record(self, domain_id, record_id, payload):
        result = self.dnsq.request(f"{self.dnsq.api_url}zones/{domain_id}/dns_records/{record_id}", "put", self.dnsq.get_headers(), json.dumps(payload))
        return result
