import requests
import threading
import json
import time

API_VERSION = "2018-06-01"
ASM_VERSION = "2015-04-01"



def xmlToJson(root):
    rVal = dict();
    stripnametag = lambda x: x[x.find('}') + 1:];
    rVal["_nsmap"] = root.nsmap;
    rVal["_attrib"] = root.attrib;
    rVal['_children'] = list();
    for i in root.iterchildren():
        if len(i) == 0:
            #child["_nsmap"] = i.nsmap;
            child = dict();
            if i.attrib:
                child["_attrib"] = i.attrib;
            if i.text:
                child["text"] = i.text;
            child['tag'] = stripnametag(i.tag);
            rVal['_children'].append(child);
        else:
            rVal['_children'].append(xmlToJson(i));
    return rVal;


def xmlToJsonSimplifiedMax(root):
    rVal = dict();
    stripnametag = lambda x: x[x.find('}') + 1:];
    #rVal["_nsmap"] = root.nsmap;
    if root.attrib:
        rVal["_attrib"] = {stripnametag(k):v for k,v in root.attrib.iteritems()};
    cl = set([]);
    lrepeating = set([]);
    for i in root.iterchildren():
        if stripnametag(i.tag) not in cl:
            cl.add(stripnametag(i.tag));
        else:
            lrepeating.add(stripnametag(i.tag));
    #initialize proper data types
    for i in cl:
        if i in lrepeating:
            rVal[i] = list();
        else:
            rVal[i] = dict();
    #iterate with obtained data.
    for i in root.iterchildren():
        if stripnametag(i.tag) in lrepeating:
            if len(i) == 0:
                rVal[stripnametag(i.tag)].append({
                    "_attrib" : {stripnametag(k):v for k,v in i.attrib.iteritems()},
                    "text" : i.text
                } if i.attrib else i.text);
            else:
                rVal[stripnametag(i.tag)].append(xmlToJsonSimplifiedMax(i));
        else:
            if len(i) == 0:
                rVal[stripnametag(i.tag)] = {
                    "_attrib" : {stripnametag(k):v for k,v in i.attrib.iteritems()},
                    "text" : i.text
                } if i.attrib else i.text;
            else:
                rVal[stripnametag(i.tag)] = xmlToJsonSimplifiedMax(i);
    return rVal;


def xmlToJsonSimplified(root):
    rVal = dict();
    stripnametag = lambda x: x[x.find('}') + 1:];
    #rVal["_nsmap"] = root.nsmap;
    if root.attrib:
        rVal["_attrib"] = {stripnametag(k):v for k,v in root.attrib.iteritems()};
    cl = set([]);
    lrepeating = set([]);
    for i in root.iterchildren():
        if stripnametag(i.tag) not in cl:
            cl.add(stripnametag(i.tag));
        else:
            lrepeating.add(stripnametag(i.tag));
    #initialize proper data types
    for i in cl:
        rVal[i] = list();
    #iterate with obtained data.
    for i in root.iterchildren():
        if len(i) == 0:
            rVal[stripnametag(i.tag)].append({
                "_attrib" : {stripnametag(k):v for k,v in i.attrib.iteritems()},
                "text" : i.text
            } if i.attrib else i.text);
        else:
            rVal[stripnametag(i.tag)].append(xmlToJsonSimplified(i));
    return rVal;

