import httplib,urllib,json,threading,time,collections;
import requests



ZH_CN = dict();
ZH_CN['/Domain.Info'] = "域信息"
ZH_CN['/Domain.List'] = "域列表"
ZH_CN['/Domain.Create'] = "域创建"
ZH_CN["/Record.Create"] = "记录创建"
ZH_CN["/Record.List"] = "记录列表"
ZH_CN["/Record.Remove"] = "记录删除"
ZH_CN["/Record.Remark"] = "记录说明"
ZH_CN["/Record.Status"] = "记录状态"
ZH_CN["/Record.Modify"] = "记录修改"
ZH_CN["DOMAIN_NOT_EXIST"] = "INFO: 域不存在!"
ZH_CN["DOMAIN_RECORDS_CLEARED"] = "INFO: 清除了域ID的记录: %s"
ZH_CN["DOMAIN_NO_RECORDS_TO_CLEAR"] = "INFO: 没有记录要清除！ 码：%s"
ZH_CN["API_ERROR"] = "%s 错误！ 码：%s \n\t%s"

EN_US = dict();
EN_US['/Domain.Info'] = "Domain Info"
EN_US['/Domain.List'] = "Domain List"
EN_US['/Domain.Create'] = "Domain Create"
EN_US["/Record.Create"] = "Record Create"
EN_US["/Record.List"] = "Record List"
EN_US["/Record.Remove"] = "Record Remove"
EN_US["/Record.Remark"] = "Record Remark"
EN_US["/Record.Status"] = "Record Status"
EN_US["/Record.Modify"] = "Record Modify"
EN_US["DOMAIN_NOT_EXIST"] = "INFO: Domain does not exist!"
EN_US["DOMAIN_RECORDS_CLEARED"] = "INFO: Records cleared for domain id: %s"
EN_US["DOMAIN_NO_RECORDS_TO_CLEAR"] = "INFO: No records to clear! code: %s"
EN_US["API_ERROR"] = "%s error! code: %s\n\t%s"





HEADERS={"Content-type":"application/x-www-form-urlencoded","Accept":"text/json","User-Agent": "curlor"};


class CN():
    LANG = EN_US;
    def __init__(self, email, token):
        self.user = email;
        self.password = token;
        self.CONN_COUNT = 0;
        self.user_token = '0';

    def verifyOutput(self,module,result):
        #print result;
        code = result['status']['code'];
        if (code == '1'):
            return result;
        elif (code == '10'):#code for no records
            return result;
        elif (code == '9'):#code for no domains
            return result;
        else:
            print result['status']['code']
            print result['status']['message']
            print module
            raise Exception(self.LANG["API_ERROR"] % (module, result['status']['code'], result['status']['message']));


    def apiRequest(self,PATH,params):

        params['format'] = 'json';
        params['login_token'] = "%s,%s" % (self.user,self.password);
        response = requests.post("https://dnsapi.cn%s" % PATH,data=params,headers=HEADERS); #conn.getresponse();
        data = response.content;
        result = json.loads(data);

        return result;

    def getDomainInfo(self,_id):
        method = '/Domain.Info';
        params = {'domain_id': _id };
        result = self.apiRequest(method,params);

        return self.verifyOutput(self.LANG[method], result);

    def getDomainList(self):
        method = '/Domain.List';
        params = {};
        result = self.apiRequest(method,params);

        return self.verifyOutput(self.LANG[method], result);

    def addDomain(self,domain):
        method = '/Domain.Create';
        params = {'domain':domain};
        result = self.apiRequest(method,params);
        return self.verifyOutput(self.LANG[method], result);

    def recordCreate(self,_id,sub_domain,record_type,ip,record_line='默认',remark='',isEnabled=True):
        method = "/Record.Create";
        params = {'domain_id':_id,'sub_domain':sub_domain,'record_type':record_type,'record_line':record_line,'value':ip};
        result = self.apiRequest(method,params);
        returnVal = self.verifyOutput(self.LANG[method], result);
        record_id = returnVal['record']['id'];
        if (remark != ''):
            self.setRecordRemark(_id,record_id,remark);
        if (not isEnabled):
            self.setRecordStatus(_id,record_id,False);
        return returnVal;


    def getRecordList(self,_id):
        method = "/Record.List";
        params = {'domain_id':_id};
        result = self.apiRequest(method,params);
        return self.verifyOutput(self.LANG[method], result);

    def delRecord(self,_id,record_id):
        method = "/Record.Remove";
        params = {'domain_id':_id,'record_id':record_id};
        result = self.apiRequest(method,params);
        return self.verifyOutput(self.LANG[method], result);

    def setRecordRemark(self,_id,record_id,remark):
        method = "/Record.Remark";
        params = {'domain_id':_id,'record_id':record_id,'remark':remark};
        result = self.apiRequest(method,params);
        return self.verifyOutput(self.LANG[method], result);

    def setRecordStatus(self,_id,record_id,status):
        method = "/Record.Status";
        status = 'enable' if status else 'disable';
        params = {'domain_id':_id,'record_id':record_id,'status':status};
        result = self.apiRequest(method,params);
        return self.verifyOutput(self.LANG[method], result);

    def updateRecord(self,_id,record_id,sub_domain,record_type,ip,record_line='默认',remark='',isEnabled=True):
        method = "/Record.Modify";
        params = {'domain_id':_id,'record_id':record_id,'sub_domain':sub_domain,'record_type':record_type,'record_line':record_line,'value':ip};
        result = self.apiRequest(method,params);
        returnVal = self.verifyOutput(self.LANG[method], result);
        if (remark != ''):
            self.setRecordRemark(_id,record_id,remark);

        self.setRecordStatus(_id,record_id,isEnabled);
        return returnVal;

    def getDomainID(self,domainList,domainName):
        try:
            for i in domainList['domains']:
                if (i['name'] == domainName):
                    return i['id'];
        except:
            print self.LANG["DOMAIN_NOT_EXIST"];
        return -1;

    def deleteAllRecords(self,_id):
        recordList = self.getRecordList(_id);
        if (recordList['status']['code'] != '10'):
            for i in recordList['records']:
                self.delRecord(_id,i['id']);
            print self.LANG["DOMAIN_RECORDS_CLEARED"] % _id;
        else:
            print self.LANG["DOMAIN_NO_RECORDS_TO_CLEAR"] % recordList['status']['code'];



