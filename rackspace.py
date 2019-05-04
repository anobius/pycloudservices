import requests
import json
import threading


class bigrax(object):
    def __init__(self,user,apikey):
        self.__u = user;
        self.__k = apikey;
        self.__token = None;
        self.genheader = lambda : {"Content-Type":"application/json", "Accept" : "application/json", "X-Auth-Token" : self.__token};
        self.__endpoint = dict();
        self.lastmsg = threading.local()
    def getLastError(self):
        try:
            return self.lastmsg.error;
        except:
            return None;

    def __setLastError(self, msg):
        self.lastmsg.error = msg;

    def refreshToken(self):
        jsonreq = {"auth":{"RAX-KSKEY:apiKeyCredentials":{"username":self.__u,"apiKey" : self.__k}}};
        res = requests.post("https://identity.api.rackspacecloud.com/v2.0/tokens",json=jsonreq,headers={"Content-type":"application/json"});
        if res.status_code != 200:
            return False;
        dRes = json.loads(res.content);
        #from pprint import pprint
        #pprint(dRes);
        self.__token = dRes['access']['token']['id'];
        for i in dRes['access']['serviceCatalog']:
            if i['type'] == 'compute':
                new = dict();
                for j in i['endpoints']:
                    new[j['region']] = j['publicURL'];
                try:
                    old = self.__endpoint['compute'];
                    self.__endpoint['compute'] = new;
                    del old;
                except:
                    self.__endpoint['compute'] = new;

        return True;

    def doReq(self,method,request_uri,catalog,key,**kwargs):
        not self.__token and self.refreshToken();
        res = requests.request(method,self.__endpoint[catalog][key] + request_uri.replace(self.__endpoint[catalog][key],"") ,headers=self.genheader(),**kwargs);
        if res.status_code != 200:
            self.__setLastError((res.status_code,res.content));
            return None;
        return json.loads(res.content);

    def getServerList(self,region='HKG'):
        #not self.__token and self.refreshToken();
        #res = requests.get("%s/servers/detail" % self.__compute_endpoint[region],headers=self.genheader());
        res = self.doReq("get","/servers/detail",'compute',region);
        #print res;
        return res

    def getFlavorList(self,region='HKG'):
        '''
        Contains technical information regarding available server plans
        :param region: region identifier
        :return:
        '''
        res = self.doReq("get","/flavors/detail",'compute',region);
        #print res;
        return res