class azul(object):
    def __init__(self,APP_ID,SECRET_KEY,TENANT_ID):
        self.__at = None;
        self.__app_id = APP_ID;
        self.__sk = SECRET_KEY;
        self.__tid = TENANT_ID;
        self.__tlocal =  threading.local();
        self._header_construct = lambda : {"Authorization" : "Bearer %s" % self.__tlocal.at};

    def __ensureARMAccessToken(self):
        if 'at' not in dir(self.__tlocal) or time.time() > self.__tlocal.at_expire:
            return self.refreshARMToken();


    def refreshARMToken(self):
        '''
        Refresh our Oauth token
        '''
        params = {
            "grant_type" : "client_credentials",
            "client_id" : self.__app_id,
            "client_secret" : self.__sk,
            "resource" : "https://management.azure.com/"
        };
        url = "https://login.microsoftonline.com/%s/oauth2/token" % self.__tid;
        res = requests.post(url,params);
        print res
        print res.content;
        dRes = json.loads(res.content);
        self.__tlocal.at = dRes['access_token'];
        self.__tlocal.at_expire = int(dRes['expires_on']);

    def getSubscriptions(self):
        '''
        Get your available subscriptions
        :return: dictionary form of results
        '''
        self.__ensureARMAccessToken();
        params = {
            "api-version" : API_VERSION,
        }
        url = "https://management.azure.com/subscriptions"
        res = requests.get(url,params=params,headers=self._header_construct());
        print res;
        return json.loads(res.content);

    def getSubscriptionInfo(self,subscription_id):
        '''
        Get subscription details
        :param subscription_id: subscription id
        :return: dictionary form of results
        '''
        self.__ensureARMAccessToken();
        params = {
            "api-version" : API_VERSION,
        }
        url = "https://management.azure.com/subscriptions/%s" % subscription_id
        res = requests.get(url,params=params,headers=self._header_construct());
        print res;
        return json.loads(res.content);

    def getVMList(self, subscription_id,resource_group=None,resolveNetworkProfile=False,mangle_add_resource_group_info=False):
        '''
        Get the list of VM's available
        :param subscription_id: subscription id
        :param resource_group: name of the resource group
        :param resolveNetworkProfile: Retrieve network profile if True
        :param mangle_add_resource_group_info: append resource group info if True
        :return: dictionary 
        '''
        #todo: fix resolveNetworkProfile
        #note: storageProfile.osDisk
        self.__ensureARMAccessToken();
        params = {
            "api-version": API_VERSION,
        }
        if resource_group:
            url = "https://management.azure.com/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Compute/virtualMachines" % (subscription_id,resource_group);
        else:
            url = "https://management.azure.com/subscriptions/%s/providers/Microsoft.Compute/virtualMachines" % subscription_id;
        res = requests.get(url, params=params, headers=self._header_construct());
        print res;
        dJson = json.loads(res.content);
        if resolveNetworkProfile:
            for i in dJson['value']:
                nitwurk = list();
                for j in i['properties']['networkProfile']['networkInterfaces']:
                    jurl = "https://management.azure.com/" +  j['id'];
                    nitwurk.append(
                        json.loads(
                            requests.get(jurl, params=params, headers=self._header_construct()).content
                        )
                    );
                i['properties']['networkProfile']['networkInterfaces'] = nitwurk;
        if mangle_add_resource_group_info:
            for i in dJson['value']:
                sample = i['id'].split('/');
                for c,v in enumerate(sample):
                    if v == "resourceGroups":
                        i[u'resource_group'] = sample[c+1];
                        break;


        return dJson;
    def getResourceSKUs(self, subscription_id):
        '''
        get available server plans
        :param subscription_id: subscription id
        :return: dictionary form of results
        '''
        self.__ensureARMAccessToken();
        params = {
            "api-version": API_VERSION,
        }
        url = "https://management.azure.com/subscriptions/%s/providers/Microsoft.Compute/skus" % subscription_id;
        res = requests.get(url, params=params, headers=self._header_construct());
        #print res;
        return json.loads(res.content);

    def getPublicAddress(self, subscription_id, resource_group):
        '''
        Get the public addresses assigned to a resource group
        :param subscription_id: subscription id
        :param resource_group: name of the resource group
        :return dictionary form of results
        '''
        self.__ensureARMAccessToken();
        params = {
            "api-version": API_VERSION,
        }
        url = 'https://management.azure.com/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Network/publicIPAddresses' % (subscription_id, resource_group);
        res = requests.get(url, params=params, headers=self._header_construct());
        #print res;
        #print res.content
        return json.loads(res.content);

from lxml import etree

class asmAzul(object):
    def __init__(self,cert_pem_path):
        self.__certpath = cert_pem_path;

    def getVMList(self, subscription_id):
        url = "https://management.core.windows.net/%s/services/vmimages" % subscription_id;
        res = requests.get(url, headers={"x-ms-version" : ASM_VERSION}, cert=self.__certpath);
        print res;
        return res;

    def getServiceList(self, subscription_id):
        url = "https://management.core.windows.net/%s/services/hostedservices" % subscription_id;
        res = requests.get(url, headers={"x-ms-version" : ASM_VERSION}, cert=self.__certpath);
        print res;
        rVal = dict();
        root = etree.fromstring(res.content);
        return xmlToJsonSimplifiedMax(root);
        ns = root.nsmap[None];
        nametag = lambda x: "{%s}%s" % (ns,x);
        stripnametag = lambda x: x.replace("{%s}" % ns,"");
        for i in root.iterchildren():
            property = dict();
            key = i.find(nametag('ServiceName')).text;
            for j in i.find(nametag('HostedServiceProperties')).iterchildren():
                if len(j) == 0: #ignore nodes with children
                    property[stripnametag(j.tag)] = j.text;
                del j;
            rVal[key] = property;
            del i;
        del root
        print rVal;
        return rVal;

    def getServiceDeployments(self, subscription_id, cloudservice_name):
        url = "https://management.core.windows.net/%s/services/hostedservices/%s" % (subscription_id,cloudservice_name);
        res = requests.get(url, headers={"x-ms-version" : ASM_VERSION},params={"embed-detail" : True}, cert=self.__certpath,timeout=30);
        print res;
        rVal = list();
        root = etree.fromstring(res.content);
        dRes = xmlToJsonSimplified(root);
        if dRes['Deployments'][0]:
            for i in dRes['Deployments'][0]['Deployment']:
                nDeployment = dict();
                nDeployment['Name'] = i['Name'][0];

                nDeployment['IP'] = i['VirtualIPs'][0]['VirtualIP'][0]['Address'][0];

                roles = list();
                for j in i['RoleInstanceList']:
                    role = dict();
                    drole = j['RoleInstance'][0];
                    role['hostname'] = drole['HostName'][0];
                    role['specs'] = drole['InstanceSize'][0];
                    roles.append(role);
                nDeployment['Roles'] = roles;
                rVal.append(nDeployment);
        return xmlToJsonSimplifiedMax(etree.fromstring(res.content));

