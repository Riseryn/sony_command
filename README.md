# Sony_command neuron
A neuron for Kalliope

Neuron to control a Sony Bravia Pro monitor from Kalliope.
This neuron was written for the FW-xxBZ35F series,
It should also work for Sony Bravia Android Tvs.
This neuron use 2 api :

The IRCC-IP which send via network command from the infrared remote controller.

The REST API.

The two share commands but some commands are more convenient to use with Kalliope using the Rest API,

## Installation
``kalliope install –-git-url https://github.com/Riseryn/sony_command.git``


## Options
<table>
    <tr>
        <td>Parameters</td>
        <td>Default</td>
         <td>Value</td>
         <td>Comments</td>
    </tr>
        <td>type</td>
        <td>none</td>
        <td>string</td>
        <td>The type of the command. Used in url builds</td>
   </tr>
   <tr> 
        <td>action</td>
        <td>none</td>
        <td>string</td>
        <td>The action to do</td>
   </tr>
   <tr> 
        <td>repeat</td>
        <td>1</td>
        <td>integer</td>
        <td>Number of time to repeat action (1-9). Used for direction command (right,left,up,down)</td>
   </tr>
    <tr> 
        <td>method</td>
        <td>none</td>
        <td>string</td>
        <td>The method to use</td>
   </tr>
   <tr> 
        <td>params</td>
        <td>none</td>
        <td>string</td>
        <td>Parameters of the command. See below for more informations.</td>
   </tr>
    <tr> 
        <td>app</td>
        <td>none</td>
        <td>string</td>
        <td>The application to open. See below for more informations.</td>
   </tr>
   <tr> 
        <td>IP</td>
        <td>none</td>
        <td>Integer</td>
        <td>The IP of your monitor</td>
   </tr>
   <tr> 
        <td>KEY</td>
        <td>none</td>
        <td>string</td>
        <td>The pre shared key</td>
   </tr>
   <tr> 
        <td>CODE</td>
        <td>none</td>
        <td>string</td>
        <td>Ircc code</td>
   </tr>   
</table>

For more informations see the Sony pro [documentation](https://pro-bravia.sony.net/develop/).
## Return values
No values are returned to be catched by the say_template attribute. 
## Synapses example 
This synapses use the REST API


    - name: "set-tv-volume"
        signals:
          - order: 
              text: "set the volume to {{ volume }}"
        neurons:
            - sony_command:
               type: "audio"
               method: "setAudioVolume"
               volume: "+{{ volume }}"
               ui : "on"
               target: "speaker"
         

    - name: "tv-mute-on"
        signals:
          - order: "coupe le son"
        neurons:
            - sony_command:
               type: "audio"
               method: "setAudioMute"
               params: '"status": true'
           
           
This synapses use the IRCC-IP API

    - name: "tv-pause-on/off"
        signals:
          - order: "pause tv"              
        neurons:
          - sony_command:
               type: "IRCC"
               action: "pause"


    - name: "tv-ChannelUp"
        signals:
          - order: "next channel"      
        neurons:
          - sony_command:
               type: "IRCC"
               action: "ChannelUp"
      
 You will find a more complete list of command in the sonycommand.yml file
 
# What can I do?
You can do everything possible with your remote controller.

# How to use this neuron
first, you need to edit the config.cfg file.
You will find four sections:
* Login
* IRCC
* Digit
* Apps

## Login
In this section you must set your monitor IP and the pre-shared KEY.
Read the Sony [documentation](https://pro-bravia.sony.net/develop/integrate/ip-control/index.html#ip-control-authentication) about 
IP Control Authentication.

## IRCC
This section contains the most common infrared codes for the remote control.
You can add codes using the following synapse:

    - name: "tv-command-list"
        signals:
          - order: "get command list"
        neurons:
          - sony_command:
               type: "system"
               method: "getRemoteControllerInfo"
               params: "[]"

This synapse will display commands in the following format in the terminal list:

    "name":"Help"
    "value":"AAAAAgAAAMQAAABNAw=="
    
Add in the IRCC section:

    Help = AAAAAgAAAMQAAABNAw==
    
That's all.
See above for an example of synapse with the IRCC API.

## Digit
sometimes the STT engine will display "one" or "1" when you say, for example, right 1 time. This section takes care of this and avoids having to add an STT correction manually in the synapse.
for french it must be "une" or "1".



## Apps
To add an application to be controlled by Kalliope use the following synapse:

    - name: "tv-app-list"
        signals:
          - order: "get application list"
        neurons:
          - sony_command:
               type: "appControl"
               method: "getApplicationList"
               params: "[]"

This synapse will display applications installed in the following format in the terminal list:

    RESULT=  "title":"Play Store"
    "uri":"com.sony.dtv.com.android.vending.com.google.android.finsky.tvmainactivity.TvMainActivity"
    "icon":"http:\/\/192.168.1.10\/DIAL\/icon\/com.sony.dtv.com.android.vending.com.google.android.finsky.tvmainactivity.TvMainActivity.png"
    
To add the Play Store application, add the following line in the Apps section:

    Play Store = com.sony.dtv.com.android.vending.com.google.android.finsky.tvmainactivity.TvMainActivity
       
That's all

to open an application, use the synapse

    - name: "open-playstore-app"
        signals:
            - order: "open play store"
        neurons:      
            - sony_command:
               type: "appControl"
               method: "setActiveApp"
               app: "Play Store"
               
__Attention__

If you are not on the home page and you launch an application while another is running, you will have both applications open simultaneously which can cause a nice cacophony.
# Known issue
If you also use the neuron for kodi, it is necessary to modify the "execute" method of the "KodiJsonTransport" class usually in /usr/local/lib/python3.7/dist-packages/kodijson/kodijson.py
to modify the header.
look for:

def execute(self, method, *args, **kwargs):
        """Execute given method with given arguments."""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'python-kodi',
         }
         
and change for:

def execute(self, method, *args, **kwargs):
        """Execute given method with given arguments."""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'python-kodi',
            'X-Auth-PSK' : 'nora_tv_control_724'
        }        
