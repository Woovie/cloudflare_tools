import configparser, json, requests

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

def main():
    domain = "woovie.net"
    zone_id = ""
    edit_records = []
    dnsq = DnsQuery()

    if dnsq.verify_token():
        for result in dnsq.request(f"{dnsq.api_url}zones", "get", dnsq.get_headers())['result']:
            if result['name'] == domain:
                zone_id = result['id']
    
        if len(zone_id) > 1:
            rec_id = ""
            records = dnsq.request(f"{dnsq.api_url}zones/{zone_id}/dns_records", "get", dnsq.get_headers())
            for record in records['result']:
                if "compute" in record['name']:
                    edit_records.append(record)
            if len(edit_records) > 0:
                public_ip = requests.get('https://api.ipify.org').text
                for record in edit_records:
                    payload = {
                        "type": record['type'],
                        "name": record['name'],
                        "content": public_ip,
                        "ttl": 1
                    }
                    result = dnsq.request(f"{dnsq.api_url}zones/{zone_id}/dns_records/{record['id']}", "put", dnsq.get_headers(), json.dumps(payload))
                    print(result)
main()
