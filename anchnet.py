import requests
import base64
import json

zones = ['ac1','ac2','ac3']

class anchor(object):
    def __init__(self,clientId,secretKey):
        self.__c = base64.b64encode("%s:%s" % (clientId,secretKey));
        self.__token = "";

    def refreshToken(self):
        headers = {"Authorization" : "Basic %s" % self.__c};
        haha = requests.post("https://openapi.anchnet.com/v2/oauth2/token",headers=headers,params={"scope":"*","grant_type" : "client_credentials"});
        d = json.loads(haha.content);
        self.__token = d['access_token'];
        return True;

    @property
    def __gen_header(self):
        return {"Authorization": "Bearer %s" % self.__token};

    def doReq(self,*args,**kwargs):
        while True:
            res = requests.request(*args,headers=self.__gen_header,**kwargs);
            if res.status_code != 400: return res;
            self.refreshToken();

    def getInstances(self,zone=None):
        if not zone:
            rVal = list();
            for i in zones:
                res = self.doReq("get","https://openapi.anchnet.com/v2/zone/%s/instances" % i,);
                print res
                rVal += json.loads(res.content)['instances'];
        else:
            res = self.doReq("get","https://openapi.anchnet.com/v2/zone/%s/instances" % zone,);
            rVal = json.loads(res.content)['instances'];
        return rVal;

