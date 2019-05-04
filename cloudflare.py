import httplib, urllib, json, threading, time, collections;


class cfDNS():
    def __init__(self, email, token):
        self.email = email;
        self.user_token = token;
        self.headers = {"X-Auth-Email": email, "X-Auth-Key": token, "Content-type": "application/json"};

    def apiRequest(self, PATH, method="GET", params={}, isJson=False):
        conn = httplib.HTTPSConnection("api.cloudflare.com");
        parameters = urllib.urlencode(params) if not isJson else json.dumps(params);
        if method != "GET":
            conn.request(method, PATH, parameters, self.headers);
        else:
            conn.request(method, PATH + "?" + parameters, headers=self.headers);
        response = conn.getresponse();
        data = response.read();
        result = json.loads(data);

        return result;

    def getZoneList(self):
        rVal = {};
        page = 1;
        while (True):
            response = self.apiRequest("/client/v4/zones",params={'per_page':50,'page':page});
            print response
            if (response['success']):
                total_pages = int(response['result_info']['total_pages']);
                for i in response['result']:
                    rVal[i['name']] = {};
                    rVal[i['name']]['id'] = i['id'];
                    rVal[i['name']]['owner'] = i['owner']['email'];
                    rVal[i['name']]['status'] = i['status'];
                page += 1;
                if (page > total_pages):
                    break;
        return rVal if rVal != {} else False;

    def searchZone(self,domain):
        rVal = {};
        response = self.apiRequest("/client/v4/zones",params={"name":domain});
        if (response['success']):
            for i in response['result']:
                rVal[i['name']] = {};
                rVal[i['name']]['id'] = i['id'];
                rVal[i['name']]['owner'] = i['owner']['email'];
                rVal[i['name']]['status'] = i['status'];
            return rVal;
        return response['success'];

    def getZoneList(self):
        rVal = {};
        response = self.apiRequest("/client/v4/zones");
        if (response['success']):
            for i in response['result']:
                rVal[i['name']] = {};
                rVal[i['name']]['id'] = i['id'];
                rVal[i['name']]['owner'] = i['owner']['email'];
                rVal[i['name']]['status'] = i['status'];
            return rVal;
        return response['success'];

    def getDNSRecordList(self, zoneid):
        rVal = []
        response = self.apiRequest("/client/v4/zones/%s/dns_records" % zoneid, params={"match": "all"});
        if (response['success']):
            for i in response['result']:
                dTemp = {};
                dTemp['id'] = i['id'];
                dTemp['type'] = i['type'];
                dTemp['name'] = i['name'];
                dTemp['value'] = i['content'];
                dTemp['ttl'] = i['ttl'];
                dTemp['isproxied'] = i['proxied'];
                dTemp['islocked'] = i['locked'];
                rVal.append(dTemp);
            return rVal;
        return response['success'];

    def updateDNSRecord(self, zone_id, record_id, recordtype, name, content, ttl=None, isProxied=None):
        dVals = {"name": name, "type": recordtype, "content": content};
        if (ttl != None):
            dVals["ttl"] = ttl;
        if (isProxied != None):
            dVals["proxied"] = isProxied;
        response = self.apiRequest("/client/v4/zones/%s/dns_records/%s" % (zone_id, record_id), "PUT", dVals, True);
        return response['success'];

    def createZone(self,name):
        dVals = {"name": name};
        response = self.apiRequest("/client/v4/zones", "POST", dVals, True);
        if (response['success']):
            return response['result']['id'];
        print response;
        return response['success'];

    def createDNSRecord(self, zone_id, recordtype, name, content, ttl=None, isProxied=None):
        dVals = {"type": recordtype, "name": name, "content": content};
        if (ttl != None):
            dVals["ttl"] = ttl;
        if (isProxied != None):
            dVals["proxied"] = isProxied;
        response = self.apiRequest("/client/v4/zones/%s/dns_records" % zone_id,"POST", dVals, True);
        if (response['success']):
            return response['result']['id'];
        print response;
        return response['success'];

    def deleteDNSRecord(self, zone_id, record_id):
        response = self.apiRequest("/client/v4/zones/%s/dns_records/%s" % (zone_id, record_id),"DELETE");
        print response;
        return response['success'];

    def deleteZone(self,zone_id):
        response = self.apiRequest("/client/v4/zones/%s" % zone_id,"DELETE");
        print response;
        return response['success'];