class EN(CN):
    '''
    English DNSPOD
    '''
    def __init__(self,user,password):
        CN.__init__(self, user, password);
        self.__login(user,password);
        self.__LANG = EN_US;


    def __login(self,user,password):
        params = {'login_email':user,'login_password':password};
        result = self.apiRequest("/Auth",params);
        if (result['status']['code'] == '1'):
            #return result['user_token'];
            self.user_token = result['user_token']
            del user;del password; #zero this thing. python zeroes with del?
        else:
            del user;del password;
            raise Exception("Login error! code: %s\n\t%s" % (result['status']['code'],result['status']['message']));


    def apiRequest(self,PATH,params):

        params['format'] = 'json';
        params['user_token'] = self.user_token;
        conn = httplib.HTTPSConnection("api.dnspod.com");
        conn.request("POST",PATH,urllib.urlencode(params),HEADERS);
        response = conn.getresponse();
        data = response.read();

        result = json.loads(data);

        return result;



    def recordCreate(self,_id,sub_domain,record_type,ip,record_line='default',remark='',isEnabled=True):
        method = "/Record.Create";
        params = {'domain_id':_id,'sub_domain':sub_domain,'record_type':record_type,'record_line':record_line,'value':ip};
        result = self.apiRequest(method,params);
        returnVal = self.verifyOutput(self.__LANG[method],result);
        record_id = returnVal['record']['id'];
        if (remark != ''):
            self.setRecordRemark(_id,record_id,remark);
        if (not isEnabled):
            self.setRecordStatus(_id,record_id,False);
        return returnVal;


    def updateRecord(self,_id,record_id,sub_domain,record_type,ip,record_line='default',remark='',isEnabled=True):
        method = "/Record.Modify";
        params = {'domain_id':_id,'record_id':record_id,'sub_domain':sub_domain,'record_type':record_type,'record_line':record_line,'value':ip};
        result = self.apiRequest(method,params);
        returnVal = self.verifyOutput(self.__LANG[method],result);
        if (remark != ''):
            self.setRecordRemark(_id,record_id,remark);
        if (not isEnabled):
            self.setRecordStatus(_id,record_id,False);
        return returnVal;
