import logging
import requests
import configparser
from kalliope.core.NeuronModule import NeuronModule, MissingParameterException
import pathlib

logging.basicConfig()
logger = logging.getLogger("kalliope")

class Sony_command(NeuronModule):
    
    def __init__(self, **kwargs):
        super(Sony_command, self).__init__(**kwargs)        
        
        # Get parameters
        self.type   = kwargs.get('type',None)
        self.action = kwargs.get('action', None)
        self.repeat = kwargs.get('repeat', None)
        self.method = kwargs.get('method', None)
        self.params = kwargs.get('params', None)
        self.app = kwargs.get('app', None)
        
        # read configuration file        
        cfgFilePath = pathlib.Path(__file__).parent.absolute()/'config.cfg'
        self.cfg = configparser.ConfigParser()
        
        try:
            self.cfg.read(cfgFilePath)
              
        except Exception as e :
            print(str(e))
        try:
            IP = self.cfg.get('Login', 'IP')
            KEY = self.cfg.get('Login', 'KEY')
            if self.type == 'IRCC':
                CODE = self.cfg.get('IRCC', (self.action))

        except Exception as e :
            print(str(e),' could not read configuration file')
        
        
       #check if parameters have been provided            
        self.rep = self.Is_repeat_ok (self.repeat)
        
        ok = self.Is_parameters_ok(IP,KEY)
        if ok:
            pass
        else:
            print ("missing parameter")
            
        ############## 
        # Define url #
        ##############

        url=('http://'+str(IP)+'/sony/'+str(self.type))
 
        # Select API Type - IRCC or REST API 
        if self.type == "IRCC":
            r = self.Ircc(KEY,CODE)
            headers = r[0]
            data = r[1]
            self.Request(url, data, headers, self.rep)
        else:
            r = self.Rest(KEY,self.method,self.params)
            headers = r[0]
            data = r[1]
            self.Request(url, data, headers, self.rep)
            
    #################### 
    # IRCC-IP commands #
    ####################        
            
    def Ircc(self,KEY,CODE):
        
        # builds header         
        head = {'SOAPACTION': '"urn:schemas-sony-com:service:IRCC:1#X_SendIRCC"','Accept': '*/*',
                'X-Auth-PSK': str(KEY)}
        
        # builds data according to the parameters  
        dat="""        
<s:Envelope s:encodingStyle='http://schemas.xmlsoap.org/soap/encoding/' xmlns:s='http://schemas.xmlsoap.org/soap/envelope/'>

    <s:Body>
        <u:X_SendIRCC xmlns:u="urn:schemas-sony-com:service:IRCC:1">
            <IRCCCode>"""
        dat +=str(CODE)
        dat +="""</IRCCCode>
        </u:X_SendIRCC>
    </s:Body>
</s:Envelope>
""" 
        return head,dat

    ##################### 
    # REST-API commands #
    #####################
    def Rest(self,KEY,method,params):

        # builds header 
        head = {'content-type': 'application/json','X-Auth-PSK': str(KEY)}
        print("self.app= ",self.app)
        # builds data according to the parameters        
        dat='{"method": "'
        dat +=self.method
        
        if self.method == "getApplicationList" or self.method =="getRemoteControllerInfo":
            dat +='","id":55,"params":'
        else:    
            dat +='","id":55,"params": [{'
            
        if self.app is not None:
            Uri = self.cfg.get('Apps', self.app)
            print("Uri= ",Uri)
            dat +='"uri": "'+ Uri +'"'
        else:    
            dat +=self.params
        
        if self.method == "getApplicationList" or self.method =="getRemoteControllerInfo":
            dat +=','
        else:
            dat +='}],'
        if self.method == "setAudioVolume":
            dat +='"version" : "1.2"}'
        else:
            dat +='"version" : "1.0"}'
        print("Data= ",dat)
        return head,dat

    #   execute the request

    def Request(self, url, data, headers, repeat):

        try:
     # execute the request the number of times specified in repeat       
            for i in range(1,int(repeat)+1):
                requests.post(url,data=data,headers=headers)
                
                if self.method == "getApplicationList":
                    
                # present the Application list in a more readable way
                    content = requests.post(url,data=data,headers=headers)
                    result=content.text
                    result = result.replace('"result":[[{','')
                    result = result.replace('{','')
                    result = result.replace('}','')
                    result = result.replace(']]"id":55','')

                    result = result.replace(',','\n')

                    print(result)
                    
                if self.method == "getRemoteControllerInfo":
                    
                # present the Command list in a more readable way    
                    content = requests.post(url,data=data,headers=headers)
                    result = content.text                    
                    result = result.replace('{"result":[{"bundled":true,"type":"IR_REMOTE_BUNDLE_TYPE_AEP"},[','')
                    result = result.replace('{','')
                    result = result.replace('}','')
                    result = result.replace(']]"id":55','')
                    result = result.replace(',','\n')
                    
                    print("RESULT= ",result)
        except Exception as e :
            print(str(e))     

#          Check if received parameters are ok to perform operations in the neuron
#          , raise an exception otherwise
#          .. raises:: MissingParameterException


    def Is_parameters_ok(self,IP,KEY):
        
        if IP is None:
            raise MissingParameterException("This neuron require an ip")

        if KEY is None:
            raise MissingParameterException("This neuron require a private key")
        else:
            return True
    
    def  Is_repeat_ok (self,repeat):         
        
        if self.repeat is None:
            self.rep=1
            return self.rep
        
        # checks whether "repeat" is in figures or in text.
        # converted to a figure if necessary and sets the maximum value to 9
        
        elif str.isdigit(self.repeat):
            self.rep = self.repeat
            if int(self.rep)>9:
                self.rep = 9
            return self.rep
        else:
            try:   
                self.rep = self.cfg.get('Digit', (self.repeat))
                return self.rep
            except Exception as e :
                print(str(e))
