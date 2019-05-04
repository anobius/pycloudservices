import urllib
import base64
from Crypto.Hash import HMAC,SHA
import time,random,requests,datetime
import json
import hashlib,hmac

class aladdin(object):

    @staticmethod
    def getHMACSig(dParams, key):
        '''
        Signature generation as per https://www.alibabacloud.com/help/doc-detail/34279.htm
        :param dParams: Parameters in dictionary form
        :param key: AccessKeySecret
        :return: returns signature in base64
        '''
        strQueryCanonical = "GET&%2F&";  # ignore uri lol
        # generate the string to sign from the sorted/canonicalized form
        for i in sorted(dParams.keys()):
            strQueryCanonical += urllib.quote_plus(urllib.urlencode({i: dParams[i]})) + "%26"  # + '\n'
        strQueryCanonical = strQueryCanonical[:-3]  # remove last 3 characters (%26), woops
        return base64.b64encode(hmac.new(key + "&", strQueryCanonical, hashlib.sha1).digest())  #append ampersand to key as per documentation, b64-encode the raw signature (not hex digested)

    def __init__(self,keyid,keysecret,api_callback='dns.aliyuncs.com',version='2015-01-09'):
        self.__id = keyid;
        self.__shh = keysecret;
        self._api = api_callback;
        self.__version = version;

    def _decorateAndSign(self, dParams):
        '''
        Preprocess a request
        :param dParams: parameters
        :return:
        '''
        timenow = time.time();
        dParams['Format'] = "json";
        dParams['Version'] = self.__version;#"2014-05-26";
        dParams['AccessKeyId'] = self.__id;
        dParams['SignatureMethod'] = 'HMAC-SHA1';
        dParams['Timestamp'] = datetime.datetime.utcfromtimestamp(timenow).strftime("%Y-%m-%dT%H:%M:%SZ");
        dParams['SignatureVersion'] = '1.0';
        dParams['SignatureNonce'] = str(int(timenow * random.random()));
        dParams['Signature'] = self.getHMACSig(dParams, self.__shh);
        return True;

    def sendReq(self,**dParams):
        self._decorateAndSign(dParams);
        result = requests.get('https://%s' % self._api,params=dParams);
        if (result.status_code != 200):
            print "AliFailed: HTTP code: %s, response: %s" % (result.status_code,result.content);
            return ;
        return json.loads(result.content);


class aladdinECS(aladdin):
    def __init__(self, keyid, keysecret, api_callback='ecs.aliyuncs.com',version='2014-05-26'):
        super(aladdinECS,self).__init__(keyid,keysecret,api_callback=api_callback,version=version);

    def getInstances(self,page=1,pagesize=100,**kwargs):
        '''
        Returns json response from Ali's DescribeInstances routine in dictionary format
        :return: JSON response in dictionary
        '''
        dParams = {
            "Action" : "DescribeInstances",
            "PageNumber" : page,
            "PageSize" : pagesize
        }
        dParams.update(kwargs);
        return self.sendReq(**dParams);

    def getInstanceStatus(self,**kwargs):
        '''
        Returns json response from Ali's DescribeInstanceStatus routine in dictionary format
        :return: JSON response in dictionary
        '''
        dParams = {
            "Action" : "DescribeInstanceStatus",
        }
        dParams.update(kwargs);
        return self.sendReq(**dParams);


    def getRegions(self,**kwargs):
        '''
        Returns json response from Ali's DescribeRegions routine in dictionary format
        :return: JSON response in dictionary
        '''
        dParams = {
            "Action" : "DescribeRegions",
        }
        dParams.update(kwargs);
        return self.sendReq(**dParams);

class aladdinDNS(aladdin):
    def delRecord(self,record_id):
        dParams = {
            'Action' : 'DeleteDomainRecord',
            'RecordId' : record_id
        }
        return self.sendReq(**dParams);


    def updateRecord(self,record_id, rr, Type, value, ttl=None):
        dParams = {
            'Action' : 'UpdateDomainRecord',
            'RecordId' : record_id,
            'RR' : rr,
            'Type' : Type,
            'Value' : value,
        }
        if ttl:
            dParams['TTL'] = ttl;
        return self.sendReq(**dParams);


    def addRecord(self,domain, rr, Type, value, ttl=None):
        dParams = {
            'Action' : 'AddDomainRecord',
            'DomainName' : domain,
            'RR' : rr,
            'Type' : Type,
            'Value' : value,
        }
        if ttl:
            dParams['TTL'] = ttl;
        return self.sendReq(**dParams);

    def getRecords(self,domain,page=1,pagesize=500):
        '''
        Returns json response from Ali's DescribeDomainRecords routine in dictionary format
        :param domain: domain to retrieve records from
        :param page: page number
        :param pagesize: page size
        :return: JSON response in dictionary
        '''
        dParams = {
            'Action' : 'DescribeDomainRecords',
            'DomainName' : domain,
            'PageNumber' : page,
            'PageSize' : pagesize,
        }
        self._decorateAndSign(dParams);
        return self.sendReq(**dParams);

    def getDomainList(self,page=1,pagesize=100):
        '''
        Returns json response from Ali's DescribeDomains routine in dictionary format
        :param page: page number
        :param pagesize: page size
        :return: JSON response in dictionary
        '''
        dParams = {
            'Action' : 'DescribeDomains',
            'PageNumber' : page,
            'PageSize' : pagesize,
        }
        #dParams['KeyWord'] = 'com';
        return self.sendReq(**dParams);





