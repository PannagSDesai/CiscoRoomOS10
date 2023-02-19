# -*- coding: utf-8 -*-
"""
Created on Sun Jul  3 18:43:51 2022

@author: panna
"""

import requests
from requests.auth import HTTPBasicAuth
import jxmlease
import time
import typing
from datetime import datetime, timezone
from functools import wraps

class Cisco_RoomOS:
    """
    This is Cisco Room OS 10 SDK which adds abstraction to the xAPI allowing devlopers-administrators to use most xAPI functions with Python
    without having to worry about parsing the results.
    
    Usage: import the library , create an object with parameters in order: IP address, username and password.
    Use this object to access functions as per the requirement.
    """
    __PACUrl_flag=0
    __man_flag=0
    
    @staticmethod
    def all_methods():
        return [method for method in dir(Cisco_RoomOS) if callable(getattr(Cisco_RoomOS,method))]
    
    
    def __init__(self,address : str ,username : str ,password :str ,ssl_verify: str = False):
        self.address:str = address
        self.username:str = username
        self.password:str = password
        self.ssl_verify:bool = ssl_verify
        
    def get_device_status(self,return_type : str = "json"):
        """Description: Get full device status
        Usage: Run the function that returns data by default in json format, but can be requested in XML by specifying "xml" in argument."""
        
        url = f"http://{self.address}/status.xml"
        
        try:
            response = requests.get(url, auth = HTTPBasicAuth(self.username,self.password), verify=self.ssl_verify)
            
            if (response.status_code==401):
                raise Exception("Authorisation Failed , Please check Credentials\n")
            elif (response.status_code==400):
                raise Exception("Connection Failed , Please check Connection\n")
            elif (response.status_code==200):
                #response_data = self.__return_type_parser(response,return_type = "json")
                response_data = jxmlease.parse(response.text)
                Name = response_data['Status']['UserInterface']['ContactInfo']['Name']
                return response_data
            else:
                raise Exception("Unknown Exception\n") 
           
        except Exception as e:
            return(e)
        
    
    def get_device_backup(self):
        """Description: Get device configuration backup
        Usage: Call the function that returns the data in XML format file located in specified optional path with device name as file name"""
        
        url = f'http://{self.address}/configuration.xml'
        try: 
            configuration = requests.get(url, auth = HTTPBasicAuth(self.username,self.password), verify=self.ssl_verify)
            if (configuration.status_code==401):
                    raise Exception("Authorisation Failed , Please check Credentials\n")
            elif (configuration.status_code==400):
                    raise Exception("Connection Failed , Please check Connection\n")
            elif (configuration.status_code==200):
                device_name = jxmlease.parse(configuration.text)['Configuration']['SystemUnit']['Name']
                with open(f"{device_name}.xml","w") as f:
                    f.write(configuration.text)
                f.close()
            else:
                raise Exception("Unknown Exception\n") 
        except Exception as e:
            return(e)
            
        
    def get_device_video_config(self,output_debug : bool =False):
        """Description: get device video configuration
        Usage: call the function that returns data in XML structure"""
        
        url = f'http://{self.address}/getxml?location=/Configuration/Video'
        try:
            configuration = requests.get(url, auth = HTTPBasicAuth(self.username,self.password), verify=self.ssl_verify)
            if (configuration.status_code==401):
                    raise Exception("Authorisation Failed , Please check Credentials\n")
            elif (configuration.status_code==400):
                    raise Exception("Connection Failed , Please check Connection\n")
            elif (configuration.status_code==200):
                if output_debug:
                    print(configuration.text)
                return(configuration.text)
                #device_name = jxmlease.parse(configuration.text)['Configuration']['SystemUnit']['Name']
                """with open(f"{device_name}_video_config.xml","w") as f:
                    f.write(configuration.text)
                f.close()"""
            else:
                raise Exception("Unknown Exception\n") 
        except Exception as e:
            if output_debug:
                print(e)
            return(e)
            
    def get_audio_status(self,output_debug : bool = False):
        """Description: Get audio status
        Usage : call the function which returns data in XML structure"""

        url = f'http://{self.address}/getxml?location=/Status/Audio'
        try:
            audio_status = requests.get(url, auth = HTTPBasicAuth(self.username,self.password), verify=self.ssl_verify)
            if (audio_status.status_code==401):
                    raise Exception("Authorisation Failed , Please check Credentials\n")
            elif (audio_status.status_code==400):
                    raise Exception("Connection Failed , Please check Connection\n")
            elif (audio_status.status_code==200):
                if output_debug:
                    print(audio_status.text)
                return(audio_status.text)
        except Exception as e:
            if output_debug:
                print(e)
            return(e)
        
    def _get_status_helper(func):
        """Helper function to process requests and its response output for all status functions"""
        @wraps(func)
        def inner(self,*n):
            url = func(self,*n)
            headers = {
              'Content-Type': 'text/xml',
            }
            try:
                response_connect = requests.request("GET", url, headers=headers,auth=HTTPBasicAuth(username=self.username,password=self.password),verify=self.ssl_verify)
                if (response_connect.status_code==401):
                        raise Exception("Authorisation Failed , Please check Credentials\n")
                elif (response_connect.status_code==400):
                        raise Exception("Connection Failed , Please check Connection\n")
                elif (response_connect.status_code==200):
                    call = jxmlease.parse(response_connect.text)
                    return(call)
            except Exception as e:
                return(e)
        return inner
            
    @_get_status_helper
    def get_status_audio_input_connectors(self):
        """Description: Get the Audio input connectors Status 
        Usage: Requires user role: ADMIN, USER"""
        
        url = f'http://{self.address}/getxml?location=/Status/Audio/Input/Connectors'
        return url
    
    @_get_status_helper
    def get_status_audio_input_usbc_mute(self,n:int):
        """Description: Shows whether the audio channel on a USB-C input connector is muted or not.
        Usage: Supply Channel number : n while calling the function, Requires user role: ADMIN, USER
        Output: On/Off -> Mute"""
        
        url = f'http://{self.address}/getxml?location=/Status/Audio/Input/Connectors/USBC/{n}/Mute'
        return url
    
    @_get_status_helper
    def get_status_audio_input_microphone_mute(self):
        """Description: Shows whether the audio on a Microphone input connector is muted or not
        Usage: Requires user role: ADMIN, USER
        output: On/Off -> Mute"""
        
        url = f'http://{self.address}/getxml?location=/Status/Audio/Input/Connectors/Microphone/Mute'
        return url
    
    @_get_status_helper
    def get_status_audio_input_keyclick_attenuate(self):
        """Description: Shows whether the device is automatically attenuating clicking noises, such as those detected 
        microphone signals caused by the typing of a keyboard.
        Usage: Requires user role: ADMIN, USER
        Output: False/True
        True: The attenuation of the microphone signal is turned on.
        False: The attenuation of the microphone signal is turned off"""
        
        url = f'http://{self.address}/getxml?location=/Status/Audio/Input/KeyClick/Attenuate'
        return url
    
    @_get_status_helper
    def get_status_audio_mic_music_mode(self):
        """Description: Shows whether MusicMode is on or off.
        Usage: Requires user role: ADMIN, USER
        Output: On/Off -> MusicMode"""
        
        url = f'http://{self.address}/getxml?location=/Status/Audio/Microphones/MusicMode'
        return url
    
    @_get_status_helper
    def get_status_audio_mic_muted(self):
        """Description: Shows whether the microphones are muted.
        Usage: Requires user role: ADMIN, USER
        Output: On/Off -> Mute"""
        
        url = f'http://{self.address}/getxml?location=/Status/Audio/Microphones/Mute'
        return url
    
    @_get_status_helper
    def get_status_audio_output_measured_hdmiarcDelay(self):
        """Description: Shows the measured audio delay of the device connected to the HDMI connector. This delay 
        is measured through the HDMI audio return channel, and will secure good lip-synchronization 
        between audio and video.
        Usage: Requires user role: ADMIN, USER
        Output: Integer -> The measured audio delay in milliseconds"""
        
        url = f'http://{self.address}/getxml?location=/Status/Audio/Output/MeasuredHdmiArcDelay'
        return url
    
    @_get_status_helper
    def get_status_audio_output_measured_hdmicecDelay(self):
        """Description: Shows the reported video delay of the device connected to the HDMI connector. This delay 
        is reported through the consumer electronics control (CEC) protocol, and will secure good 
        lip-synchronization between audio and video. 
        Usage: Requires user role: ADMIN, USER
        Output: Integer -> The measured audio delay in milliseconds"""
        
        url = f'http://{self.address}/getxml?location=/Status/Audio/Output/MeasuredHdmiCecDelay'
        return url
    
    @_get_status_helper
    def get_status_audio_volume_mute(self):
        """Description: Shows whether the device volume is set to mute.
        Usage: Requires user role: ADMIN, USER
        Output: On/Off -> MusicMode"""
        
        url = f'http://{self.address}/getxml?location=/Status/Audio/VolumeMute'
        return url
    
    @_get_status_helper
    def get_status_bookings_currentId(self):
        """Description: The ID of the on going booking event, if any. 
        Usage: Requires user role: ADMIN, USER
        Output: String -> Booking ID"""
        
        url = f'http://{self.address}/getxml?location=/Status/Bookings/Current/Id'
        return url
    
    @_get_status_helper
    def get_status_call_answered(self,n:int):
        """Description: Indicates if a call is answered, ignored or has been automatically answered by a device.
        Usage: Supply the nth call you want to check, Requires user role: ADMIN, USER
        Output: Unanswered/Ignored/Autoanswered/Answered -> Answer State of nth call"""
        
        url = f'http://{self.address}/getxml?location=/Status/Call/{n}/AnswerState'
        return url
    
    @_get_status_helper
    def get_status_call_answered_transferredFrom(self,n:int):
        """Description: Shows the CallId for the call the current call was transferred from.
        Usage: Supply the nth call you want to check, Requires user role: ADMIN, USER
        Output: Integer -> caller id of nth transferred call"""
        
        url = f'http://{self.address}/getxml?location=/Status/Call/{n}/AttendedTransferFrom'
        return url
    
    @_get_status_helper
    def get_status_call_callbackNumber(self,n:int):
        """Description: Shows the remote (far end) number or URI of an incoming or outgoing call, including the call 
        protocol, for call back.
        Usage: Supply the nth call you want to check, Requires user role: ADMIN, USER
        Output: String -> Call back number/uri"""
        
        url = f'http://{self.address}/getxml?location=/Status/Call/{n}/CallbackNumber'
        return url
    
    @_get_status_helper
    def get_status_call_callType(self,n:int):
        """Description: Shows the call type of the incoming or outgoing call.
        Usage: Supply the nth call you want to check, Requires user role: ADMIN, USER
        Output: Video/Audio/AudioCanEscalate/ForwardAllCall/Unknown
        """
        
        url = f'http://{self.address}/getxml?location=/Status/Call/{n}/CallType'
        return url
    
    @_get_status_helper
    def get_status_call_deviceType(self,n:int):
        """Description: Shows where the call is connected to.
        Usage: Supply the nth call you want to check, Requires user role: ADMIN, USER
        Output: Endpoint/MCU 
        Endpoint: It is a point-to-point call to another device.
        MCU: The call is to a multipoint conferencing unit (MCU) in the network, or a MultiSite call hosted on a device.
        """
        
        url = f'http://{self.address}/getxml?location=/Status/Call/{n}/DeviceType'
        return url
    
    @_get_status_helper
    def get_status_call_direction(self,n:int):
       """Description: States the direction of the call initiation.
       Usage: Supply the nth call you want to check, Requires user role: ADMIN, USER
       Output: Incoming/Outgoing
       """
       url = f'http://{self.address}/getxml?location=/Status/Call/{n}/Direction'
       return url
   
    @_get_status_helper
    def get_status_call_displayName(self,n:int):
       """Description: Shows the name of the remote (far end) participant in an incoming or outgoing call.
       Usage: Supply the nth call you want to check, Requires user role: ADMIN, USER
       Output: String
       """
       url = f'http://{self.address}/getxml?location=/Status/Call/{n}/DisplayName'
       return url   
   
    @_get_status_helper
    def get_status_call_encryptionType(self,n:int):
       """Description: Shows the encryption type of the call.
       Usage: Supply the nth call you want to check, Requires user role: ADMIN, USER
       Output: None/Aes-128
       """
       url = f'http://{self.address}/getxml?location=/Status/Call/{n}/Encryption/Type'
       return url
    
    @_get_status_helper
    def get_status_call_duration(self,n:int):
       """Description:Shows the duration of a call (in seconds).
       Usage: Supply the nth call you want to check, Requires user role: ADMIN, USER
       Output: Integer
       """
       url = f'http://{self.address}/getxml?location=/Status/Call/{n}/Duration'
       return url
   
    @_get_status_helper
    def get_status_call_facilityServiceId(self,n:int):
       """Description: When calling a facility service, the facility service id is shown. Otherwise the value 0 is returned.
       Usage: Supply the nth call you want to check, Requires user role: ADMIN, USER
       Output: Integer 0..5
       """
       url = f'http://{self.address}/getxml?location=/Status/Call/{n}/FacilityServiceId'
       return url
   
    @_get_status_helper
    def get_status_call_holdReason(self,n:int):
       """Description: Shows the reason the current outgoing call was put on hold.
       Usage: Supply the nth call you want to check, Requires user role: ADMIN, USER
       Output:Conference/Transfer/None
       Conference: On hold while the call is being merged into a conference. 
       Transfer: On hold while the call is being transferred. 
       None: All other instances.
       """
       url = f'http://{self.address}/getxml?location=/Status/Call/{n}/HoldReason'
       return url
     
    @_get_status_helper
    def get_status_call_placedOnHold(self,n:int):
       """Description: Shows the placed on hold status of the call.
       Usage: Supply the nth call you want to check, Requires user role: ADMIN, USER
       Output: True/False
       """
       url = f'http://{self.address}/getxml?location=/Status/Call/{n}/PlacedOnHold'
       return url
   
    @_get_status_helper
    def get_status_call_ice(self,n:int):
       """Description: ICE is a feature that enables two sides of a call to send media (video and audio) directly 
       between each other, if a direct network path has been found through ICE negotiation. This 
       status reflects the result of that negotiation.
       Usage: Supply the nth call you want to check, Requires user role: ADMIN, USER
       Output: Disabled/Passed/Failed
       Disabled: ICE is disabled.
       Passed: A direct network path was found and is being used.
       Failed: A direct network path was not found, and media will most likely flow through an 
       intermediary component
       """
       url = f'http://{self.address}/getxml?location=/Status/Call/{n}/Ice'
       return url
   
    @_get_status_helper
    def get_status_callProtocol(self,n:int):
       """Description: Shows the call protocol of the incoming or outgoing call.
       Usage: Supply the nth call you want to check, Requires user role: ADMIN, USER
       Output: H320/H323/SIP/Spark/Unknown/WebRTC
       """
       url = f'http://{self.address}/getxml?location=/Status/Call/{n}/Protocol'
       return url
   
    @_get_status_helper
    def get_status_call_receiveRate(self,n:int):
       """Description: Shows the receive bandwidth in the call in kilobits per second (kbps).
       Usage: Supply the nth call you want to check, Requires user role: ADMIN, USER
       Output: Integer
       """
       url = f'http://{self.address}/getxml?location=/Status/Call/{n}/ReceiveCallRate'
       return url
   
    @_get_status_helper
    def get_status_call_remoteNumber(self,n:int):
       """Description: Shows the remote (far end) number or URI of an incoming or outgoing call.
       Usage: Supply the nth call you want to check, Requires user role: ADMIN, USER
       Output: String
       """
       url = f'http://{self.address}/getxml?location=/Status/Call/{n}/RemoteNumber'
       return url
   
    @_get_status_helper
    def get_status_call_transmitRate(self,n:int):
       """Description: Shows the transmit bandwidth in the call in kilobits per second (kbps).
       Usage: Supply the nth call you want to check, Requires user role: ADMIN, USER
       Output: Integer
       """
       url = f'http://{self.address}/getxml?location=/Status/Call/{n}/TransmitCallRate'
       return url
   
    @_get_status_helper
    def get_status_call_status(self,n:int):
       """Description: Shows the status of a call. 
       Usage: Supply the nth call you want to check, Requires user role: ADMIN, USER
       Output: Idle/Dialling/Ringing/Connecting/Connected/Disconnecting/OnHold/EarlyMedia/Preserved/RemotePreserved
       """
       url = f'http://{self.address}/getxml?location=/Status/Call/{n}/Status'
       return url
   
    @_get_status_helper
    def get_status_camera_capabilities(self,n:int):
       """Description: Shows the camera capabilities (ptzf = pan, tilt, zoom, focus).
       Usage: Supply the nth camera you want to check, Requires user role: ADMIN, INTEGRATOR, USER, ROOMCONTROL
       Output: String
       """
       url = f'http://{self.address}/getxml?location=/Status/Cameras/Camera/{n}/Capabilities/Options'
       return url
    
    @_get_status_helper
    def get_status_camera_connected(self,n:int):
       """Description: Shows if the camera is connected or not.
       Usage: Supply the nth camera you want to check, Requires user role: ADMIN, INTEGRATOR, USER, ROOMCONTROL
       Output: True/False
       """
       url = f'http://{self.address}/getxml?location=/Status/Cameras/Camera/{n}/Connected'
       return url
   
    @_get_status_helper
    def get_status_camera_lightingConditions(self,n:int):
       """Description: Shows if the camera is connected or not.
       Usage: Supply the nth camera you want to check, Requires user role: ADMIN, INTEGRATOR, USER, ROOMCONTROL
       Output: Unknown/Good/Dark/Backlight
       Unknown: The camera is turned off or does not support this functionality.
       Good: The lighting is at a good level.
       Dark: The lighting is too low. 
       Backlight: There is a high level of backlight in the image.
       """
       url = f'http://{self.address}/getxml?location=/Status/Cameras/Camera/{n}/LightingConditions'
       return url
   
    @_get_status_helper
    def get_status_camera_manufacturer(self,n:int):
       """Description: Shows the manufacturer of the camera.
       Usage: Supply the nth camera you want to check, Requires user role: ADMIN, INTEGRATOR, USER, ROOMCONTROL
       Output: String
       """
       url = f'http://{self.address}/getxml?location=/Status/Cameras/Camera/{n}/Manufacturer'
       return url
   
    @_get_status_helper
    def get_status_camera_model(self,n:int):
       """Description: Shows the camera model.
       Usage: Supply the nth camera you want to check, Requires user role: ADMIN, INTEGRATOR, USER, ROOMCONTROL
       Output: String
       """
       url = f'http://{self.address}/getxml?location=/Status/Cameras/Camera/{n}/Model'
       return url
   
    
    @_get_status_helper
    def get_status_camera_positionPan(self,n:int):
       """Description: Shows the current pan (move left and right) position of the camera. The value range depends on camera type.
       Usage: Supply the nth camera you want to check, Requires user role: ADMIN, INTEGRATOR, USER, ROOMCONTROL
       Output: -10000..10000
       """
       url = f'http://{self.address}/getxml?location=/Status/Cameras/Camera/{n}/Position/Pan'
       return url
   
    @_get_status_helper
    def get_status_camera_positionTilt(self,n:int):
       """Description: Shows the current tilt (move up and down) position of the camera. The value range depends on camera type.
       Usage: Supply the nth camera you want to check, Requires user role: ADMIN, INTEGRATOR, USER, ROOMCONTROL
       Output: -2500..2500
       """
       
       url = f'http://{self.address}/getxml?location=/Status/Cameras/Camera/{n}/Position/Tilts'
       return url
     
        
    @_get_status_helper
    def get_status_camera_positionZoom(self,n:int):
       """Description: Shows the current zoom (zoom in and out) position of the camera. The value range depends on camera type.
       Usage: Supply the nth camera you want to check, Requires user role: ADMIN, INTEGRATOR, USER, ROOMCONTROL
       Output: 0..11800
       """
       
       url = f'http://{self.address}/getxml?location=/Status/Cameras/Camera/{n}/Position/Zoom'
       return url
   
    @_get_status_helper
    def get_status_speakerTrack_activeConnector(self):
       """Description: Shows the number of the connector that a camera with speaker tracking support is connected 
       to. If it is a SpeakerTrack 60 camera, it is the connector number for the camera that is currently 
       chosen by the SpeakerTrack algorithm.
       This status is not applicable for Room Kit Mini, Desk Pro, Desk Limited Edition, or Boards.
       Usage: Requires user role: ADMIN, INTEGRATOR, USER, ROOMCONTROL
       Output: Integer
       """
       
       url = f'http://{self.address}/getxml?location=/Status/Cameras/SpeakerTrack/ActiveConnector'
       return url
   
    @_get_status_helper
    def get_status_speakerTrack_availability(self):
        """Description: The product may support speaker tracking (which also includes best overview), or only the best 
        overview feature. This status shows whether or not that feature is available.
        Usage:Requires user role: ADMIN, INTEGRATOR, USER, ROOMCONTROL 
        Output: Off/Unavailable/Available
        Off: Speaker tracking / best overview is turned off with the command xConfiguration 
        Cameras SpeakerTrack Mode: Off
        Unavailable: Hardware for speaker tracking / best overview is not found. 
        Available: Hardware for speaker tracking / best overview is found, and it is possible to 
        turn the feature on or off from the user interface"""
        
        url = f'http://{self.address}/getxml?location=/Status/Cameras/SpeakerTrack/Availability'
        return url
    
    @_get_status_helper
    def get_status_speakerTrack_status(self):
        """Description: The product may support speaker tracking (which also includes best overview), or only the best 
        overview feature. This status shows whether or not that feature is active
        Usage:Requires user role: ADMIN, INTEGRATOR, USER, ROOMCONTROL 
        Output: Active/Inactive
        Active: Speaker tracking / best overview is active.
        Inactive: Speaker tracking / best overview is inactive."""
        
        url = f'http://{self.address}/getxml?location=/Status/Cameras/SpeakerTrack/Status'
        return url

    
    @_get_status_helper
    def get_status_capabilities_maxActiveCalls(self):
        """Description:Shows the maximum number of simultaneous active calls. Calls that are set on hold/transfer are not counted as active.
        Usage:Requires user role: ADMIN, USER. 
        Output:0..5
        """
        
        url = f'http://{self.address}/getxml?location=/Status/Capabilities/Conference/MaxActiveCalls'
        return url
    
    @_get_status_helper
    def get_status_capabilities_maxAudioCalls(self):
        """Description:Shows the maximum number of simultaneous audio calls that is supported.
        Usage:Requires user role: ADMIN, USER.
        Output:Integer
        """
        
        url = f'http://{self.address}/getxml?location=/Status/Capabilities/Conference/MaxAudioCalls'
        return url
    
    @_get_status_helper
    def get_status_capabilities_maxVideoCalls(self):
        """Description:Shows the maximum number of simultaneous video calls that is supported.
        Usage:Requires user role: ADMIN, USER.
        Output:Integer
        """
        
        url = f'http://{self.address}/getxml?location=/Status/Capabilities/Conference/MaxVideoCalls'
        return url
    
    @_get_status_helper
    def get_status_capabilities_maxCalls(self):
        """Description:Shows the maximum number of simultaneous calls.
        Usage: Requires user role: ADMIN, USER.
        Output:0..5
        """
        
        url = f'http://{self.address}/getxml?location=/Status/Capabilities/Conference/MaxCalls'
        return url
    
    @_get_status_helper
    def get_status_conference_activeSpeaker_callId(self):
        """Description:Shows the CallId of the current active speaker.
        Usage:Requires user role: ADMIN, USER
        Output: Integer
        """
        
        url = f'http://{self.address}/getxml?location=/Status/Conference/ActiveSpeaker/CallId'
        return url
    
    @_get_status_helper
    def get_status_conferenece_authRequest(self,n:int):
        """Description:This status is only relevant for Cisco Webex registered devices. When this status has another 
        value than "None" the device is waiting for an authentication response. Use the Conference 
        Call AuthenticationResponse command to give the response.
        Usage: Supply nth call where n is an integer,Requires user role: ADMIN, INTEGRATOR, USER
        Output: None/HostPinOrGuest/HostPinOrGuestPin/PanelistPin
        None: The device is not waiting for an authentication response (no authentication 
        request).
        HostPinOrGuest: You must either provide a host PIN, or join as a Guest without PIN.
        HostPinOrGuestPin: You must either provide a host PIN or a guest PIN.
        PanelistPin: You must provide a Panelist PIN for joining an Event Center event as panelist.
        """
        
        url = f'http://{self.address}/getxml?location=/Status/Conference/Call/{n}/AuthenticationRequest'
        return url
    
    @_get_status_helper
    def get_status_conferenece_bookingId(self,n:int):
        """Description:Shows the booking ID of a conference (if assigned). The booking ID can be used for easy 
        identification of a call or conference.
        Usage: Supply nth call where n is an integer,Requires user role: ADMIN, USER
        Output: String : Booking ID
        """
        
        url = f'http://{self.address}/getxml?location=/Status/Conference/Call/{n}/BookingId'
        return url
    
    
    @_get_status_helper
    def get_status_fecc_presetsNumber(self,n:int):
        """Description: Shows the number of presets available for the input sources at a far end site.
        Usage: Supply nth call where n is an integer,Requires user role: ADMIN, USER
        Output: 1..15 : Denoting the number of presets.
        """
        
        url = f'http://{self.address}/getxml?location=/Status/Conference/Call/{n}/Capabilities/FECC/NumberOfPresets'
        return url
    
    @_get_status_helper
    def get_status_fecc_mode(self,n:int):
        """Description: Shows whether or not you have permission to control the input sources at a far end site.
        Usage: Supply nth call where n is an integer,Requires user role: ADMIN, USER
        Output: On/Off
        On: Far end input source control is permitted.
        Off: Far end input source control is not permitted
        """
        
        url = f'http://{self.address}/getxml?location=/Status/Conference/Call/{n}/Capabilities/FECC/Mode'
        return url
    
    @_get_status_helper
    def get_status_fecc_inputSource_name(self,n:int,i:int):
        """Description: Shows the name of an input source that can be connected at a far end site.
        Usage: Supply nth call and ith source where n and i are integers, Requires user role: ADMIN, USER
        Output: String : Denoting the name of the selected input source.
        """
        
        url = f'http://{self.address}/getxml?location=/Status/Conference/Call/{n}/Capabilities/FECC/Source/{i}/Name'
        return url
    
    
    @_get_status_helper
    def get_status_fecc_inputSource_ID(self,n:int,i:int):
        """Description: Shows the ID of an input source that can be connected at a far end site.
        Usage: Supply nth call and ith source where n and i are integers, Requires user role: ADMIN, USER
        Output: Integer:Denoting the Source ID.
        """
        
        url = f'http://{self.address}/getxml?location=/Status/Conference/Call/{n}/Capabilities/FECC/Source/{i}/SourceId'
        return url
    
    @_get_status_helper
    def get_status_conference_capabilities_hold(self,n:int):
        """Description: Indicates whether the far-end site can be placed on hold or not.
        Usage: Supply nth call where n is an integers, Requires user role: ADMIN, USER
        Output: True/False
        """
        
        url = f'http://{self.address}/getxml?location=/Status/Conference/Call/{n}/Capabilities/Hold/'
        return url
    
    
    @_get_status_helper
    def get_status_conference_DND(self):
        """Description: Shows whether DoNotDisturb mode is switched on or not.
        Usage: Requires user role:  ADMIN, INTEGRATOR, USER
        Output: Active/Inactive."""
        # Did not return, needs to be checked later
        url = f'http://{self.address}/getxml?location=/Status/Conference/DoNotDisturb'
        return url
    
    @_get_status_helper
    def get_status_conference_sipSessionId(self,n:int):
        """Description: Show the SIP SessionId, which is a CUCM identifier used to identify a specific call leg in a meeting.
        Usage:Supply nth call where n is an integers Requires user role:  ADMIN, USER
        Output: String denoting the Session of ID for the supplied nth call."""
        # Did not return, needs to be checked later
        url = f'http://{self.address}/getxml?location=/Status/Conference/Call/{n}/Sip/SessionId'
        return url
    
    @_get_status_helper
    def get_status_fecc_inputSource_Id(self,n:int,i:int):
        """Description: Shows the ID of an input source that can be connected at a far end site.
        Usage: Supply nth call and ith source where n and i are an integers, Requires user role: ADMIN, USER
        Output: Integer:Denoting the Source ID.
        """
        
        url = f'http://{self.address}/getxml?location=/Status/Conference/Call/{n}/Capabilities/FECC/Source/{i}/SourceId'
        return url
    
    @_get_status_helper
    def get_status_fecc_inputSource_Options(self,n:int,i:int):
        """Description: Shows available options for an input source that can be connected at a far end site (for a camera: p=pan; t=tilt; z=zoom; f=focus).
        Usage: Supply nth call and ith source where n and i are integers, Requires user role: ADMIN, USER
        Output: String Denoting options.
        """
        
        url = f'http://{self.address}/getxml?location=/Status/Conference/Call/{n}/Capabilities/FECC/Source/{i}/Options'
        return url
    
    @_get_status_helper
    def get_status_h320_gatewayAddress(self):
        """Description: Returns the IPv4 address of the ISDN Gateway, if the video conferencing device is paired to one.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the gateway address"""
        
        url = f'http://{self.address}/getxml?location=/Status/H320/Gateway/Id'
        return url
    
    @_get_status_helper
    def get_status_h320_gatewayMode(self):
        """Description: Returns information on the type of calls the ISDN Gateway is configured for, if the video conferencing device is paired with an ISDN Link.
        Usage: Requires user role: ADMIN, USER
        Output: BRI/External/G703/PRI/Unknown"""
        
        url = f'http://{self.address}/getxml?location=/Status/H320/Gateway/Mode'
        return url
    
    @_get_status_helper
    def get_status_h320_gatewayNumber(self):
        """Description: Returns the IPv6 address of the ISDN Gateway if the video conferencing device is paired to one.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the IPv6 address"""
        
        url = f'http://{self.address}/getxml?location=/Status/H320/Gateway/Number'
        return url
    
    @_get_status_helper
    def get_status_h320_gatewayReason(self):
        """Description: Shows the reason for rejected Gateway registration. Only available if the video conferencing device is connected to an ISDN Link.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the reason for rejection"""
        
        url = f'http://{self.address}/getxml?location=/Status/H320/Gateway/Reason'
        return url
    
    @_get_status_helper
    def get_status_h320_gatewayStatus(self):
        """Description: Returns the state of the H320 Gateway, if the video conferencing device is paired with an ISDN Link.
        Usage: Requires user role: ADMIN, USER
        Output: Error/Inactive/OK/OKWithWarning/Warning/NoConnection"""
        
        url = f'http://{self.address}/getxml?location=/Status/H320/Gateway/Status'
        return url
    
    @_get_status_helper
    def get_status_h320_gatewayId(self):
        """Description:Returns the unique identification of the H320 Gateway, if the video conferencing device is paired with an ISDN Link
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the Gateway ID"""
        
        url = f'http://{self.address}/getxml?location=/Status/H320/Gateway/Id'
        return url
    
    @_get_status_helper
    def get_status_h323_gatekeeperAddress(self):
        """Description: Displays the IP address of the gatekeeper where the device is registered.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the Gatekeeper IP address"""
        
        url = f'http://{self.address}/getxml?location=/Status/H323/Gatekeeper/Address'
        return url
    
    @_get_status_helper
    def get_status_h323_gatekeeperPort(self):
        """Description: Shows the port which is used when connecting to on the gatekeeper.
        Usage: Requires user role: ADMIN, USER
        Output: Integer denoting the Gatekeeper Port"""
        
        url = f'http://{self.address}/getxml?location=/Status/H323/Gatekeeper/Port'
        return url
    
    @_get_status_helper
    def get_status_h323_gatekeeperRejection(self):
        """Description: Shows the reason for rejected registration.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the Gatekeeper Port"""
        
        url = f'http://{self.address}/getxml?location=/Status/H323/Gatekeeper/Reason'
        return url
    
    @_get_status_helper
    def get_status_h323_gatekeeperRegistration(self):
        """Description: Shows the status for H.323 registration.
        Usage: Requires user role: ADMIN, USER
        Output:Enabled/Disabled
        Enabled: Registration is enabled.
        Disabled: Registration is disable, because SIP is enabled."""
        
        url = f'http://{self.address}/getxml?location=/Status/H323/Gatekeeper/Status'
        return url
    
    
    @_get_status_helper
    def get_status_h323_gatewayMode(self):
        """Description: Shows the status for H.323 registration.
        Usage: Requires user role: ADMIN, USER
        Output:Enabled/Disabled
        Enabled: Registration is enabled.
        Disabled: Registration is disable, because SIP is enabled."""
        
        url = f'http://{self.address}/getxml?location=/Status/H323/Mode/Status'
        return url
    
    @_get_status_helper
    def get_status_h323_gatewayMode_reason(self):
        """Description: Shows whether there is a conflict between H.323 settings and xStatus H323 Mode Status.
        Usage: Requires user role: ADMIN, USER
        Output:String
         “”: When H.323 is set to On and there is no conflict between H.323 Mode configuration 
        and the rest of the device settings.
        "SIP is enabled": When H.323 Mode is set to On and SIP is enabled on a device that does 
        not support the two simultaneously.
        "Not available": When a device does not support H.323."""
        
        url = f'http://{self.address}/getxml?location=/Status/H323/Mode/Reason'
        return url
    
    @_get_status_helper
    def get_status_cdpAddress(self):
        """Description: Describes the functional capability for the switch in form of a device type. See documentation for CDP protocol for more information.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting Hex Value for CDP capabilities. Empty String will be returned if set to nothing."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/CDP/Address'
        return url
    
    @_get_status_helper
    def get_status_cdpCapabilities(self):
        """Description: Returns the first network address of both receiving and sending devices.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting cdp IP address. Empty String will be returned if set to nothing."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/CDP/Capabilities'
        return url
    
    @_get_status_helper
    def get_status_cdpDeviceId(self):
        """Description: Identifies the name of the switch in form of a character string.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting cdp device ID. Empty String will be returned if set to nothing."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/CDP/DeviceId'
        return url
    
    @_get_status_helper
    def get_status_cdpDuplex(self):
        """Description: Indicates the status (duplex configuration) of the CDP broadcast interface. Used by network 
        operators to diagnose connectivity problems between adjacent network elements.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting Duplex Mode. Empty String will be returned if set to nothing."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/CDP/Duplex'
        return url
    
    
    @_get_status_helper
    def get_status_cdpPlatform(self):
        """Description: Returns the hardware platform name of the switch connected to the device.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting Connected device Platform (applicable only for Cisco). Empty String will be returned if set to nothing."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/CDP/Platform'
        return url
    
    @_get_status_helper
    def get_status_cdpManagementIP(self):
        """Description: Returns the management address used to configure and monitor the switch the device is connected to.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting Primary management IP address. Empty String will be returned if set to nothing."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/CDP/PrimaryMgmtAddress'
        return url
    
    @_get_status_helper
    def get_status_cdpSysName(self):
        """Description: Returns the SysName as configured in the switch the device is connected to.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting Connected device's sysname. Empty String will be returned if set to nothing."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/CDP/SysName'
        return url
    
    @_get_status_helper
    def get_status_cdpPortId(self):
        """Description: Returns the identification the switch uses of the port the device is connected to.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting Connected device's Interface or Port ID. Empty String will be returned if set to nothing."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/CDP/PortID'
        return url
    
    @_get_status_helper
    def get_status_cdpVoIPAppliancevlanId(self):
        """Description: Identifies the VLAN used for VoIP traffic from the device to the switch. For more information see documentation of the IEEE 802.1Q protocol.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting VOIP appliance VLAN ID. Empty String will be returned if set to nothing."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/CDP/VoIPApplianceVlanID'
        return url
    
    @_get_status_helper
    def get_status_cdpVersion(self):
        """Description: Returns information about the software release version the switch is running.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting CDP version. Empty String will be returned if set to nothing."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/CDP/Version'
        return url
    
    @_get_status_helper
    def get_status_cdpVTPmanagement(self):
        """Description: Returns the switch's configured VTP management domain name-string.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting VTP Management Domain. Empty String will be returned if set to nothing."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/CDP/VTPMgmtDomain'
        return url
    
    @_get_status_helper
    def get_status_dnsDomainName(self):
        """Description: Shows the domain name.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting Domain Name. Empty String will be returned if set to nothing."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/DNS/Domain/Name'
        return url
    
    @_get_status_helper
    def get_status_dnsServerAddress(self):
        """Description: Shows the Ethernet speed in Mbps. The speed can be in full-duplex or half-duplex.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting DNS server Address"""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/DNS/Server/Address'
        return url
    
    @_get_status_helper
    def get_status_EthernetMACaddress(self):
        """Description: Shows the MAC (Media Access Control) address for the Ethernet interface.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting MAC address. Empty String will be returned if set to nothing."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/Ethernet/MacAddress'
        return url
    
    @_get_status_helper
    def get_status_EthernetSpeed(self):
        """Description: Shows the Ethernet speed in Mbps. The speed can be in full-duplex or half-duplex.
        Usage: Requires user role: ADMIN, USER
        Output:10half/10full/100half/100full/1000full."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/Ethernet/Speed'
        return url
    

    
    @_get_status_helper
    def get_status_Ipv4_address(self):
        """Description: Shows the IPv4 address that uniquely identifies this device.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting IPv4 Address assigned."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/IPv4/Address'
        return url
    
    @_get_status_helper
    def get_status_Ipv4_gateway(self):
        """Description: Shows the address of the IPv4 gateway.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting the address of the IPv4 gateway."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/IPv4/Gateway'
        return url
    
    @_get_status_helper
    def get_status_Ipv4_subnetMask(self):
        """Description: Shows the subnet mask which determines which subnet an IPv4 address belongs to.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting the subnet mask of the unit."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/IPv4/SubnetMask'
        return url
    
    @_get_status_helper
    def get_status_Ipv6_address(self):
        """Description: Shows the IPv6 address that uniquely identifies this device..
        Usage: Requires user role: ADMIN, USER
        Output:String denoting IPv6 Address assigned."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/IPv6/Address'
        return url
    
    @_get_status_helper
    def get_status_Ipv6_gateway(self):
        """Description: Shows the address of the IPv6 gateway.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting the address of the IPv6 gateway."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/IPv6/Gateway'
        return url
    
    @_get_status_helper
    def get_status_voice_VLANID(self):
        """Description: The feedback shows the VLAN Voice ID.
        Usage: Requires user role: ADMIN, USER
        Output:Off/1..4094
        Off: The VLAN Voice Mode is not enabled.
        1..4094: VLAN Voice ID"""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/VLAN/Voice/VlanId'
        return url
    
    @_get_status_helper
    def get_status_Ipv6_linkLocalAddress(self):
        """Description: Shows the IPv6 link local address that is displayed on the primary user interface.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting the address of the IPv6 Link Local Address."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/IPv6/LinkLocalAddress'
        return url
    
    @_get_status_helper
    def get_status_wifi_BSSID(self):
        """Description: Shows the Basic Service Set Identifiers (BSSID) used for the Wi-Fi connection.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting the BSSID of Wifi network. Empty string is returned if not appliable."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/Wifi/BSSID'
        return url
    
    @_get_status_helper
    def get_status_wifi_channel(self):
        """Description: Shows the channel used for the Wi-Fi connection.
        Usage: Requires user role: ADMIN, USER
        Output:Integer denoting the wifi Channel. -1 if not applicable."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/Wifi/Channel'
        return url
    
    @_get_status_helper
    def get_status_wifi_InterfaceEnabled(self):
        """Description: Indicates whether the Wi-Fi is enabled (on) or not (off).
        Usage: Requires user role: ADMIN, USER
        Output:On/Off"""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/Wifi/InterfaceEnabled'
        return url
    
    @_get_status_helper
    def get_status_wifi_frequency(self):
        """Description: Shows the frequency corresponding to the Wi-Fi channel.
        Usage: Requires user role: ADMIN, USER
        Output:Integer denoting the wifi Frequency. 0 if the wifi is not enabled."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/Wifi/Frequency'
        return url
    
    @_get_status_helper
    def get_status_wifi_InterfaceReason(self):
        """Description: Provides a description of why the Wi-Fi interface is enabled or not.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the reason for interface status and config value."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/Wifi/InterfaceReason'
        return url
    
    @_get_status_helper
    def get_status_wifi_MacAddress(self):
        """Description: Shows the MacAddress used for the Wi-Fi connection.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting the MAC address of Wifi adapter."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/Wifi/MacAddress'
        return url
    
    @_get_status_helper
    def get_status_wifi_RawSSID(self):
        """Description: Shows the Raw SSID of the Wi-Fi connection.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting the Raw SSID of Wifi Connection. Empty string is returned if not appliable."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/Wifi/RawSSID'
        return url
    
    @_get_status_helper
    def get_status_wifi_Reason(self):
        """Description: Shows the reason defined for the Wi-Fi connection, if applicable.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting the Reason for the Wifi connection. Empty string is returned if not appliable."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/Wifi/Reason'
        return url
   
    @_get_status_helper
    def get_status_wifi_Phase2Method(self):
        """Description: Shows the Phase2Method used for the Wi-Fi connection, if applicable.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting the Method used for the Wifi connection. Empty string is returned if not appliable."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/Wifi/Phase2Method'
        return url
    
    @_get_status_helper
    def get_status_wifi_Region(self):
        """Description: Shows the region of the Wi-Fi connection.
        Usage: Requires user role: ADMIN, USER
        Output:The region code. If the device doesn't receive a region code from the access point, the value will be '00'. If there is no wifi at all, Empty string will be returned."""
        
        url = f'http://{self.address}/getxml?location=/Status/Network/Wifi/Region'
        return url
    
    
    @_get_status_helper
    def get_status_wifi_RSSI(self):
        """Description: Shows the Received Signal Strength Indicator (RSSI) used by the Wi-Fi connection.
        Usage: Requires user role: ADMIN, USER
        Output: Integer denoting the strength of the wifi signal."""
        # Did not return, needs to be checked later
        url = f'http://{self.address}/getxml?location=/Status/Network/Wifi/RSSI'
        return url
    
    @_get_status_helper
    def get_status_wifi_ScanResult_flag(self):
        """Description: Returns all the flags found in a scan result.
        Note that you must run a scan before this will yield results.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the flag."""
        # Did not return, needs to be checked later
        url = f'http://{self.address}/getxml?location=/Status/Network/Wifi/ScanResult/Flags'
        return url
    
     
    @_get_status_helper
    def get_status_wifi_Status(self):
        """Description: Shows the status of the Wi-Fi network connection.
        Usage: Requires user role: ADMIN, USER
        Output: Associating/Connected/Disconnected/AuthFailed/Failed/Other
        Associating-Trying to connect to a WI-FI network.
        Connected- The device is not connected to a WI-FI network.
        Disconnected-The device is not connected to a WI-FI network.
        AuthFailed- Authentication failed when trying to connect to a WI-FI network.
        Failed- The device could not connect to the WI-FI network for reasons other than authentication failure.
        Other-Any other scenario"""

        url = f'http://{self.address}/getxml?location=/Status/Network/Wifi/Status'
        return url
    
    @_get_status_helper
    def get_status_wifi_type(self):
        """Description: Shows the encryption type of the Wi-Fi network connection.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the type of Wifi Security. Empty string will be returned if not appliable."""

        url = f'http://{self.address}/getxml?location=/Status/Network/Wifi/Type'
        return url
    
    @_get_status_helper
    def get_status_diagnosticMessage_description(self):
        """Description: Shows a description of the current diagnostics alerts.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the message description"""

        url = f'http://{self.address}/getxml?location=/Status/Diagnostics/Message/Description'
        return url
    
    @_get_status_helper
    def get_status_diagnosticMessage_level(self):
        """Description: Shows the level of importance of the diagnostics message. Use it along with get_status_diagnosticMessage_description for better correspondance.
        Usage: Requires user role: ADMIN, USER
        Output: Returns anyone of Error/Warning/Critical
        Error: There is an error in the device. The device can still be used, but there can be some restrictions. 
        Warning: A problem is detected and a more specific report follows indicating the exact problem.
        Critical: The warning level is critical. The device cannot be used."""

        url = f'http://{self.address}/getxml?location=/Status/Diagnostics/Message/Level'
        return url
    
    @_get_status_helper
    def get_status_diagnosticMessage_level(self):
        """Description: Additional information on the diagnostics alert, if available. Use it along with get_status_diagnosticMessage_description for better correspondance.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting an additional information. An empty string is returned if no information is available."""

        url = f'http://{self.address}/getxml?location=/Status/Diagnostics/Message/References'
        return url
    
    @_get_status_helper
    def get_status_diagnosticMessage_type(self):
        """Description: Shows information on the results of the latest diagnostics on the device. Use it along with get_status_diagnosticMessage_description for better correspondance.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting a diagnostic message class"""

        url = f'http://{self.address}/getxml?location=/Status/Diagnostics/Message/Type'
        return url
    
    @_get_status_helper
    def get_status_mediaChannel_count(self):
        """Description: Shows the number of incoming or outgoing audio channels.
        Usage: Requires user role: ADMIN, USER
        Output: Integer denoting the number of incoming or outgoing audio channels. Returns an empty result if no calls found."""

        url = f'http://{self.address}/getxml?location=/Status/MediaChannels/Call/Channel/Audio/Channels'
        return url
    
    @_get_status_helper
    def get_status_mediaChannel_audioProtocol(self):
        """Description: Shows the audio algorithm of the incoming or outgoing audio.
        Usage: Requires user role: ADMIN, USER
        Output: AACLD/G711A/G711Mu/G722/G7221/G7221C/G723_1/G728/G729/G729A/G729AB/Off/Opus , Returns an empty result if no call.
        AACLD: The AAC-LD is an MPEG-4 Low Delay Audio Coder audio compression format.
        G711A: The G.711 A-law algorithm is an ITU-T standard for audio compression.
        G711Mu: The G.711 Mu-law algorithm is an ITU-T standard for audio compression.
        G722: The G.722 algorithm is an ITU-T standard for audio compression.
        G7221: The G.722.1 algorithm is an ITU-T standard for audio compression.
        G7221C: The G.722.1 annex C algorithm is an ITU-T standard for audio compression.
        G723_1: The G.723.1 algorithm is an ITU-T standard for audio compression.
        G728: The G.728 algorithm is an ITU-T standard for audio compression.
        G729: The G.729 algorithm is an ITU-T standard for audio compression.
        G729A: The G.729 annex A algorithm is an ITU-T standard for audio compression.
        G729AB: The G.729 annex A and B algorithm is an ITU-T standard for audio compression.
        Off: No audio.
        Opus: Opus is a royalty-free IETF standard for audio compression"""

        url = f'http://{self.address}/getxml?location=/Status/MediaChannels/Call/Channel/Audio/Protocol'
        return url
    
    
    @_get_status_helper
    def get_status_netStat_Bytes(self):
        """Description: Shows the encryption status for audio or video on the incoming or outgoing call.
        Usage: Requires user role: ADMIN, USER
        Output:Integer denoting the value bytes for audio, video. Returns an empty result if no calls found."""

        url = f'http://{self.address}/getxml?location=/Status/MediaChannels/Call/Channel/NetStat/Bytes'
        return url
    
    @_get_status_helper
    def get_status_mediaChannel_encryption(self):
        """Description: Shows the encryption status for audio or video on the incoming or outgoing call.
        Usage: Requires user role: ADMIN, USER
        Output: On/Off. Returns an empty result if no calls found."""

        url = f'http://{self.address}/getxml?location=/Status/MediaChannels/Call/Channel/Encryption'
        return url
    
    @_get_status_helper
    def get_status_netStat_ChannelRate(self):
        """Description: Shows the bandwidth for audio, video or data on the incoming or outgoing channel.
        Usage: Requires user role: ADMIN, USER
        Output:Integer denoting the value of channel rate. Returns an empty result if no calls found."""

        url = f'http://{self.address}/getxml?location=/Status/MediaChannels/Call/Channel/NetStat/ChannelRate'
        return url
    
    @_get_status_helper
    def get_status_netStat_Jitter(self):
        """Description: Shows the jitter for audio, video or data at the present moment on the incoming or outgoing channel, as specified by RFC 3550.
        Usage: Requires user role: ADMIN, USER
        Output:Integer denoting the value of jitter. Returns an empty result if no calls found."""

        url = f'http://{self.address}/getxml?location=/Status/MediaChannels/Call/Channel/NetStat/LastIntervalLost'
        return url
    
    @_get_status_helper
    def get_status_netStat_LastIntervalLost(self):
        """Description: Shows the number of packets lost for audio, video or data during the last interval on the incoming or outgoing channels.
        Usage: Requires user role: ADMIN, USER
        Output:Integer denoting the value of packets lost. Returns an empty result if no calls found."""

        url = f'http://{self.address}/getxml?location=/Status/MediaChannels/Call/Channel/NetStat/LastIntervalLost'
        return url
    
    @_get_status_helper
    def get_status_netStat_LastIntervalReceived(self):
        """Description: Shows the number of packets received for audio, video or data during the last interval on the incoming or outgoing channels.
        Usage: Requires user role: ADMIN, USER
        Output:Integer denoting the value of packets received for audio, video in last interval. Returns an empty result if no calls found."""

        url = f'http://{self.address}/getxml?location=/Status/MediaChannels/Call/Channel/NetStat/LastIntervalReceived'
        return url
    
    @_get_status_helper
    def get_status_netStat_Loss(self):
        """Description: Shows the number of packets lost for audio, video or data during the last interval on the incoming or outgoing channels.
        Usage: Requires user role: ADMIN, USER
        Output:Integer denoting the value of packets lost for audio, video. Returns an empty result if no calls found."""

        url = f'http://{self.address}/getxml?location=/Status/MediaChannels/Call/Channel/NetStat/Loss'
        return url
    
    @_get_status_helper
    def get_status_netStat_Packets(self):
        """Description: Shows the number of packets that was received or sent for audio, video or data on the incoming or outgoing channels.
        Usage: Requires user role: ADMIN, USER
        Output:Integer denoting the value of packets received for audio, video. Returns an empty result if no calls found."""

        url = f'http://{self.address}/getxml?location=/Status/MediaChannels/Call/Channel/NetStat/Packtes'
        return url
    
    @_get_status_helper
    def get_status_netStat_MaxJitter(self):
        """Description: Shows the maximum jitter for audio, video or data that has been measured during last interval (about 5 seconds).
        Usage: Requires user role: ADMIN, USER
        Output:Integer denoting the value of Jitter for audio, video. Returns an empty result if no calls found."""

        url = f'http://{self.address}/getxml?location=/Status/MediaChannels/Call/Channel/NetStat/MaxJitter'
        return url
    
    @_get_status_helper
    def get_status_netStat_ParticipantId(self):
        """Description: Shows the ID of the Active Control participant on the incoming audio or video channel.
        Usage: Requires user role: ADMIN, USER
        Output:String denoting the participant id for the corresponding call. Returns an empty result if no calls found."""

        url = f'http://{self.address}/getxml?location=/Status/MediaChannels/Call/Channel/ParticipantId'
        return url
    
    @_get_status_helper
    def get_status_netStat_Type(self):
        """Description: Shows the media type on the incoming or outgoing channel.
        Usage: Requires user role: ADMIN, USER
        Output:Audio/Video/Data
        Audio: The media type on the incoming or outgoing channel is audio. 
        Video: The media type on the incoming or outgoing channel is video. 
        Data: The media type on the incoming or outgoing channel is data
        Returns an empty result if no calls found."""

        url = f'http://{self.address}/getxml?location=/Status/MediaChannels/Call/Channel/Type'
        return url
    
    
    @_get_status_helper
    def get_status_connectedHardware_info(self):
        """Description: Shows hardware information about connected device.
        Usage: Requires user role: ADMIN, INTEGRATOR, ROOMCONTROL, USER
        Output:String denoting the Hardware information of the connected device.
        Returns an empty result if no device found."""

        url = f'http://{self.address}/getxml?location=/Status/Peripherals/ConnectedDevice/HardwareInfo'
        return url
    
    @_get_status_helper
    def get_status_connectedHardware_ID(self):
        """Description: Shows the MAC-address of the connected device.
        Usage: Requires user role: ADMIN, INTEGRATOR, ROOMCONTROL, USER
        Output:String denoting the MAC address of the connected device.
        Returns an empty result if no device found."""

        url = f'http://{self.address}/getxml?location=/Status/Peripherals/ConnectedDevice/ID'
        return url
    
    @_get_status_helper
    def get_status_connectedHardware_Name(self):
        """Description: Shows the product name of connected device.
        Usage: Requires user role: ADMIN, INTEGRATOR, ROOMCONTROL, USER
        Output:String denoting the Name of the connected device.
        Returns an empty result if no device found."""

        url = f'http://{self.address}/getxml?location=/Status/Peripherals/ConnectedDevice/Name'
        return url
    
    @_get_status_helper
    def get_status_room_airQualityIndex(self):
        """Description: Shows the air quality index as reported by the Room Navigator with the specific device id. The values are as defined by the German Federal Environmental Agency (UBA).
        Usage: Requires user role: ADMIN, INTEGRATOR, ROOMCONTROL, USER . Room Navigator(s) is necessary to be connected to the device.
        Output:String denoting the air quality as per UBA and as reported by the Room Navigator(s). Returns an empty result if Room Navigator(s) is not conncted or communicative. 
        0–1.9: Clean Hygienic Air.
        2.0–2.9: Good Air Quality. Ventilation recommended.
        3.0-3.9: Noticeable Comfort Concerns. Not recommended for exposure longer than 12 
        months. Ventilation Required.
        4.0-4.9: Significant Comfort Issues. Not recommended for exposure longer than 1 month. 
        Refresh air when possible. Increase ventilation.
        5.0 and above: Unacceptable Conditions.
        Returns an empty result if no device found."""

        url = f'http://{self.address}/getxml?location=/Status/Peripherals/ConnectedDevice/RoomAnalytics/AirQuality/Index'
        return url
    
    @_get_status_helper
    def get_status_room_ambientTemperature(self):
        """Description: Shows the ambient temperature as reported by the Room Navigator with the specific device id.
        Usage: Requires user role: ADMIN, INTEGRATOR, ROOMCONTROL, USER . Room Navigator is necessary to be connected to the device.
        Output:String denoting the value of ambient temperature. Returns an empty result if Room Navigator is not conncted or communicative.
        Returns an empty result if no device found."""

        url = f'http://{self.address}/getxml?location=/Status/Peripherals/ConnectedDevice/RoomAnalytics/AmbientTemperature'
        return url
    
    @_get_status_helper
    def get_status_connectedHardware_serial(self):
        """Description: Shows the serial number of a connected peripheral device, for example a touch controller.
        Usage: Requires user role: ADMIN, INTEGRATOR, ROOMCONTROL, USER . Room Navigator is necessary to be connected to the device.
        Output:String denoting the value of Serial Number of connected device(s).
        Returns an empty result if no device found."""

        url = f'http://{self.address}/getxml?location=/Status/Peripherals/ConnectedDevice/SerialNumber'
        return url
    
    @_get_status_helper
    def get_status_connectedHardware_SoftwareInfo(self):
        """Description: Shows information of the software version running on the connected device.
        Usage: Requires user role: ADMIN, INTEGRATOR, ROOMCONTROL, USER . Room Navigator is necessary to be connected to the device.
        Output:String denoting the value of running software information of connected device(s).
        Returns an empty result if no device found."""

        url = f'http://{self.address}/getxml?location=/Status/Peripherals/ConnectedDevice/SoftwareInfo'
        return url
    
    @_get_status_helper
    def get_status_connectedHardware_status(self):
        """Description: Shows peripheral devices that are currently connected to the video conferencing device.
        Usage: Requires user role: ADMIN, INTEGRATOR, ROOMCONTROL, USER . Room Navigator is necessary to be connected to the device.
        Output: Connected/ResponseTimedOut for the device ID. To get more information about the device , use get_status_connectedHardware_info.
        Returns an empty result if no device found."""

        url = f'http://{self.address}/getxml?location=/Status/Peripherals/ConnectedDevice/Status'
        return url
    
    @_get_status_helper
    def get_status_provisioning_SWcurrent_versionID(self):
        """Description: Shows the version ID of the current software.
        Usage: Requires user role: ADMIN, USER .
        Output: String denoting the current software version ID."""
    
        url = f'http://{self.address}/getxml?location=/Status/Provisioning/Software/Current/VersionId'
        return url
    
    @_get_status_helper
    def get_status_provisioning_status(self):
        """Description: Shows the status of the provisioning.
        Usage: Requires user role: ADMIN, USER .
        Output: Failed/AuthenticationFailed/Provisioned/Idle/NeedConfig/ConfigError.
        Failed: The provisioning failed.
        AuthenticationFailed: The authentication failed.
        Provisioned: The device is provisioned.
        Idle: The provisioning is not active.
        NeedConfig: The device needs to be configured.
        ConfigError: An error occurred during configuration."""
    
        url = f'http://{self.address}/getxml?location=/Status/Provisioning/Status'
        return url
    
    @_get_status_helper
    def get_status_proximityStatus(self):
        """Description: Shows whether proximity services are available on the device.
        Usage: Requires user role: ADMIN, USER .
        Output: Available, Deactivated, Disabled
        Available: Proximity mode has been enabled with the command xConfiguration Proximity 
        Mode and one or more of the proximity services have been enabled with xConfiguration 
        Proximity Services commands. 
        Deactivated: Proximity services have been deactivated with the command xCommand 
        Proximity Services Deactivate.
        Disabled: Proximity mode has been disabled with xConfiguration Proximity Mode, or none 
        of the services have been enabled with the xConfiguration Proximity Services commands."""
    
        url = f'http://{self.address}/getxml?location=/Status/Proximity/Services/Availability'
        return url
    
    @_get_status_helper
    def get_status_peoplePresence(self):
        """Description: Shows if there are people present in the room or not. The feature is based on ultrasound. 
        The device will not keep record of who was in the room, only whether or not there are people 
        present in the room.
        When someone enters the room, the status is updated immediately. After the room gets vacant, 
        it may take up to two minutes for the status to change.
        Usage: Requires user role: ADMIN, INTEGRATOR, USER
        Output: Yes/No/Unknown."""
    
        url = f'http://{self.address}/getxml?location=/Status/RoomAnalytics/PeoplePresence'
        return url
        
    @_get_status_helper
    def get_status_roomPreset_defined(self,n:int):
        """Description: Shows if a camera preset is stored at this position.
        Usage: Requires user role: ADMIN, INTEGRATOR, USER
        Output: True/False.An empty string will be returned if the specified preset is not available on the device."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/RoomPreset/{n}/Defined'
        return url
    
    @_get_status_helper
    def get_status_roomPreset_description(self,n:int):
        """Description: Lists the configured name for the specific preset.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting configuration name for the presets. An empty string will be returned if the specified preset is not available on the device."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/RoomPreset/{n}/Description'
        return url
    
    @_get_status_helper
    def get_status_roomPreset_type(self,n:int):
        """Description: Shows the camera preset type.
        Usage: Requires user role: ADMIN, USER
        Output: All/Camera . An empty string will be returned if the specified preset is not available on the device."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/RoomPreset/{n}/Type'
        return url
    
    @_get_status_helper
    def get_status_sip_alternateURI(self):
        """Description: Shows an alternate SIP URI defined in its configuration.
        Usage: Requires user role: ADMIN, USER
        Output: Shows an alternate SIP URI defined in its configuration . An empty string will be returned if the configuration is not available on the device."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SIP/AlternateURI/Alias'
        return url
    
    @_get_status_helper
    def get_status_sip_authentication(self):
        """Description: Shows if Authentication for SIP is configured.
        Usage: Requires user role: ADMIN, USER
        Output: Shows which authentication mechanism is used when registering to the SIP Proxy Server . An empty string will be returned if the configuration is not available on the device."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SIP/Authentication'
        return url
    
    @_get_status_helper
    def get_status_sip_callForward_displayName(self):
        """Description: Returns the URI that is displayed on the user interface for the forwarded call.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the display name of call forward."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SIP/CallForward/DisplayName'
        return url
    
    @_get_status_helper
    def get_status_sip_callForward_Mode(self):
        """Description: Indicates whether the call forward mode for SIP is set to on or off.
        Usage: Requires user role: ADMIN, USER
        Output: On/Off"""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SIP/CallForward/Mode'
        return url
    
    @_get_status_helper
    def get_status_sip_callForward_URI(self):
        """Description: Indicates the address the incoming calls are directed to when call forward mode is set on.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the value of uri"""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SIP/CallForward/URI'
        return url
    
    @_get_status_helper
    def get_status_sip_mailbox_messageWaiting(self):
        """Description: Indicates how many new messages are in the mailbox for SIP.
        Usage: Requires user role: ADMIN, USER
        Output: Integer denoting the value of number of messages received and waiting."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SIP/Mailbox/MessagesWaiting'
        return url
    
    @_get_status_helper
    def get_status_sip_mailbox_uri(self):
        """Description: Returns the URI for your SIP mailbox.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the value of mailbox uri for SIP."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SIP/Mailbox/URI'
        return url
    
    @_get_status_helper
    def get_status_sip_proxyAddress(self):
        """Description: Returns the URI for your SIP mailbox.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the value of proxy address for SIP."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SIP/Proxy/Address'
        return url
    
    @_get_status_helper
    def get_status_sip_proxyStatus(self):
        """Description: Shows the status of the communication between the device and the SIP Proxy server.
        Usage: Requires user role: ADMIN, USER
        Output: Active/AuthenticationFailed/DNSFailed/Off/Timeout/UnableTCP/UnableTLS/Unknown
        Active: The communication between the device and the SIP Proxy is active.
        DNSFailed: The attempt to establish communication to the DNS server failed.
        Off: There is no communication between the device and the SIP Proxy.
        Timeout: The attempt to establish communication to the SIP Proxy timed out.
        UnableTCP: The device is unable to use TCP as the transport method.
        UnableTLS: The device is unable to use TLS as the transport method.
        Unknown: The status of the communication is not known.
        AuthenticationFailed: Wrong username or password."""

        url = f'http://{self.address}/getxml?location=/Status/SIP/Proxy/Status'
        return url
    
    @_get_status_helper
    def get_status_sip_RegistrationStatus(self):
        """Description: Shows the status of the communication between the device and the SIP Proxy server.
        Usage: Requires user role: ADMIN, USER
        Output: Deregister/Failed/Inactive/Registered/Registering
        Deregister: The device is in the process of de-registering to the SIP Proxy.
        Failed: The device failed to register to the SIP Proxy.
        Inactive: The device is not registered to any SIP Proxy.
        Registered: The device is registered to the SIP Proxy.
        Registering: The device is in the process of registering to the SIP Proxy."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SIP/Registration/Status'
        return url
    
    @_get_status_helper
    def get_status_sip_registrationAuthentication(self):
        """Description: Shows the status of the communication between the device and the SIP Proxy server.
        Usage: Requires user role: ADMIN, USER
        Output: Digest/Off
        Digest: Uses the Digest access authentication method, as specified by RFC 2069.
        Off: No authentication mechanism is used.
        Returns an empty string if SIP is not available."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SIP/Registration/Authentication'
        return url
    
    @_get_status_helper
    def get_status_sip_registrationURI(self):
        """Description: Shows the URI used for registration to the SIP Proxy server.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the value of SIP registration URI. Returns an empty string if SIP is not available."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SIP/Registration/URI'
        return url
    
    @_get_status_helper
    def get_status_sip_security(self):
        """Description: Shows the encryption status of the signaling with the SIP Proxy server.
        Usage: Requires user role: ADMIN, USER
        Output: True/False. Returns an empty string if SIP is not available"""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SIP/Secure'
        return url
    
    @_get_status_helper
    def get_status_sip_verified(self):
        """Description: Shows whether or not the SSL certificate of the server that the device tries to register to is 
        included in the device's trusted CA-list. The server is typically a Cisco VCS or CUCM.
        Usage: Requires user role: ADMIN, USER
        Output: True/False
        True: The server's SIP certificate is checked against the trusted CA-list on the device and 
        found valid. Additionally, the fully qualified domain name of the server matches the valid 
        certificate.
        False: A TLS connection is not set up because the SIP certificate verification failed or the 
        domain name did not match. Note that the status also returns False when TLS is not used 
        (SIP DefaultTransport not set to TLS) or certificate verification is switched 
        off (SIP TlsVerify: Off. This setting is accessible through your products web interface)."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SIP/Verified'
        return url
    
    @_get_status_helper
    def get_status_unit_wifiAvailability(self):
        """Description: Shows whether or not the device has wireless internet (WiFi) capability.
        Usage: Requires user role: ADMIN, USER
        Output: False/True"""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SystemUnit/Hardware/HasWiFi'
        return url
    
    @_get_status_helper
    def get_status_unit_module_SerialNumber(self):
        """Description: Shows the serial number of the hardware module in the device.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the value of Hardware module's serial number."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SystemUnit/Hardware/Module/SerialNumber'
        return url
    
    @_get_status_helper
    def get_status_unit_module_compatibilityScore(self):
        """Description: The devices have different sets of compatibility levels. Please check the release note to find the 
        compatibility levels and minimum software version required for your product.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the value of the compatibility level for the device. 0 is the lowest"""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SystemUnit/Hardware/Module/CompatibilityLevel'
        return url
    
    @_get_status_helper
    def get_status_unit_temperature_status(self):
        """Description: Shows the current temperature alarm level. "High" is meant to raise attention to the temperature trend since the operating temperature is higher than normal. At "Critical" level the device 
        will shut down processes and processors to prevent any damage to the device.
        Usage: Requires user role: ADMIN, USER
        Output: Unknown, Normal, High, Critical."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SystemUnit/Hardware/Monitoring/Temperature/Status'
        return url
    
    @_get_status_helper
    def get_status_unit_fan_speed(self):
        """Description: The feedback shows the speed (rpm) for the specified fan.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the value of the speed of fan in Revolutions per Minute (rpm). An empty string is returned if this monitoring is not applicable."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SystemUnit/Hardware/Monitoring/Fan/Status'
        return url
    
    @_get_status_helper
    def get_status_unit_notification(self):
        """Description: Lists text related to important system notifications. Notifications are issued e.g. when a device 
        was rebooted because of a software upgrade, or when a factory reset has been performed.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the text of notification(s). An empty string is returned if this monitoring is not applicable."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SystemUnit/Notifications/Notification/Text'
        return url
    
    @_get_status_helper
    def get_status_unit_notificationType(self):
        """Description: Lists notifications types. Notifications are issued e.g. when a device 
        was rebooted because of a software upgrade, or when a factory reset has been performed.
        Usage: Requires user role: ADMIN, USER
        Output: SoftwareUpgradeOK/SoftwareUpgradeFailed/RebootRequired/Other
        SoftwareUpgradeOK: This value is returned after a successful software upgrade.
        SoftwareUpgradeFailed: This value is returned after a failed software upgrade attempt.
        RebootRequired: This value is returned when a reboot is required.
        Other: This value is returned for any other notifications. 
        An empty string is returned if this monitoring is not applicable."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SystemUnit/Notifications/Notification/Type'
        return url
    
    @_get_status_helper
    def get_status_unit_productID(self):
        """Description: Shows the product ID.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the product ID."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SystemUnit/ProductId'
        return url
    
    @_get_status_helper
    def get_status_unit_productPlatform(self):
        """Description: Shows the product platform.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the product Platform."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SystemUnit/ProductPlatform'
        return url
    
    @_get_status_helper
    def get_status_unit_productType(self):
        """Description: Shows the product type.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the product Type."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SystemUnit/ProductType'
        return url
    
    
    @_get_status_helper
    def get_status_unit_software_displayName(self):
        """Description: Shows the name of the software that is installed on the device, as it is displayed in the UI.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the software name being displayed on the UI."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SystemUnit/Software/DisplayName'
        return url
    
    @_get_status_helper
    def get_status_unit_software_installed(self):
        """Description: Shows the name of the software that is installed on the device.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the software name installed on the system."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SystemUnit/Software/Name'
        return url
    
    @_get_status_helper
    def get_status_unit_software_version(self):
        """Description: Shows the software version installed on the device.
        Usage: Requires user role: ADMIN, USER
        Output: String denoting the software version installed on the system."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SystemUnit/Software/Version'
        return url
    
    @_get_status_helper
    def get_status_unit_uptime(self):
        """Description: Shows the number of seconds since the last restart of the device.
        Usage: Requires user role: ADMIN, USER
        Output: Integer denoting the System Uptime in seconds."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/SystemUnit/Uptime'
        return url
    
    @_get_status_helper
    def get_status_unit_timeNow(self):
        """Description: Returns the date and time set on the device.
        Usage: Requires user role: ADMIN, INTEGRATOR, USER
        Output: String denoting date and time."""
        #To be checked later
        url = f'http://{self.address}/getxml?location=/Status/Time/SystemTime'
        return url
    
    
    
    def test_call(self,extension : str ,duration : int = 30,output_debug : bool =False):
        """Description: Test calls automatically for desired duration to termintae automatically.
        Usage: provide the remote destination extension/uri: extension , call duration  to be tested is set at 30 seconds by default, can be changed. Note that the call either must be received or set to auto answer on remote device."""
            
        url = f"http://{self.address}/putxml"
        payload_connect = f"<Command>\r\n\t<Dial>\r\n\t\t<Number>{extension}</Number>\r\n\t</Dial>\r\n</Command>"
        headers = {
          'Content-Type': 'text/xml',
        }
        try:
            response_connect = requests.post(url, headers=headers,auth=HTTPBasicAuth(self.username,self.password), data=payload_connect)
            call_id = jxmlease.parse(response_connect.text)['Command']['DialResult']['CallId']
            if (response_connect.status_code==401):
                    raise Exception("Authorisation Failed , Please check Credentials\n")
            elif (response_connect.status_code==400):
                    raise Exception("Connection Failed , Please check Connection\n")
            elif (response_connect.status_code==200):
                time.sleep(duration)
                payload_disconnect = f"<Command>\r\n\t<Call>\r\n\t\t<Disconnect>\r\n \t\t\t<CallId>{call_id}</CallId>\r\n \t\t</Disconnect>\r\n\t</Call>\r\n</Command>"
                response_disconnect = requests.post(url, headers=headers,auth=HTTPBasicAuth(self.username,self.password), data=payload_disconnect)
                call_data = self.get_call_history(output_debug=False)['Command']['CallHistoryGetResult']['Entry'][0]
                if output_debug:
                    print(call_data)
                return call_data
        except Exception as e:
            return (e)
    
    def set_call_protocol_priotity(self,protocol : str,output_debug :bool = False):
        """Descriptopn: Set protocol priority for calls
        Usage: WebRTC, Auto"""

        url = f"http://{self.address}/putxml"
        headers = {
          'Content-Type': 'text/xml',
        }
        payload_Bookings_protocol_priotity = f"<Configuration>\r\n\t\t<Bookings>\r\n\t\t<ProtocolPriority>{protocol}</ProtocolPriority>\r\n\t\t</Bookings>\r\n</Configuration>"
        try:
            response = requests.post(url, headers=headers,auth=HTTPBasicAuth(self.username,self.password), data=payload_Bookings_protocol_priotity,verify=self.ssl_verify)
            call_priotity = jxmlease.parse(response.text)
            if response.status_code == 200:
                if "Success" in response.text:
                    if output_debug:
                        print(call_priotity)
                    return(call_priotity)
                elif "Error" in response.text:
                    error = jxmlease.parse(response.text)['Configuration']['Error']['Details']
                    raise f"Error: {error}"
            else:
                if response.status_code == 401:
                    raise Exception("Authorisation Failed , Please check Credentials\n")
                elif (response.status_code==400):
                    raise Exception("Connection Failed , Please check Connection\n")
                else:
                    raise Exception(f"Error: {response.status_code}")
        except Exception as e:
            if output_debug:
                print(e)
            return(e)
        
        
    def set_default_call_protocol(self,protocol : str,output_debug: bool =False):
        """Description: Set the default call protocol
        Usage : Auto/H320/H323/Sip/Spark"""
        
        url = f"http://{self.address}/putxml"
        headers = {
          'Content-Type': 'text/xml',
        }
        payload_default_call_protocol = f"<Configuration>\r\n\t<Conference>\r\n\t\t<DefaultCall>\r\n\t \t\t<Protocol>{protocol}</Protocol>\r\n\t\t</DefaultCall>\r\n\t</Conference>\r\n</Configuration>"
        
        try:
            response = requests.post(url, headers=headers,auth=HTTPBasicAuth(self.username,self.password), data=payload_default_call_protocol)
            default_call_proto = jxmlease.parse(response.text)
            if response.status_code == 200:
                if "Success" in response.text:
                    if output_debug:
                        print(default_call_proto)
                    return(default_call_proto)
                elif "Error" in response.text:
                    error = jxmlease.parse(response.text)['Configuration']['Error']['Details']
                    raise f"Error: {error}"
            else:
                if response.status_code == 401:
                    raise Exception("Authorisation Failed , Please check Credentials\n")
                elif (response.status_code==400):
                    raise Exception("Connection Failed , Please check Connection\n")
                else:
                    raise Exception(f"Error: {response.status_code}")
        except Exception as e:
            if output_debug:
                print(e)
            return(e)
            
    
    def set_auto_answer(self,mode: str,mute: str,delay: int=0,output_debug: bool=False):
        """Description: Set Auto Answer on or off along with associated functions like mute and delay in seconds
        Usage Provide mode, mute mode and delay is by default 0, can be set as desired."""
        
        url = f"http://{self.address}/putxml"
        headers = {
          'Content-Type': 'text/xml',
        }
        payload_auto_answer = f"<Configuration>\r\n\t<Conference>\r\n\t\t<AutoAnswer>\r\n\t\t\t<Mode>{mode}</Mode><Delay>{delay}</Delay><Mute>{mute}</Mute>\r\n\t\t</AutoAnswer>\r\n\t</Conference>\r\n</Configuration>"
        try:
            response = requests.post(url, headers=headers,auth=HTTPBasicAuth(self.username,self.password), data=payload_auto_answer)
            auto_answer = jxmlease.parse(response.text)
            if response.status_code == 200:
                if "Success" in response.text:
                    if output_debug:
                        print(auto_answer)
                    return(auto_answer)
                elif "Error" in response.text:
                    error = jxmlease.parse(response.text)['Configuration']['Error'][0]['Details']
                    raise Exception(f"Error: {error}")
            else:
                if response.status_code == 401:
                    raise Exception("Authorisation Failed , Please check Credentials\n")
                elif (response.status_code==400):
                    raise Exception("Connection Failed , Please check Connection\n")
                else:
                    raise Exception(f"Error: {response.status_code}")
        except Exception as e:
            if output_debug:
                print(e)
            return(e)
        
    def get_call_history(self,output_debug : bool =False):
        """Description: Get call history
        Usage: Call the function , returns json structured output for all calls"""
        
        url = f"http://{self.address}/putxml"
        
        payload_call_history = f"<Command>\r\n\t<CallHistory>\r\n\t\t<Get>\r\n\t\t\t<DetailLevel>Full</DetailLevel>\t\r\n\t\t</Get>\r\n\t</CallHistory>\r\n</Command>"

        headers = {
          'Content-Type': 'text/xml',
        }
        try:
            response_call_history = requests.post(url, headers=headers,auth=HTTPBasicAuth(self.username,self.password), data=payload_call_history)
            call_history = jxmlease.parse(response_call_history.text)
            #print(response_call_history.text)
            if response_call_history.status_code == 200:
                if output_debug:
                    print(call_history)
                return(call_history)
            else:
                if response_call_history.status_code == 401:
                    raise Exception("Authorisation Failed , Please check Credentials\n")
                elif (response_call_history.status_code==400):
                    raise Exception("Connection Failed , Please check Connection\n")
                else:
                    raise Exception(f"Error: {response_call_history.status_code}")
        except Exception as e:
            if output_debug:
                print(e)
            return(e)
        
    def set_audio_noise_removal(self,mode : str ,output_debug : bool =False):
        """Description: Audio Noise Removal
        usage mode = on, off"""
        
        payload = f"<Configuration>\r\n\t<Audio>\r\n\t\t<Microphones>\r\n\t\t\t<NoiseRemoval>\r\n\t\t\t\t<Mode>{mode}</Mode>\r\n\t\t\t</NoiseRemoval>\r\n\t\t</Microphones>\r\n\t</Audio>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
    def set_encryption_mode(self,mode : str,output_debug:bool=False):
        """Description: Encrytion Mode
        usage Off/On/BestEffort"""
        
        payload = f"<Configuration>\r\n\t<Conference>\r\n\t\t<Encryption>\r\n\t\t\t<Mode>{mode}</Mode>\r\n\t\t\t</Encryption>\r\n\t\t</Conference>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
    def set_default_call_rate(self,value:int=6000,output_debug:bool=False):
        """Description: Default call rate
        usage 64-6000"""
        
        payload = f"<Configuration>\r\n\t<Conference>\r\n\t\t<DefaultCall>\r\n\t\t\t<Rate>{value}</Rate>\r\n\t\t\t</DefaultCall>\r\n\t\t</Conference>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
    def set_far_end_ctrl_sig_capbality(self,mode:str,output_debug:bool=False):
        """Description: far end control signal capability
        usage Off/On"""
    
        payload = f"<Configuration>\r\n\t<Conference>\r\n\t\t<FarEndControl>\r\n\t\t\t<SignalCapability>{mode}</SignalCapability>\r\n\t\t\t</FarEndControl>\r\n\t\t</Conference>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
    def set_h323_auth_mode(self,mode:str,output_debug:bool=False):
        """Off: The device will not try to authenticate itself to a H.323 Gatekeeper, but will still try a 
        normal registration.
        On: If an H.323 Gatekeeper indicates that it requires authentication, the device will try 
        to authenticate itself to the gatekeeper. Requires the H323 Authentication LoginName 
        and H323 Authentication Password settings to be defined on both the device and the 
        Gatekeeper
        usage Off/On"""
            
        payload = f"<Configuration>\r\n\t<H323>\r\n\t\t<Authentication>\r\n\t\t\t<Mode>{mode}</Mode>\r\n\t\t\t</Authentication>\r\n\t\t</H323>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
    def set_h323_encryption_key_size(self,size:str="Min1024bit",output_debug:bool=False):
        """Description: Set the encryption key size for H323
        usage : Max1024bit/Min1024bit/Min2048bit"""
        
        payload = f"<Configuration>\r\n\t<H323>\r\n\t\t<Encryption>\r\n\t\t\t<KeySize>{size}</KeySize>\r\n\t\t\t</Encryption>\r\n\t\t</H323>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
    def set_h323_login_name_password(self,name:str,password:str,output_debug:bool=False):
        """Description: The device sends the H323 Authentication Login Name and the H323 Authentication Password 
        to an H.323 Gatekeeper for authentication. The authentication is a one way authentication from 
        the device to the H.323 Gatekeeper, i.e. the device is authenticated to the gatekeeper. If the 
        H.323 Gatekeeper indicates that no authentication is required, the device will still try to register. 
        Requires the H.323 Authentication Mode to be enabled.
        Usage : Provide Name and password , string """
        
        url = f"http://{self.address}/putxml"
        headers = {
          'Content-Type': 'text/xml',
        }
        payload_name = f"<Configuration>\r\n\t<H323>\r\n\t\t<Authentication>\r\n\t\t\t<LoginName>{name}</LoginName>\r\n\t\t\t</Authentication>\r\n\t\t</H323>\r\n</Configuration>"
        try:
            response_name = requests.post(url, headers=headers,auth=HTTPBasicAuth(self.username,self.password), data=payload_name)
            parse_name = jxmlease.parse(response_name.text)
            if response_name.status_code == 200:
                if "Success" in response_name.text:
                    payload_password = f"<Configuration>\r\n\t<H323>\r\n\t\t<Authentication>\r\n\t\t\t<Password>{password}</Password>\r\n\t\t\t</Authentication>\r\n\t\t</H323>\r\n</Configuration>"
                    response_h323_pass = requests.post(url, headers=headers,auth=HTTPBasicAuth(self.username,self.password), data=payload_password)
                    if output_debug:
                        print(parse_name)
                    return(parse_name)
                else:
                    error = jxmlease.parse(response_name.text)['Configuration']['Error']['Details']
                    raise Exception(f"Error: {error}")
            else:
                if response_name.status_code == 401:
                    raise Exception("Authorisation Failed , Please check Credentials\n")
                elif (response_name.status_code==400):
                    raise Exception("Connection Failed , Please check Connection\n")
                else:
                    raise Exception(f"Error: {response_name.status_code}")
        except Exception as e:
            if output_debug:
                print(e)
            return(e)
        
    def set_h323_gateway_address(self,address:str,output_debug:bool=False):
        """Description: Define the IP address of the Gatekeeper. Requires H323 CallSetup Mode to be set to 
        Gatekeeper.
        Usage : Valid IPv4 or IPv6 addresses or DNS record address"""
        
        
        payload = f"<Configuration>\r\n\t<H323>\r\n\t\t<Gatekeeper>\r\n\t\t\t<Address>{address}</Address>\r\n\t\t\t</Gatekeeper>\r\n\t\t</H323>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
    def set_h323_alias_id(self,alias_id:str,output_debug:bool=False):
        """Description: Define the H.323 Alias ID, which is used to address the device on a H.323 Gatekeeper and will 
        be displayed in the call lists
        Usage : Proper alias ID"""

        payload = f"<Configuration>\r\n\t<H323>\r\n\t\t<H323Alias>\r\n\t\t\t<ID>{alias_id}</ID>\r\n\t\t\t</H323Alias>\r\n\t\t</H323>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_sip_mode(self,mode:str,output_debug:bool=False):
        """Description: SNMP (Simple Network Management Protocol) is used by network management systems to 
        monitor and manage devices such as routers, servers, and switches, that are connected to the 
        IP network. SNMP exposes management data in the form of variables on the managed devices, 
        which describe the device status and configuration. These variables can then be remotely 
        queried, and sometimes set, by managing applications
        Usage: Off/ReadOnly/ReadWrite , Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<NetworkServices>\r\n\t\t<SIP>\r\n\t\t\t<Mode>{mode}</Mode>\r\n\t\t\t</SIP>\r\n\t\t</NetworkServices>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    
    def set_snmp_community_name(self,community_name:str,output_debug:bool=False):
        """Description: Define the name of the SNMP community. The SNMP community name is used to authenticate 
        SNMP requests. If an SNMP request from a management system does not include a matching 
        community name (case sensitive), the message is dropped and the SNMP agent in the video 
        device will not send a response. 
        If you have the Cisco TelePresence Management Suite (TMS) you must make sure the same 
        SNMP community is configured there.
        Usage: Supply string of community name , Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<NetworkServices>\r\n\t\t<SNMP>\r\n\t\t\t<CommunityName>{community_name}</CommunityName>\r\n\t\t\t</SNMP>\r\n\t\t</NetworkServices>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_snmp_system_contact(self, system_contact:str,output_debug:bool=False):
        """Description: Define contact information that SNMP servers can use
        Usage: Supply string of contact details , Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<NetworkServices>\r\n\t\t<SNMP>\r\n\t\t\t<SystemContact>{system_contact}</SystemContact>\r\n\t\t\t</SNMP>\r\n\t\t</NetworkServices>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
    def set_snmp_location(self,system_location:str,output_debug:bool=False):
        """Description: Define location information that SNMP servers can use
        Usage: Supply System Location, Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<NetworkServices>\r\n\t\t<SNMP>\r\n\t\t\t<SystemLocation>{system_location}</SystemLocation>\r\n\t\t\t</SNMP>\r\n\t\t</NetworkServices>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
    def set_ssh_mode(self,mode:str,output_debug:bool=False):
        """Description: The SSH (or Secure Shell) protocol can provide secure encrypted communication between the 
        video conferencing device and your local computer
        Usage: Off/On, Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<NetworkServices>\r\n\t\t<SSH>\r\n\t\t\t<Mode>{mode}</Mode>\r\n\t\t\t</SSH>\r\n\t\t</NetworkServices>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
    def set_wifi_allowed(self,allow:str,output_debug:bool=False):
        """Description: Devices that have a built-in Wi-Fi adapter, can connect to the network either via Ethernet or 
        Wi-Fi. Both Ethernet and Wi-Fi are allowed by default, and the user can choose which one to 
        use from the user interface. With this setting, the administrator can disable Wi-Fi configuration, 
        so that it cannot be set up from the user interface. 
        The devices support the following standards: IEEE 802.11a, IEEE 802.11b, IEEE 802.11g, IEEE 
        802.11n, and IEEE 802.11ac. The device supports the following security protocols: WPA-PSK 
        (AES), WPA2-PSK (AES), EAP-TLS, EAP-TTLS, EAP-FAST, PEAP, EAP-MSCHAPv2, EAP-GTC, 
        and open networks (not secured).
        If the PID (Product ID), found on the rating label at the rear of the device, contains the letters NR 
        (No Radio) the device does not support Wi-F
        Usage: True, False, Requires user role: ADMIN, USER"""
            
        payload = f"<Configuration>\r\n\t<NetworkServices>\r\n\t\t<Wifi>\r\n\t\t\t<Allowed>{allow}</Allowed>\r\n\t\t\t</Wifi>\r\n\t\t</NetworkServices>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
    def set_ssh_key_algorithm(self,algorithm:str,output_debug:bool=False):
        """Description: Choose the cryptographic algorithm that shall be used for the SSH host key. Choices are 
        RSA (Rivest–Shamir–Adleman) with 2048 bits keysize, ECDSA (Elliptic Curve Digital Signature 
        Algorithm) with NIST curve P-384, and EdDSA (Edwards-curve Digital Signature Algorithm) with 
        ed25519 signature schema
        usage:ECDSA/RSA/ed25519 , Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<NetworkServices>\r\n\t\t<SSH>\r\n\t\t\t<HostKeyAlgorithm>{algorithm}</HostKeyAlgorithm>\r\n\t\t\t</SSH>\r\n\t\t</NetworkServices>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
    def set_touchpanel_remote_pairing(self,mode:str,output_debug:bool=False):
        """Description: In order to use a touch controller (Cisco Webex Room Navigator or Cisco Touch 10) as user 
        interface for the video conferencing device, the touch controller must be paired to the device. 
        When the touch controller is paired via the network (LAN), this is referred to as remote pairing. 
        Remote pairing is allowed by default; you must switch this setting Off if you want to prevent 
        remote pairing.
        Usage: On/Off, Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<Peripherals>\r\n\t\t<Pairing>\r\n\t\t\t<CiscoTouchPanels>\r\n\t\t\t\t<RemotePairing>{mode}</RemotePairing>\r\n\t\t\t</CiscoTouchPanels>\r\n\t\t\t</Pairing>\r\n\t\t</Peripherals>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_provisioning_mode(self,mode:str,output_debug:bool=False):
        """Description: It is possible to configure a device using a provisioning system (external manager). This allows 
        video conferencing network administrators to manage many devices simultaneously. With this 
        setting you choose which type of provisioning system to use. Provisioning can also be switched 
        off. Contact your provisioning system provider/representative for more information.
        Usage: Off/Auto/CUCM/Edge/Webex/WebexCalling/TMS/VCS , Requires user role: ADMIN, USER"""
        
        payload = f"<Configuration>\r\n\t<Provisioning>\r\n\t\t<Mode>{mode}</Mode>\r\n\t</Provisioning>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_provisioning_login_name(self,name:str,output_debug:bool=False):
        """Desscription: This is the username part of the credentials used to authenticate the device with the provisioning server. 
        This setting must be used when required by the provisioning server
        Usage:  Suppy login name ,Requires user role: ADMIN, USER"""
        
        payload = f"<Configuration>\r\n\t<Provisioning>\r\n\t\t<LoginName>{name}</LoginName>\r\n\t</Provisioning>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    
    def set_provisioning_login_password(self,password:str,output_debug:bool=False):
        """Desscription: This is the password part of the credentials used to authenticate the device with the provisioning server. 
        This setting must be used when required by the provisioning server
        Usage:  Supply password ,Requires user role: ADMIN, USER"""
        
        payload = f"<Configuration>\r\n\t<Provisioning>\r\n\t\t<Password>{password}</Password>\r\n\t</Provisioning>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_provisioning_webex_edge(self,mode:str,output_debug:bool=False):
        """Define if the device is linked to Webex Edge for Devices, which gives access to select Webex 
        cloud services.
        The setting applies only to devices that are registered to an on-premises service
        Usage: Off/On, Requires user role: ADMIN, USER"""
        
        payload = f"<Configuration>\r\n\t<Provisioning>\r\n\t\t<WebexEdge>{mode}</WebexEdge>\r\n\t</Provisioning>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_provisioning_tls_verify(self,mode:str,output_debug:bool=False):
        """Description: This setting applies when a video conferencing device connects to a provisioning server via 
        HTTPS.
        Before establishing a connection between the device and the HTTPS server, the device checks 
        if the certificate of the server is signed by a trusted Certificate Authority (CA). The CA certificate must be included in the CA list on the device, either pre-installed or manually uploaded 
        using the web interface or API.
        In general, the minimum TLS (Transport Layer Security) version for the HTTPS connection is 1.1. 
        There are two exceptions to this rule: 1) For compatibility reasons, the minimum TLS version is 
        1.0 for devices that are registered to CUCM. 2) Devices registered to the Webex cloud service 
        always use version 1.2.
        Usage: Off/On , Requires user role: ADMIN, USER"""
        
        payload = f"<Configuration>\r\n\t<Provisioning>\r\n\t\t<TlsVerify>{mode}</TlsVerify>\r\n\t</Provisioning>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_proximity_alternate_port(self,mode:str,output_debug:bool=False):
        """Description: This setting applies only when NetworkServices HTTP Mode is set to HTTP+HTTPS or HTTPS.
        By default, Proximity connections use TCP port 443. Use this setting to allow Proximity 
        connections also on port 65533
        Usage: True/ False, Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<Proximity>\r\n\t\t<AlternatePort>\r\n\t\t\t<Enabled>{mode}</Enabled>\r\n\t</AlternatePort>\r\n\t</Proximity>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_proximity_mode(self,mode:str,output_debug:bool=False):
        """Description: The Proximity Mode setting has no effect for devices that are registered to the Webex cloud 
        service. To prevent a cloud registered device from sending ultrasound pairing messages, you 
        must set Audio Ultrasound MaxVolume to 0.
        For devices registered on-premises, the Proximity Mode setting determines whether the 
        device will emit ultrasound pairing messages or not. When the device emits ultrasound pairing 
        messages, Cisco collaboration clients can detect that they are close to the device. 
        In order to use a client, at least one of the Proximity services must be enabled (refer to the 
        Proximity Services settings) as well. In general, Cisco recommends enabling all the Proximity 
        services.
        The Proximity Mode and Audio Ultrasound MaxVolume settings only affect ultrasound pairing 
        messages. To stop all ultrasound emissions, the RoomAnalytics PeoplePresenceDetector and 
        Standby WakeupOnMotionDetection settings must also be switched Off.
        Usage: Off/On , Requires user role: ADMIN, USER"""

        payload = f"<Configuration>\r\n\t<Proximity>\r\n\t\t<Mode>{mode}</Mode>\r\n\t</Proximity>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_proximity_services_callcontrol(self,mode:str,output_debug:bool=False):
        """Description: Enable or disable basic call control features on Cisco collaboration clients. When this setting is 
        enabled, you are able to control a call using a Cisco collaboration client (for example dial, mute, 
        adjust volume and hang up). This service is supported by mobile devices (iOS and Android). 
        Proximity Mode must be On for this setting to take any effect.
        Usage: Enabled/Disabled, Requires user role: ADMIN, USER"""
        
        payload = f"<Configuration>\r\n\t<Proximity>\r\n\t\t<Services>\r\n\t\t\t<CallControl>{mode}</CallControl>\r\n\t</Services>\r\n\t</Proximity>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_proximity_contentshare_from_clients(self,mode:str,output_debug:bool=False):
        """Description: Enable or disable content sharing from Cisco collaboration clients. When this setting is enabled, 
        you can share content from a Cisco collaboration client wirelessly on the device, e.g. share your 
        laptop screen. This service is supported by laptops (OS X and Windows). Proximity Mode must 
        be On for this setting to take any effect.
        Usage: Enabled/ Disabled , Requires user role: ADMIN, USER"""
        
        payload = f"<Configuration>\r\n\t<Proximity>\r\n\t\t<Services>\r\n\t\t\t<ContentShare>\r\n\t\t\t<FromClients>{mode}</FromClients>\r\n\t</ContentShare>\r\n\t</Services>\r\n\t</Proximity>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ambient_noise_estimation_interval(self,interval:int=10,output_debug:bool=False):
        """Set the interval at which the ambient noise estimation is run, if enabled. The xConfiguration 
        RoomAnalytics AmbientNoiseEstimation Mode can be used to enable or disable ambient noise 
        estimations.
        Usage:  (Default 10)-60 ,Requires user role: ADMIN, INTEGRATOR, USER"""
        
        payload = f"<Configuration>\r\n\t<RoomAnalytics>\r\n\t\t<AmbientNoiseEstimation>\r\n\t\t\t<Interval>{int(interval)}</Interval>\r\n\t</AmbientNoiseEstimation>\r\n\t</RoomAnalytics>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ambient_noise_estimation_mode(self,mode:str,output_debug:bool=False):
        """Description: The device can estimate the stationary ambient noise level (background noise level) in the 
        room. The result is reported in the RoomAnalytics AmbientNoise Level dBA status. The status 
        is updated when a new ambient noise level is detected
        Usage : Off/On, Requires user role: ADMIN, INTEGRATOR, USER"""
        
        payload = f"<Configuration>\r\n\t<RoomAnalytics>\r\n\t\t<AmbientNoiseEstimation>\r\n\t\t\t<Mode>{mode}</Mode>\r\n\t</AmbientNoiseEstimation>\r\n\t</RoomAnalytics>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_people_count_out_of_call_mode(self, mode:str, output_debug:bool=False):
        """By using face detection, the device has the capability to find how many persons are in the 
        room. By default, the device only counts people when in a call, or when displaying the self-view 
        picture.
        Codec Plus, Codec Pro: Applies only when the device has a Cisco Quad Camera connected.
        Usage: On/Off ,Requires user role: ADMIN, INTEGRATOR, USER"""
        
        payload = f"<Configuration>\r\n\t<RoomAnalytics>\r\n\t\t<PeopleCountOutOfCall>{mode}</PeopleCountOutOfCall>\r\n\t</RoomAnalytics>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_people_presence_detector_mode(self,mode:str,output_debug:bool=False):
        """Description: The device has the capability to find whether or not people are present in the room, and report 
        the result in the RoomAnalytics PeoplePresence status. The feature is based on ultrasound. 
        Read the status description for more details.
        Ultrasound signals for presence detection are not emitted when both this setting AND 
        the Standby WakeupOnMotionDetection setting are switched Off. The Audio Ultrasound 
        MaxVolume and Proximity Mode settings has no effect on presence detection
        Usage: On/ Off , Requires user role: ADMIN, INTEGRATOR, USER"""
        
        payload = f"<Configuration>\r\n\t<RoomAnalytics>\r\n\t\t<PeoplePresenceDetector>{mode}</PeoplePresenceDetector>\r\n\t</RoomAnalytics>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_reverberation_time_interval(self,interval:int=1800,output_debug:bool=False):
        """Description: Defines how often the RT60 will be measured and reported to the RoomAnalytics status. The 
        interval is in seconds.
        The RoomAnalytics ReverberationTime Mode configuration must be enabled to set the interval.
        Usage: Supply interval value (60-3600), default = 1800, Requires user role: ADMIN, INTEGRATOR, USER"""
        
        payload = f"<Configuration>\r\n\t<RoomAnalytics>\r\n\t\t<ReverberationTime>\r\n\t\t\t<Interval>{int(interval)}</Interval>\r\n\t</ReverberationTime>\r\n\t</RoomAnalytics>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_reverberation_time_mode(self,mode:str,output_debug:bool=False):
        """Description: Reverberation time is a measure of how fast a sound will "fade away" or decay in a room.
        This is highly related to the perception of the acoustic quality of a room.
        The Cisco Webex devices are capable of measuring the reverberation time, RT60, directly from 
        the acoustic echo canceller.
        As opposed to traditional reverberation time measurement where it is required to emit a noise 
        or impulse signal in the room, the Cisco device will measure RT60 as a “silent measurement”.
        Due to the silent measurement behavior, the RT60 values will be indicative and not strictly 
        correct according to the ISO 3382-2 standard.
        The measurements will measure the RT60 values for each octave band from 125 Hz to 4 kHz.
        Usage: On/ Off, Requires user role: ADMIN, INTEGRATOR, USER
        """
        
        
        payload = f"<Configuration>\r\n\t<RoomAnalytics>\r\n\t\t<ReverberationTime>\r\n\t\t\t<Mode>{mode}</Mode>\r\n\t</ReverberationTime>\r\n\t</RoomAnalytics>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ssh_welcome_text(self,mode:str,output_debug:bool=False):
        """Description: Choose which information the user should see when logging on to the device through SSH
        Off: The welcome text is: Login successful
        On: The welcome text is: Welcome to <system name>; Software version; Software 
        release date; Login successful.
        Usage: message in string format"""
        
        payload = f"<Configuration>\r\n\t<NetworkServices>\r\n\t\t<WelcomeText>{mode}</WelcomeText>\r\n\t\t</NetworkServices>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ntp_mode(self,mode:str,output_debug:bool=False):
        """Description: The Network Time Protocol (NTP) is used to synchronize the device's time and date to a reference time server. The time server will be queried regularly for time updates.
        Usage: Auto/Off , Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<NetworkServices>\r\n\t\t<NTP>\r\n\t<Mode>{mode}</Mode>\r\n\t\t</NTP>\r\n\t\t</NetworkServices>\r\n</Configuration>"
        if mode == "Auto" or mode == "Off":
            return (self.__post_parser_return(payload,output_debug))
        else:
            raise Exception("Illegal Value")
        
    def set_ntp_manual_mode(self,address:str,order:int=1,output_debug:bool=False):
        #TO BE CHECKED
        payload_manual = f"<Configuration>\r\n\t<NetworkServices>\r\n\t\t<NTP>\r\n\t<Mode>{address}</Mode>\r\n\t\t</NTP>\r\n\t\t</NetworkServices>\r\n</Configuration>"
        manual_setting = str(self.__post_parser_return(payload_manual,output_debug))
        if "Success" in manual_setting:
            payload_set = f"<Configuration>\r\n\t<NetworkServices>\r\n\t\t<NTP>\r\n\t\t\t<Server>{order}</Server><Address>{address}</Address>\r\n\t\t</NTP>\r\n\t</NetworkServices>\r\n</Configuration>"
            return (self.__post_parser_return(payload_set,output_debug))
    
        
    def set_cdp_mode(self,mode:str,output_debug:bool=False):
        """Description: Enable or disable the CDP (Cisco Discovery Protocol) daemon. Enabling CDP will make the 
            device report certain statistics and device identifiers to a CDP-enabled switch. If CDP is 
            disabled, the Network VLAN Voice Mode: Auto setting will not work
        Usage: Off/On , Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<NetworkServices>\r\n\t\t<CDP>\r\n\t<Mode>{mode}</Mode>\r\n\t\t</CDP>\r\n\t\t</NetworkServices>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_http_mode(self,mode: str,output_debug: bool=False):
        """Description: Define whether or not to allow access to the device using the HTTP or HTTPS (HTTP Secure) 
        protocols. Note that the device's web interface use HTTP or HTTPS. If this setting is switched 
        Off, you cannot use the web interface.
        For additional security (encryption and decryption of requests and pages that are returned by 
        the web server), allow only HTTPS.
        Usage: Off/HTTP+HTTPS/HTTPS"""
        
        payload = f"<Configuration>\r\n\t<NetworkServices>\r\n\t\t<HTTP>\r\n\t<Mode>{mode}</Mode>\r\n\t\t</HTTP>\r\n\t\t</NetworkServices>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_http_proxy_mode(self,mode:str,output_debug:bool=False):
        
        """Description: You can configure to use a proxy server for HTTP, HTTPS, and WebSocket traffic. The HTTP 
        proxy can be set up manually, it can be auto-configured (PACUrl), fully automated (WPAD), or it 
        can be turned off.
        If NetworkServices HTTP Proxy Mode is not turned Off, you can further specify which 
        services shall use the proxy in the HttpClient UseHttpProxy, HttpFeedback UseHttpProxy, and 
        WebEngine UseHttpProxy settings.
        Communication with the Cisco Webex cloud will always go via the proxy if NetworkServices 
        HTTP Proxy Mode is not turned Off.
        Regardless of the Proxy Mode, the device will never communicate with CUCM, MRA (CUCM via 
        Expressway), or TMS via proxy.
        Usage : Manual/Off/PACUrl/WPAD"""
        
        if mode == "Manual":
             global __man_flag
             __man_flag = 1
        elif mode == "Off" or mode=="WPAD":
             #__man_flag, PACUrl_flag
             __man_flag = 0;PACUrl_flag=0;
        elif mode == "PACUrl":
            global __PACUrl_flag
            __PACUrl_flag=1

        payload = f"<Configuration>\r\n\t<NetworkServices>\r\n\t\t<HTTP>\r\n\t\t<Proxy>\r\n\t<Mode>{mode}</Mode>\r\n\t\t</Proxy>\r\n\t\t</HTTP>\r\n\t\t</NetworkServices>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_http_proxy_url(self,url:str,output_debug:bool=False):
        """Description: Requires user role: ADMIN, USER
        Set the URL of the HTTP proxy server. Requires that the NetworkServices HTTP Proxy Mode is 
        set to Manual.
        Usage: Requires user role: ADMIN, USER
        Set the URL of the HTTP proxy server. Requires that the NetworkServices HTTP Proxy Mode is 
        set to Manual."""
        global __man_flag
        if __PACUrl_flag==0 and __man_flag==1:
            
            __man_flag = 0
            payload = f"<Configuration>\r\n\t<NetworkServices>\r\n\t\t<HTTP>\r\n\t\t<Proxy>\r\n\t<Url>{url}</Url>\r\n\t\t</Proxy>\r\n\t\t</HTTP>\r\n\t\t</NetworkServices>\r\n</Configuration>"
            return (self.__post_parser_return(payload,output_debug))
        else:
            raise Exception("Please set proxy mode to manual with set_http_proxy_mode('Manual') and try again")
    
    def set_http_proxy_pacurl(self,url:str,output_debug:bool=False):
        """Description: Set the URL of the PAC (Proxy Auto Configuration) script. Requires that the NetworkServices 
        HTTP Proxy Mode is set to PACUrl
        Usage: supply URL ,Requires user role: ADMIN, USER"""
        global __PACUrl_flag
        if __PACUrl_flag==1 and __man_flag==0:
            
            __PACUrl_flag = 0
            payload = f"<Configuration>\r\n\t<NetworkServices>\r\n\t\t<HTTP>\r\n\t\t<Proxy>\r\n\t<PACUrl>{url}</PACUrl>\r\n\t\t</Proxy>\r\n\t\t</HTTP>\r\n\t\t</NetworkServices>\r\n</Configuration>"
            return (self.__post_parser_return(payload,output_debug))
        else:
            raise Exception("Please set proxy mode to PACUrl with set_http_proxy_mode('PACUrl') and try again")
    
    def set_https_min_tls(self,tlsv:str,output_debug:bool=False):
        """Description: Set the lowest version of the TLS (Transport Layer Security) protocol that is allowed for HTTPS.
        Usage: Requires user role: ADMIN , TLSv1.1/TLSv1.2"""
        
        payload = f"<Configuration>\r\n\t<NetworkServices>\r\n\t\t<HTTPS>\r\n\t\t<Server>\r\n\t<MinimumTLSVersion>{tlsv}</MinimumTLSVersion>\r\n\t\t</Server>\r\n\t\t</HTTPS>\r\n\t\t</NetworkServices>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_https_strict_transport(self,mode:str,output_debug:bool=False):
        """Description: The HTTP Strict Transport Security header lets a web site inform the browser that it should 
        never load the site using HTTP and should automatically convert all attempts to access the site 
        using HTTP to HTTPS requests instead
        Usage: Requires user role: ADMIN, Off/On"""
        
        payload = f"<Configuration>\r\n\t<NetworkServices>\r\n\t\t<HTTPS>\r\n\t\t<StrictTransportSecurity>{mode}</StrictTransportSecurity>\r\n\t\t</HTTPS>\r\n\t\t</NetworkServices>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_incoming_call_notification(self,mode:str,output_debug:bool=False):
        """Description: You can enable an incoming call notification with amplified visuals. The screen and touch 
        controller will flash red/white approximately once every second (1.75 Hz) to make it easier for 
        hearing impaired users to notice an incoming call. If the device is already in a call the screen 
        will not flash as this will disturb the on-going call, instead you will get a normal notification on 
        screen and touch panel.
        Usage: AmplifiedVisuals/Default , Requires user role: ADMIN, INTEGRATOR, USER"""
        
        payload = f"<Configuration>\r\n\t<UserInterface>\r\n\t\t<Accessibility>\r\n\t\t<IncomingCallNotification>{mode}</IncomingCallNotification>\r\n\t\t</Accessibility>\r\n\t\t</UserInterface>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
    def set_ui_webex_assistance(self,mode:str,output_debug:bool=False):
        """Description: Webex Assistant allows you to control the device by using voice commands. Webex Assistant 
        is a cloud service, so the device must either be registered to the Webex cloud service or registered to an on-premises service and linked to Webex Edge for Devices. 
        Use this setting to enable or disable the Webex Assistant on the device
        Usage:  Off/On ,Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<UserInterface>\r\n\t\t<Assistant>\r\n\t\t<Mode>{mode}</Mode>\r\n\t\t</Assistant>\r\n\t\t</UserInterface>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ui_bookings_visibility_tree(self,mode:str,output_debug:bool=False):
        """Description: Sets the meeting details to private. “Schedule meeting” will be displayed as the title of the 
        meeting.
        Usage: Auto/Hidden, Requires user role: ADMIN, INTEGRATOR, USER"""
        
        payload = f"<Configuration>\r\n\t<UserInterface>\r\n\t\t<Bookings>\r\n\t\t<Visibility>\r\n\t\t<Title>{mode}</Title>\r\n\t\t</Visibility>\r\n\t\t</Bookings>\r\n\t\t</UserInterface>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ui_branding_awake_colors(self, mode:str, output_debug:bool=False):
        """Description: If the device is set up with branding customizations, this setting affects the colors of the 
        logo that is shown when the device is awake. You can choose whether you want to show the 
        logo in full color, or reduce the opacity of the logo so that it blends in more naturally with the 
        background and other elements on the screen.
        Usage: Auto/Native , Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<UserInterface>\r\n\t\t<Branding>\r\n\t\t<AwakeBranding>\r\n\t\t<Colors>{mode}</Colors>\r\n\t\t</AwakeBranding>\r\n\t\t</Branding>\r\n\t\t</UserInterface>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    
    def set_ui_contact_info_type(self,mode:str,output_debug:bool=False):
        """Description: Choose which type of contact information to show in the user interface
        Usage:  Auto/DisplayName/E164Alias/H320Number/H323Id/IPv4/IPv6/None/SipUri/SystemName, Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<UserInterface>\r\n\t\t<ContactInfo>\r\n\t\t<Type>{mode}</Type>\r\n\t\t</ContactInfo>\r\n\t\t</UserInterface>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ui_ket_tones_mode(self,mode:str,output_debug:bool=False):
        """Description: You can configure the device to make a keyboard click sound effect (key tone) when typing text 
        or numbers.
        Usage: Off/On , Requires user role: ADMIN, USER."""
        
        payload = f"<Configuration>\r\n\t<UserInterface>\r\n\t\t<KeyTones>\r\n\t\t<Mode>{mode}</Mode>\r\n\t\t</KeyTones>\r\n\t\t</UserInterface>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ui_features_call_end(self,mode:str,output_debug:bool=False):
        """Description: Choose whether or not to remove the default End Call button from the user interface. The 
        setting removes only the button, not its functionality as such.
        Usage:  Auto/Hidden, Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<UserInterface>\r\n\t\t<Features>\r\n\t\t<Call>r\n\t\t<End>{mode}</End>\r\n\t\t</Call>\r\n\t\t</Features>\r\n\t\t</UserInterface>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ui_features_call_keypad(self,mode:str,output_debug:bool=False):
        """Description: Choose whether or not to remove the default in-call Keypad button from the user interface. 
        This button opens a keypad, which for example can be used for DTMF input.
        Usage:  Auto/Hidden ,Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<UserInterface>\r\n\t\t<Features>\r\n\t\t<Call>r\n\t\t<End>{mode}</End>\r\n\t\t</Call>\r\n\t\t</Features>\r\n\t\t</UserInterface>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_time_zone(self,zone:str,output_debug:bool=False):
        """Description: Define the time zone for the geographical location of the device. The information in the value 
        space is from the tz database, also called the IANA Time Zone Database.
        Usage: Zone , Requires user role: ADMIN, INTEGRATOR, USER"""
        
        payload = f"<Configuration>\r\n\t<Time>\r\n\t\t<Zone>\{zone}</Zone>\r\n\t\t</Time>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_time_format(self, time_format:int,output_debug:bool=False):
        """Description: Define the time format
        Usage: 24/12, Requires user role: ADMIN, USER"""
        
        payload = f"<Configuration>\r\n\t<Time>\r\n\t\t<TimeFormat>\{time_format}H</TimeFormat>\r\n\t\t</Time>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_date_format(self, date_format:str,output_debug:bool=False):
        """Descriotion: Define the date format.
        Usage: DD_MM_YY/MM_DD_YY/YY_MM_DD, Requires user role: ADMIN, USER"""
        
        payload = f"<Configuration>\r\n\t<Time>\r\n\t\t<DateFormat>{date_format}</DateFormat>\r\n\t\t</Time>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_standby_boot_action(self, camrea_pos:str,output_debug=False):
        """Description: Define the camera position after a restart of the video conferencing device
        Usage: None/DefaultCameraPosition/RestoreCameraPosition, Requires user role: ADMIN, INTEGRATOR, USER"""
        
        payload = f"<Configuration>\r\n\t<Standby>\r\n\t\t<BootAction>{camrea_pos}</BootAction>\r\n\t\t</Standby>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
    
    def set_standby_control(self,mode:str,output_debug:bool=False):
        """Description: Define whether the device should go into standby mode or not
        Usage: Off/On, Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<Standby>\r\n\t\t<Control>{mode}</Control>\r\n\t\t</Standby>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_standby_signage_audio(self, mode:str="Off",output_debug:bool=False):
        """By default, a device does not play out audio in digital signage mode even if the web page has 
        audio. You can use this setting to override the default behavior.
        Usage: Off/On ,Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<Standby>\r\n\t\t<Signage>\r\n\t\t\t<Audio>{mode}</Audio>\r\n\t\t</Signage>\r\n\t\t</Standby>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_standby_delay(self, delay:int=7, output_debug:bool=False):
        """Descreiption: Define how long (in minutes) the device shall be in idle mode before it goes into standby mode. 
        Requires the Standby Control to be enabled.
        Usage: Integer (1..480), Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<Standby>\r\n\t\t<Delay>{int(delay)}</Delay>\r\n\t\t</Standby>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    
    def set_standby_signage_mode(self,mode:str="Off",output_debug:bool=False):
        """Description: Content from a URL (a web page) can replace the traditional half-wake background image and 
        information. This feature is called digital signage. Users can interact with the web page if the 
        device has an interactive screen, for example click on a link or enter text in a form.
        The use of digital signage does not prevent the device from entering standby the normal way. 
        Therefore, the Standby Delay setting determines for how long the digital signage is shown 
        before the device goes into standby.
        Usage: Off/On, Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<Standby>\r\n\t\t<Signage>\r\n\t\t\t<Mode>{mode}</Mode>\r\n\t\t</Signage>\r\n\t\t</Standby>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
    def set_standby_signage_url(self, url:str,output_debug:bool=False):
        """Description: Set the URL of the web page you want to display on the screen (digital signage). If the length 
        of the URL is 0, the device retains normal half-wake mode. If the URL fails, the device retains 
        normal half-wake mode and a diagnostics message is issued.
        Usage: string of valid url, Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<Standby>\r\n\t\t<Signage>\r\n\t\t\t<Url>{url}</Url>\r\n\t\t</Signage>\r\n\t\t</Standby>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_standby_signage_refresh_interval(self, interval:int=0,output_debug:bool=False):
        """Description: You can use this setting to force a web page to refresh at regular intervals. This is useful for 
        web pages that are not able to refresh themselves. It is not recommended to set a refresh 
        interval with the interactive mode.
        Usage: Integer (0..1440), Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<Standby>\r\n\t\t<Signage>\r\n\t\t\t<RefreshInterval>{int(interval)}</RefreshInterval>\r\n\t\t</Signage>\r\n\t\t</Standby>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_standby_wakeup_action(self,camera_pos:str,output_debug:bool=False):
        """Define the camera position when leaving standby mode
        Usage:None/RestoreCameraPosition/DefaultCameraPosition, Requires user role: ADMIN, INTEGRATOR, USER"""
        
        payload = f"<Configuration>\r\n\t<Standby>\r\n\t\t<WakeupAction>{camera_pos}</WakeupAction>\r\n\t\t</Standby>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
    def set_standby_wakeup_motion_detection(self,mode:str,output_debug:bool=False):
        """Automatic wake up on motion detection is a feature that allows the device to detect when 
        people enter the room. The feature is based on ultrasound detection.
        Ultrasound signals for motion detection are not emitted when both this setting AND the 
        RoomAnalytics PeoplePresenceDetector setting are switched Off. The Audio Ultrasound 
        MaxVolume and Proximity Mode settings has no effect on motion detection
        Usage: Off/On , Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<Standby>\r\n\t\t<WakeupOnMotionDetection>{mode}</WakeupOnMotionDetection>\r\n\t\t</Standby>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
    def set_system_unit_name(self,name:str,output_debug:bool=False):
        """Description: Define the device name. The device name will be sent as the hostname in a DHCP request and 
        when the device is acting as an SNMP Agent
        Usage: String ,Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<SystemUnit>\r\n\t\t<Name>{name}</Name>\r\n\t\t</SystemUnit>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
    def set_system_unit_crash_reporting(self,mode:str,output_debug:bool=False):
        """Description: If the device crashes, the device can automatically send logs to the Cisco Automatic Crash 
        Report tool (ACR) for analyses. The ACR tool is for Cisco internal usage only and not available 
        to customers
        Usage: Off/On , Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<SystemUnit>\r\n\t\t<CrashReporting>\r\n\t\t<Mode>{mode}</Mode>\r\n\t\t</CrashReporting>\r\n\t\t</SystemUnit>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_system_unit_crash_report_url(self,url:str,output_debug:bool=False):
        """Description: If the device crashes, the device can automatically send logs to the Cisco Automatic Crash 
        Report tool (ACR) for analyses. The ACR tool is for Cisco internal usage only and not available 
        to customers
        Usage: String with valid url, Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<SystemUnit>\r\n\t\t<CrashReporting>\r\n\t\t<Url>{url}</Url>\r\n\t\t</CrashReporting>\r\n\t\t</SystemUnit>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))  
    
    def set_system_unit_custom_id(self, sys_id:str,output_debug:bool=False):
        """Description: The SystemUnit CustomDeviceId provides a place for you to store custom information about a 
        unit. This can be useful, for example, in aiding to track devices in a provisioning setup).
        Usage: String (0..255), Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<SystemUnit>\r\n\t\t<CustomDeviceId>{sys_id}</CustomDeviceId>\r\n\t\t</SystemUnit>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))  
    
    def set_sip_anat(self, mode:str="On",output_debug:bool=False):
        """Description: ANAT (Alternative Network Address Types) enables media negotiation for multiple addresses 
        and address types, as specified in RFC 4091.
        Usage: Off/On, Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<SIP>\r\n\t\t<ANAT>{mode}</ANAT>\r\n\t\t</SIP>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))  
    
    def set_sip_auth_username(self,name:str,output_debug:bool=False):
        """Description: This is the username part of the credentials used to authenticate towards the SIP proxy
        Usage: String (0..128), Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<SIP>\r\n\t\t<Authentication>\r\n\t\t<UserName>{name}</UserName>\r\n\t\t</Authentication>\r\n\t\t</SIP>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))  
    
    def set_sip_auth_password(self,password:str,output_debug:bool=False):
        """Description: This is the password part of the credentials used to authenticate towards the SIP proxy
        Usage: String (0..128), Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<SIP>\r\n\t\t<Authentication>\r\n\t\t<Password>{password}</Password>\r\n\t\t</Authentication>\r\n\t\t</SIP>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))  
    
    def set_sip_default_transport(self,protocol:str,output_debug:bool=False):
        """Description: Select the transport protocol to be used over the LAN
        Usage: Auto/TCP/Tls/UDP, Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<SIP>\r\n\t\t<DefaultTransport>{protocol}</DefaultTransport>\r\n\t\t</SIP>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug)) 
    
    def set_sip_display_name(self,name:str,output_debug:bool=False):
        """Description: When configured the incoming call will report the display name instead of the SIP URI.
        Usage: String (0, 550), Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<SIP>\r\n\t\t<DisplayName>{name}</DisplayName>\r\n\t\t</SIP>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_sip_ice_mode(self,mode:str="Auto",output_debug=False):
        """Description: ICE (Interactive Connectivity Establishment, RFC 5245) is a NAT traversal solution that the 
        devices can use to discover the optimized media path. Thus the shortest route for audio and 
        video is always secured between the devices. Initially STUN (Session Traversal Utilities for NAT) 
        messages are exchanged when setting up the media path.
        Usage: Auto/Off/On , Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<SIP>\r\n\t\t<Ice>\r\n\t\t<Mode>{mode}</Mode>\r\n\t\t</Ice>\r\n\t\t</SIP>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))  
        
    def set_sip_ice_default_candidate(self,mode:str="Host",output_debug=False):
        """Description: The ICE protocol needs some time to reach a conclusion about which media route to use (up to 
        the first 5 seconds of a call). During this period media for the device will be sent to the Default 
        Candidate as defined in this setting.
        Usage: Host/Rflx/Relay, Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<SIP>\r\n\t\t<Ice>\r\n\t\t<DefaultCandidate>{mode}</DefaultCandidate>\r\n\t\t</Ice>\r\n\t\t</SIP>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))  
    
    def set_sip_listen_port_mode(self,mode:str,output_debug:bool=False):
        """Description: Turn on or off the listening for incoming connections on the SIP TCP/UDP ports. If turned off, 
        the device will only be reachable through a SIP Proxy (CUCM or VCS). As a security measure, 
        SIP ListenPort should be Off when the device is registered to a SIP Proxy
        Usage: Auto/Off/On , Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<SIP>\r\n\t\t<ListenPort>{mode}</ListenPort>\r\n\t\t</SIP>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))  
    
    def sip_min_tls_version(self,tls_version:str="TLSv1.0",output_debug:bool=False):
        """Description: Set the lowest version of the TLS (Transport Layer Security) protocol that is allowed for SIP.
        Usage: TLSv1.0/TLSv1.1/TLSv1.2 , Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<SIP>\r\n\t\t<MinimumTLSVersion>{tls_version}</MinimumTLSVersion>\r\n\t\t</SIP>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
        
    def set_ui_features_join_webex(self,mode:str="Auto",output_debug:bool=False):
        """Description: Choose whether or not to remove the default Join Webex button from the user interface. 
        The button allows users to dial into a Webex meeting using just the Webex meeting number, no 
        domain is required. However, for this to work, you must set up the infrastructure to allow calls to 
        be routed to *@webex.com"
        Usage: Auto/Hidden , Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<UserInterface>\r\n\t\t<Features>\r\n\t\t<Call>r\n\t\t<JoinWebex>{mode}</JoinWebex>\r\n\t\t</Call>\r\n\t\t</Features>\r\n\t\t</UserInterface>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
                    
    def set_ui_features_call_midcall_controls(self,mode:str="Auto",output_debug:bool=False):
        """Description: Choose whether or not to remove the default Hold, Transfer, and Resume in-call buttons from 
        the user interface. The setting removes only the buttons, not their functionality as such.
        Usage: Auto/Hidden ,Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<UserInterface>\r\n\t\t<Features>\r\n\t\t<Call>r\n\t\t<MidCallControls>{mode}</MidCallControls>\r\n\t\t</Call>\r\n\t\t</Features>\r\n\t\t</UserInterface>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ui_features_call_musicmode(self,mode:str="Hidden",output_debug:bool=False):
        """Description: Choose whether or not to show the toggle button for Music Mode in the user interface
        Usage: Auto/Hidden ,Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<UserInterface>\r\n\t\t<Features>\r\n\t\t<Call>r\n\t\t<MusicMode>{mode}</MusicMode>\r\n\t\t</Call>\r\n\t\t</Features>\r\n\t\t</UserInterface>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
    def set_ui_features_call_start(self,mode:str="Auto",output_debug:bool=False):
        """Description: Choose whether or not to remove the default Call button (including the directory, favorites, and 
        recent calls lists) and the default in-call Add participant button from the user interface. The 
        setting removes only the buttons, not their functionality as such.
        Usage: Auto/Hidden , Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<UserInterface>\r\n\t\t<Features>\r\n\t\t<Call>r\n\t\t<Start>{mode}</Start>\r\n\t\t</Call>\r\n\t\t</Features>\r\n\t\t</UserInterface>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ui_features_hide_all(self,mode:bool=False,output_debug:bool=False):
        """Description: Choose whether or not to remove all default buttons from the user interface. The setting 
        removes only the buttons, not their functionality as such.
        Usage: False/True, Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<UserInterface>\r\n\t\t<Features>\r\n\t\t<HideAll>{mode}</HideAll>\r\n\t\t</Features>\r\n\t\t</UserInterface>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ui_features_share_start(self,mode:str="Auto",output_debug:bool=False):
        """Description: Choose whether or not to remove the default buttons and other UI elements for sharing and 
        previewing content, both in call and out of call, from the user interface. The setting removes 
        only the buttons and UI elements, not their functionality as such. You can still share content 
        using Cisco Proximity or Cisco Webex apps.
        Usage: Auto/Hidden , Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<UserInterface>\r\n\t\t<Features>\r\n\t\t<Share>r\n\t\t<Start>{mode}</Start>\r\n\t\t</Share>\r\n\t\t</Features>\r\n\t\t</UserInterface>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ui_language(self,language:str="English",output_debug:bool=False):
        """Description: Select the language to be used in the user interface. If the language is not supported, the 
        default language (English) will be used
        Usage: Language as string , Requires user role: ADMIN, USER"""
        
        payload = f"<Configuration>\r\n\t<UserInterface>\r\n\t\t<Language>{language}</Language>\r\n\t\t</UserInterface>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
    def set_ui_osd_mode(self,mode:str,output_debug:bool=False):
        """Description: You can configure a device to output a clean video stream. This is referred to as broadcast 
        mode. In this mode the indicators, notifications, and controls are removed. This mode is primarily for broadcasting and recording services where you only want to pass on the video to your 
        viewers
        Usage: Auto/Unobstructed , Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<UserInterface>\r\n\t\t<OSD>\r\n\t\t<Mode>{mode}</Mode>\r\n\t\t</OSD>\r\n\t\t</UserInterface>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ui_soundeffects_mode(self, mode:str="On", output_debug:bool=False):
        """Description: You can configure the device to make a sound effect, e.g. when someone connects a laptop or 
        mobile through Proximity.
        The keyboard click sound effect when typing text is not affected by this setting (refer to the 
        UserInterface Keytones Mode setting).
        Usage: Off/On , Requires user role: ADMIN, USER"""
        
        payload = f"<Configuration>\r\n\t<UserInterface>\r\n\t\t<SoundEffects>\r\n\t\t<Mode>{mode}</Mode>\r\n\t\t</SoundEffects>\r\n\t\t</UserInterface>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ui_settings_menu_visibility(self, mode:str="Auto",output_debug:bool=False):
        """Description: Choose whether or not to show the device name (or contact information) and the associated 
        drop down menu and Settings panel on the user interface.
        Usage: Auto/Hidden , Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<UserInterface>\r\n\t\t<SettingsMenu>\r\n\t\t<Visibility>{mode}</Visibility>\r\n\t\t</SettingsMenu>\r\n\t\t</UserInterface>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ui_whiteboard_actiity_indicators(self,mode:str="On",output_debug:bool=False):
        """Description: Activity indicators let you see who is drawing and annotating in a call.
        The avatars of the participants or the initials of the device are displayed when someone is interacting with the whiteboard, so you can follow who is drawing or annotating.
        Applies only to cloud-registered devices.
        Usage: Off/On , Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<UserInterface>\r\n\t\t<Whiteboard>\r\n\t\t<ActivityIndicators>{mode}</ActivityIndicators>\r\n\t\t</Whiteboard>\r\n\t\t</UserInterface>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_video_default_source(self,default_source:int=1,output_debug:bool=False):
        """Description: Define the default input source for main video in calls. The main video is played on this 
        source when you switch on or restart the video conferencing device. Use the Video Input 
        SetMainVideoSource command to change to another source while the device is running.
        Usage: 1/2/3/4/5/6 [ CodecPro ] , 1/2/3/4 [ Room70G2  RoomPanorama/Room70Panorama ] ,  [ RoomKitMini  Boards ],1/2/3 [ RoomKit  CodecPlus  Room55  Room70/Room55D  DeskPro/DeskLE ] , Requires user role: ADMIN, USER"""
        
        payload = f"<Configuration>\r\n\t<Video>\r\n\t\t<DefaultMainSource>{default_source}</DefaultMainSource>\r\n\t\t</Video>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    
    def set_video_presentation_priority(self,priority:str,output_debug:bool=False):
        """Description: Specify how to distribute the bandwidth between the presentation channel and the main video 
        channel.
        Usage: Equal/High/Low [ RoomKit  RoomKitMini  CodecPlus  CodecPro  Room55  Room70/Room55D  Room70G2  DeskPro/DeskLE  Boards ] , Equal [ RoomPanorama/Room70Panorama ], Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<Video>\r\n\t\t<Presentation>\r\n\t\t<Priority>{priority}</Priority>\r\n\t\t</Presentation>\r\n\t\t</Video>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ldap_mode(self,mode:str,output_debug:bool=False):
        """Description: The device supports the use of an LDAP (Lightweight Directory Access Protocol) server as a 
        central place to store and validate usernames and passwords. Use this setting to configure 
        whether or not to use LDAP authentication. Our implementation is tested for the Microsoft 
        Active Directory (AD) service.
        If you switch on LDAP Mode, make sure to configure the other UserManagement LDAP settings 
        to suit your setup
        Usage: Off/On , Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<UserManagement>\r\n\t\t<LDAP>\r\n\t\t<Mode>{mode}</Mode>\r\n\t\t</LDAP>\r\n\t\t</UserManagement>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ldap_address(self, address:str,output_debug:bool=False):
        """Description: Set the IP address or hostname of the LDAP server.
        Usage: String (0..255), Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<UserManagement>\r\n\t\t<LDAP>\r\n\t\t\t<Server>\r\n\t\t<Address>{address}</Address>\r\n\t\t</Server>\r\n\t\t</LDAP>\r\n\t\t</UserManagement>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ldap_port(self,port:int=0,output_debug:bool=False):
        """Description: Set the port to connect to the LDAP server on. If set to 0, use the default for the selected 
        protocol (see the UserManagement LDAP Encryption setting).
        Usage: Integer (0..65535) , Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<UserManagement>\r\n\t\t<LDAP>\r\n\t\t\t<Server>\r\n\t\t<Port>{port}</Port>\r\n\t\t</Server>\r\n\t\t</LDAP>\r\n\t\t</UserManagement>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ldap_verify_certificate_mode(self,mode:str="On",output_debug:bool=False):
        """Description: When the device connects to an LDAP server, the server will identify itself to the device by 
        presenting its certificate. Use this setting to determine whether or not the device will verify the 
        server certificate
        Usage: Off/On, Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<UserManagement>\r\n\t\t<LDAP>\r\n\t\t\t<VerifyServerCertificate>{mode}</VerifyServerCertificate>\r\n\t\t</LDAP>\r\n\t\t</UserManagement>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ldap_admin_group(self, group:str,output_debug:bool=False):
        """Description: Members of this AD (Active Directory) group will be given administrator access. This setting is a 
        shorthand for saying (memberOf:1.2.840.113556.1.4.1941:=<group name>). 
        You always have to set either an LDAP Admin Group or an LDAP Admin Filter. An LDAP 
        Admin Filter takes precedence, so if the UserManagement LDAP Admin Filter is set, the 
        UserManagement LDAP Admin Group setting is ignored
        Usage: String (0..255) , Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<UserManagement>\r\n\t\t<LDAP>\r\n\t\t\t<Admin>\r\n\t\t<Group>{group}</Group>\r\n\t\t</Admin>\r\n\t\t</LDAP>\r\n\t\t</UserManagement>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ldap_attribute(self, attribute:str, output_debug:bool=False):
        """Description: The attribute used to map to the provided username. If not set, sAMAccountName is used
        Usage: String (0..255) , Requires user role: ADMIN"""
         
        payload = f"<Configuration>\r\n\t<UserManagement>\r\n\t\t<LDAP>\r\n\t\t\t<Attribute>{attribute}</Attribute>\r\n\t\t</LDAP>\r\n\t\t</UserManagement>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ldap_min_tls_version(self,tls_version:str="TLSv1.2",output_debug:bool=False):
        """Description: Set the lowest version of the TLS (Transport Layer Security) protocol that is allowed for LDAP
        Usage: TLSv1.0/TLSv1.1/TLSv1.2 , Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<UserManagement>\r\n\t\t<LDAP>\r\n\t\t\t<MinimumTLSVersion>{tls_version}</MinimumTLSVersion>\r\n\t\t</LDAP>\r\n\t\t</UserManagement>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ldap_encryption(self,encryption:str="LDAPS",output_debug:bool=False):
        """Description: Define how to secure the communication between the device and the LDAP server. You can 
        override the port number by using the UserManagement LDAP Server Port setting
        Usage: LDAPS/None/STARTTLS , Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<UserManagement>\r\n\t\t<LDAP>\r\n\t\t\t<Encryption>{encryption}</Encryption>\r\n\t\t</LDAP>\r\n\t\t</UserManagement>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
    def set_ldap_basedn(self,basedn:str,output_debug:bool=False):
        """Description: The distinguishing name of the entry at which to start a search (base).
        Usage: String (0..255) , Requires user role: ADMIN"""
        
        payload = f"<Configuration>\r\n\t<UserManagement>\r\n\t\t<LDAP>\r\n\t\t\t<BaseDN>{basedn}</BaseDN>\r\n\t\t</LDAP>\r\n\t\t</UserManagement>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_voice_control_wakeword_mode(self, mode:str,output_debug:bool=False):
        """Description: Use this setting to enable or disable the wakeword (e.g., "Ok Webex") that is used by the 
        Webex Assistant. The Webex Assistant allows you to use the device hands free, and by using 
        the wakeword you can initiate tasks, such as placing a call and starting a presentation.
        Use the UserInterface Assistant Mode setting to switch on the Webex Assistant.
        Usage: Off/On , Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<VoiceControl>\r\n\t\t<Wakeword>\r\n\t\t\t<Mode>{mode}</Mode>\r\n\t\t</Wakeword>\r\n\t\t</VoiceControl>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
        
    def set_video_selfview_oncall_mode(self,mode:str,output_debug:bool=False):
        """Description: This setting is used to switch on self-view for a short while when setting up a call. The Video 
        Selfview OnCall Duration setting determines for how long it remains on. This applies when self view in general is switched off.
        Usage: Off/On, Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<Video>\r\n\t\t<Selfview>\r\n\t\t\t<OnCall>\r\n\t\t\t\t<Mode>{mode}</Mode>\r\n\t\t</OnCall>\r\n\t\t</Selfview>\r\n\t\t</Video>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_video_selfview_oncall_duration(self,duration:int,output_debug:bool=False):
        """Description: This setting only has an effect when the Video Selfview OnCall Mode setting is switched On. In 
        this case, the number of seconds set here determines for how long self-view is shown before it 
        is automatically switched off.
        Usage: Integer (1..60) , Requires user role: ADMIN, INTEGRATOR"""
        
        payload = f"<Configuration>\r\n\t<Video>\r\n\t\t<Selfview>\r\n\t\t\t<OnCall>\r\n\t\t\t\t<Duration>{duration}</Duration>\r\n\t\t</OnCall>\r\n\t\t</Selfview>\r\n\t\t</Video>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_network_speed(self,speed:str="Auto",output_debug=False):
        """Description: Define the Ethernet link speed. We recommend not to change from the default value, which 
        negotiates with the network to set the speed automatically. If you do not use auto-negotiation, 
        make sure that the speed you choose is supported by the closest switch in your network 
        infrastructure.
        Usage: Auto/10half/10full/100half/100full/1000full , Requires user role: ADMIN, INTEGRATOR
        10half: Force link to 10 Mbps half-duplex.
        10full: Force link to 10 Mbps full-duplex.
        100half: Force link to 100 Mbps half-duplex.
        100full: Force link to 100 Mbps full-duplex.
        1000full: Force link to 1 Gbps full-duplex"""
        
        payload = f"<Configuration>\r\n\t<Network><Speed>{speed}</Speed>\r\n\t</Network>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ipv4_mode(self,mode:str,output_debug:bool=False):
        """Description: Define how the device will obtain its IPv4 address, subnet mask and gateway address.
        The client identifier, which is used in the DHCP requests, is different for different products: MAC 
        address (Touch 10), "01" followed by the MAC address (Room Kit, Room Kit Mini, Room 55, 
        Room 70, Room 70 G2, Room 70 Panorama, Room Panorama, Boards, Codec Plus, and Codec 
        Pro), and DHCP Unique Identifier (DUID) as specified in RFC 4361 (other products, including 
        Room Navigator)
        Usage: Static/DHCP , Requires user role: ADMIN, USER"""
        
        payload = f"<Configuration>\r\n\t<Network>\r\n\t\t<IPv4>\r\n\t\t<Assignment>{mode}</Assignment>\r\n\t</IPv4>\r\n\t</Network>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ipv4_address(self, address:str,gateway:str,subnetmask:str,output_debug:bool=False):
        """Requires user role: ADMIN, USER
        Define the static IPv4 network address for the device. 
        Define the IPv4 network subnet mask.
        Define the IPv4 network gateway address. 
        ****Applicable only when the Network IPv4 Assignment 
        is set to Static
        Usage: String (0, 64) a valid IPv4 address for IpV4 address and Gateway, and valid subnet mask for Subnet mask , Requires user role: ADMIN, USER"""
        #DO NO TEST
        payload = f"<Configuration>\r\n\t<Network>\r\n\t\t<IPv4>\r\n\t\t<Address>{address}</Address>\r\n\t</IPv4>\r\n\t</Network>\r\n</Configuration>"
        resp = self.__post_parser_return(payload,output_debug)
        if "Success" in str(resp):
            payload = f"<Configuration>\r\n\t<Network>\r\n\t\t<IPv4>\r\n\t\t<Gateway>{gateway}</Gateway>\r\n\t</IPv4>\r\n\t</Network>\r\n</Configuration>"
            resp = self.__post_parser_return(payload,output_debug)
            if "Success" in str(resp):
                payload = f"<Configuration>\r\n\t<Network>\r\n\t\t<IPv4>\r\n\t\t<SubnetMask>{subnetmask}</SubnetMask>\r\n\t</IPv4>\r\n\t</Network>\r\n</Configuration>"
                return self.__post_parser_return(payload,output_debug)
            else:
                return resp
        return resp
    
    def set_network_mtu_size(self,mtu_size:int=1500,output_debug:bool=False):
        """Description:Define the Ethernet MTU (Maximum Transmission Unit) size. The MTU size must be supported 
        by your network infrastructure. The minimum size is 576 for IPv4 and 1280 for IPv6
        Usage: Integer (576..1500) , default: 1500 , Requires user role: ADMIN, USER"""
        
        payload = f"<Configuration>\r\n\t<Network>\r\n\t\t<MTU>{mtu_size}</MTU>\r\n\t</Network>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ipv6_mode(self,mode:str="Autoconf",output_debug:bool=False):
        """Description: Define how the device will obtain its IPv6 address, subnet mask and gateway address.
        The client identifier, which is used in the DHCP requests, is different for different products: MAC 
        address (Touch 10), "01" followed by the MAC address (Room Kit, Room Kit Mini, Room 55, 
        Room 70, Room 70 G2, Room 70 Panorama, Room Panorama, Boards, Codec Plus, and Codec 
        Pro), and DHCP Unique Identifier (DUID) as specified in RFC 4361 (other products, including 
        Room Navigator)
        Usage: Static/DHCPv6/Autoconf , Requires user role: ADMIN, USER"""
        
        payload = f"<Configuration>\r\n\t<Network>\r\n\t\t<IPv6>\r\n\t\t<Assignment>{mode}</Assignment>\r\n\t</IPv6>\r\n\t</Network>\r\n</Configuration>"
        return (self.__post_parser_return(payload,output_debug))
    
    def set_ipv6_address(self, address:str,gateway:str,output_debug:bool=False):
        """Description: Define the static IPv6 network address for the device and its gateway.
        ****Applicable only when the Network IPv6 
        Assignment is set to Static.
        Usage:String (0, 64) , A valid IPv6 address including a network mask. Example: 2001:DB8::/48 , 
        Define the IPv6 network gateway address.  Requires user role: ADMIN, USER"""
        
        payload = f"<Configuration>\r\n\t<Network>\r\n\t\t<IPv6>\r\n\t\t<Address>{address}</Address>\r\n\t</IPv6>\r\n\t</Network>\r\n</Configuration>"
        resp = self.__post_parser_return(payload,output_debug)
        if "Success" in str(resp):
            payload = f"<Configuration>\r\n\t<Network>\r\n\t\t<IPv6>\r\n\t\t<Gateway>{gateway}</Gateway>\r\n\t</IPv6>\r\n\t</Network>\r\n</Configuration>"
            resp = self.__post_parser_return(payload,output_debug)
            return resp
        else:
            return resp
        
    def set_ipv6_dhcp_options(self, mode:str="On",output_debug:bool=False):
         """Description: Retrieve a set of DHCP options, for example NTP and DNS server addresses, from a DHCPv6 
         server
         Usage: Off/On,  Requires user role: ADMIN, USER
         Off: Disable the retrieval of DHCP options from a DHCPv6 server.
         On: Enable the retrieval of a selected set of DHCP options from a DHCPv6 server."""
         
         payload = f"<Configuration>\r\n\t<Network>\r\n\t\t<IPv6>\r\n\t\t<DHCPOptions>{mode}</DHCPOptions>\r\n\t</IPv6>\r\n\t</Network>\r\n</Configuration>"
         return self.__post_parser_return(payload,output_debug)
     
    def set_ipv6_interface_identifier(self, interface_id:str,output_debug:bool=False):
        """Description: Define the IPv6 interface identifier for the device. The interface identifier you choose, either 
        MAC or Opaque, will determine the method that is used for generating part of the the 
        IPv6 address. This is applicable to both link-local IPv6 addresses and Stateless Address 
        Autoconfiguration (SLAAC) addresses. 
        The address contains a 64-bit prefix and a 64-bit interface itentifier generated by the device. 
        With MAC, an EUI-64 based interface identifier is generated, as described in RFC-2373.
        With Opaque, a random 64-bit interface identifier is generated as described in RFC-7217 on 
        the first boot of the device, and this is used forever, or until factory reset.
        Usage: MAC/Opaque , Requires user role: ADMIN, USER"""
        
        payload = f"<Configuration>\r\n\t<Network>\r\n\t\t<IPv6>\r\n\t\t<InterfaceIdentifier>{interface_id}</InterfaceIdentifier>\r\n\t</IPv6>\r\n\t</Network>\r\n</Configuration>"
        return self.__post_parser_return(payload,output_debug)
        
        
    def set_network_qos_mode(self,mode:str,output_debug:bool=False):
        """Description: The QoS (Quality of Service) is a method which handles the priority of audio, video and other 
        data in the network. The QoS settings must be supported by the infrastructure. Diffserv 
        (Differentiated Services) is a networking architecture that specifies a simple, scalable and 
        coarse-grained mechanism for classifying and managing network traffic. It provides QoS priorities on IP networks.
        Usage: Off/Diffserv ,Requires user role: ADMIN, USER
        
        Off: No QoS method is used. 
        Diffserv: The Network QoS Diffserv Audio, Network QoS Diffserv Video, Network QoS 
        Diffserv Data, Network QoS Diffserv Signalling, Network QoS Diffserv ICMPv6 and 
        Network QoS Diffserv NTP settings are used to prioritize packets"""
        
        payload = f"<Configuration>\r\n\t<Network>\r\n\t\t<QoS>\r\n\t\t<Mode>{mode}</Mode>\r\n\t</QoS>\r\n\t</Network>\r\n</Configuration>"
        return self.__post_parser_return(payload,output_debug)
    
    def set_allow_remote_access(self,address:str,output_debug:bool=False):
        """Description: Define which IP addresses (IPv4/IPv6) are allowed for remote access to the device from SSH/
        HTTP/HTTPS. Multiple IP addresses are separated by a white space. 
        A network mask (IP range) is specified by <ip address>/N, where N is 1-32 for IPv4, and N is 
        1-128 for IPv6. The /N is a common indication of a network mask where the first N bits are set. 
        Usage: String (0..255), A valid IPv4 address to be allowed, Requires user role: ADMIN, USER"""
        
        payload = f"<Configuration>\r\n\t<Network>\r\n\t\t<RemoteAccess>\r\n\t\t<Allow>{address}</Allow>\r\n\t</RemoteAccess>\r\n\t</Network>\r\n</Configuration>"
        return self.__post_parser_return(payload,output_debug)
            
    def set_vlan_voice_mode(self,mode:str="Auto",output_debug:bool=False):
        """Description: Define the VLAN voice mode. The VLAN Voice Mode will be set to Auto automatically if you 
        have Cisco UCM (Cisco Unified Communications Manager) as provisioning infrastructure. Note 
        that Auto mode will NOT work if the NetworkServices CDP Mode setting is Off.
        Usage: Auto/Manual/Off , Requires user role: ADMIN, USER
        Auto: The Cisco Discovery Protocol (CDP), if available, assigns an id to the voice VLAN. If CDP is not available, VLAN is not enabled. 
        Manual: The VLAN ID is set manually using the Network VLAN Voice VlanId setting. If CDP is available, the manually set value will be overruled by the value assigned by CDP.
        Off: VLAN is not enabled."""
        
        payload = f"<Configuration>\r\n\t<Network>\r\n\t\t<VLAN>\r\n\t\t<Voice>\r\n\t\t<Mode>{mode}</Mode>\r\n\t</Voice>\r\n\t</VLAN>\r\n\t</Network>\r\n</Configuration>"
        return self.__post_parser_return(payload,output_debug)
        
    def set_vlan_voice_id(self, vlan_id:int=1,output_debug=False):
        """Description: Define the VLAN voice ID. This setting will only take effect if Network VLAN Voice Mode is set 
        to Manual.
        Usage: Integer (1..4094), a vlaid VLAN id, Requires user role: ADMIN, USER"""
        
        payload = f"<Configuration>\r\n\t<Network>\r\n\t\t<VLAN>\r\n\t\t<Voice>\r\n\t\t<VlanId>{vlan_id}</VlanId>\r\n\t</Voice>\r\n\t</VLAN>\r\n\t</Network>\r\n</Configuration>"
        return self.__post_parser_return(payload,output_debug)
    
    def set_network_qos_diffserv_ntp(self,ntp_priority:int=0,output_debug:bool=False):
        """Description: This setting takes effect only if Network QoS Mode is set to Diffserv.
        Define which priority NTP packets should have in the IP network. The traffic classes recomended in the DiffServ RFCs map to a decimal value between 0 and 63. We recommend you 
        use 0 for NTP.
        The priority set here might be overridden when packets are leaving the network controlled by 
        the local network administrator
        Usage:  Integer (0..63) a set priority, 0 means 'best-effort', Requires user role: ADMIN, USER"""
        
        payload = f"<Configuration>\r\n\t<Network>\r\n\t\t<QoS>\r\n\t\t<Diffserv>\r\n\t\t<NTP>{ntp_priority}</NTP>\r\n\t</Diffserv>\r\n\t</QoS>\r\n\t</Network>\r\n</Configuration>"
        return self.__post_parser_return(payload,output_debug)
    
    def set_network_qos_diffserv_audio(self,audio_priority:int=46,output_debug:bool=False):
        """Description: This setting takes effect only if Network QoS Mode is set to Diffserv.
        Define which priority Audio packets should have in the IP network. The traffic classes recommended in the DiffServ RFCs map to a decimal value between 0 and 63. Cisco recommends you 
        use EF for Audio. EF equals the decimal value 46.
        The priority set here might be overridden when packets are leaving the network controlled by 
        the local network administrator
        Usage: Integer (0..63) , set Audio packet priority, 0 means 'best-effort', Requires user role: ADMIN, USER"""
        
        payload = f"<Configuration>\r\n\t<Network>\r\n\t\t<QoS>\r\n\t\t<Diffserv>\r\n\t\t<Audio>{audio_priority}</Audio>\r\n\t</Diffserv>\r\n\t</QoS>\r\n\t</Network>\r\n</Configuration>"
        return self.__post_parser_return(payload,output_debug)
    
    def set_network_qos_diffserv_video(self,video_priority:int=34,output_debug:bool=False):
        """Description: This setting takes effect only if Network QoS Mode is set to Diffserv.
        Define which priority Video packets should have in the IP network. The packets of the presentation channel (shared content) are also in the Video packet category. The traffic classes 
        recommended in the DiffServ RFCs map to a decimal value between 0 and 63. Cisco recommends 
        you use AF41 for Video. AF41 equals the decimal value 34.
        The priority set here might be overridden when packets are leaving the network controlled by 
        the local network administrator
        Usage: Integer (0..63) , set Video packet priority, 0 means 'best-effort', Requires user role: ADMIN, USER """
        
        payload = f"<Configuration>\r\n\t<Network>\r\n\t\t<QoS>\r\n\t\t<Diffserv>\r\n\t\t<Video>{video_priority}</Video>\r\n\t</Diffserv>\r\n\t</QoS>\r\n\t</Network>\r\n</Configuration>"
        return self.__post_parser_return(payload,output_debug)        
    
    def set_network_qos_diffserv_data(self,data_priority:int=34,output_debug:bool=False):
        """Description: This setting takes effect only if Network QoS Mode is set to Diffserv.
        Define which priority Data packets should have in the IP network. The traffic classes recommended in the DiffServ RFCs map to a decimal value between 0 and 63. Cisco recommends you 
        use AF41 for Data. AF41 equals the decimal value 34.
        The priority set here might be overridden when packets are leaving the network controlled by 
        the local network administrator
        Usage: Integer (0..63) , set Data packet priority, 0 means 'best-effort', Requires user role: ADMIN, USER """
        
        payload = f"<Configuration>\r\n\t<Network>\r\n\t\t<QoS>\r\n\t\t<Diffserv>\r\n\t\t<Data>{data_priority}</Data>\r\n\t</Diffserv>\r\n\t</QoS>\r\n\t</Network>\r\n</Configuration>"
        return self.__post_parser_return(payload,output_debug)        
    
    def set_network_qos_diffserv_signalling(self,signalling_priority:int=24,output_debug:bool=False):
        """Description: This setting takes effect only if Network QoS Mode is set to Diffserv.
        Define which priority Signalling packets that are deemed critical (time-sensitive) for the real time operation should have in the IP network. The traffic classes recommended in the DiffServ 
        RFCs map to a decimal value between 0 and 63. Cisco recommends you use CS3 for Signalling. 
        CS3 equals the decimal value 24.
        The priority set here might be overridden when packets are leaving the network controlled by 
        the local network administrator
        Usage: Integer (0..63) , set Signalling packet priority, 0 means 'best-effort', Requires user role: ADMIN, USER"""
        
        payload = f"<Configuration>\r\n\t<Network>\r\n\t\t<QoS>\r\n\t\t<Diffserv>\r\n\t\t<Signalling>{signalling_priority}</Signalling>\r\n\t</Diffserv>\r\n\t</QoS>\r\n\t</Network>\r\n</Configuration>"
        return self.__post_parser_return(payload,output_debug)    
    
    def command_audioDiagnose_MeasureDelay(self,output_debug=False):
        payload = "<Command>\r\n\t<Audio>\r\n\t\t<Diagnostics>\r\n \t\t\t<MeasureDelay></MeasureDelay>\r\n \t\t</Diagnostics>\r\n\t</Audio>\r\n</Command>"
        return self.__command_parser_return(payload) 
    
    def command_music_mode(self):
        """Description: Start using MusicMode in the current call. Music mode allows the dynamic range of music go 
        through. When Music mode is in use, sound level variations are transmitted intact and the noise 
        filtering is kept to a minimum. MusicMode is automatically turned off when the call ends.
        Usage: Requires user role: ADMIN, INTEGRATOR, USER"""
        
        payload = "<Command>\r\n\t<Audio>\r\n\t\t<Microphones>\r\n\t\t\t<MusicMode><Start></Start></MusicMode>\r\n\t\t</Microphones>\r\n\t</Audio>\r\n</Command>"
        return self.__command_parser_return(payload)
    
    def command_activate_NoiseRemoval(self,mode:str):
        """Description: Activate noise removal on the device.
        Usage: Supply Activate to activate the Noise removal feature, Deactivate to deactivate the noise removal. Requires user role: ADMIN, INTEGRATOR, USER 
        Note that Noise removal mode should be set to enable to use this feature. Use : to activate"""
        payload = f"<Command>\r\n\t<Audio>\r\n\t\t<Microphones>\r\n\t\t\t<NoiseRemoval><{mode}></{mode}></NoiseRemoval>\r\n\t\t</Microphones>\r\n\t</Audio>\r\n</Command>"
        return self.__command_parser_return(payload)
    
    def command_microphoneToggle_mute(self):
        """Description: Toggle the microphone between muted and unmuted. Returns result along with Microphones Mute status.
        Usage:Requires user role: ADMIN, INTEGRATOR, USER"""
        payload = "<Command>\r\n\t<Audio>\r\n\t\t<Microphones>\r\n\t\t\t<ToggleMute></ToggleMute>\r\n\t\t</Microphones>\r\n\t</Audio>\r\n</Command>"
        print (self.__command_parser_return(payload))
        return self.get_status_audio_input_microphone_mute()
    
    
    def command_book_meeting(self,BookingId:str,Title:str,Duration:int=30,StartTime:str="Default"):
        """Description: Book the meeting room for the specified period. If you don’t specify the start time and duration, 
        the room will be booked from now on and for 30 minutes. Use get_booking_byID function to confirm if the meeting was scheduled.
        Usage: Requires user role: ADMIN, USER.
        Arguments:
        BookingId:String (1, 128) , A unique identifier for the booking request.
        Duration: Integer (0..1440), The duration of the meeting, in minutes. Default value: 30
        StartTime:String (1, 128), The start time of the meeting in the following UTC format: YYYY-MM-DDThh:mm:ssZ. Example: 2022-07-20T01:29:00Z.
        Title:String (1, 128), The title or subject field in the calendar booking. It will also be displayed on screen in the today’s bookings list."""
        
        __current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        if StartTime == "Default":
            StartTime = __current_time
        payload = f"<Command>\r\n\t<Bookings>\r\n\t\t<Book>\r\n\t\t\t<BookingRequestUUID>{BookingId}</BookingRequestUUID><Duration>{Duration}</Duration><StartTime>{StartTime}</StartTime><Title>{Title}</Title>\r\n\t\t</Book>\r\n\t</Bookings>\r\n</Command>"
        return self.__command_parser_return(payload)
    
    def get_booking_byID(self,BookingId:str):
        """Description: Get the booking information for a specific ID.
        Usage: Requires user role: ADMIN, USER. 
        Arguments:
        BookingId:String (1, 128) , A unique identifier used for the booking request."""
                
        payload = f"<Command>\r\n\t<Bookings>\r\n\t\t<Get><Id>{BookingId}</Id></Get>\r\n\t</Bookings>\r\n</Command>"
        return self.__command_parser_return(payload)
    
    def get_bookings_list(self,Days:int,DayOffset:int=0,Limit:int=15,Offset:int=0):
        """Description: Book the meeting room for the specified period. If you don’t specify the start time and duration, 
        the room will be booked from now on and for 30 minutes.
        Usage: Requires user role: ADMIN, USER
        Arguments:
        Days: Integer (1..365), Number of days to retrieve bookings from.
        DayOffset: Integer (0..365), Which day to start the search from (today: 0, tomorrow: 1, …). Default value: 0
        Limit: Integer (1..65534), Max number of bookings to list. Default value: 15
        Offset: Integer (0..65534), Offset number of bookings for this search. Default value: 0
        """
        payload = f"<Command>\r\n\t<Bookings>\r\n\t\t<List>\r\n\t\t\t<Days>{Days}</Days><DayOffset>{DayOffset}</DayOffset><Limit>{Limit}</Limit><Offset>{Offset}</Offset>\r\n\t\t</List>\r\n\t</Bookings>\r\n</Command>"
        return self.__command_parser_return(payload)
    
    def set_bookings_notificationSnooze(self,Id:str,SecondsToSnooze:int=300):
        """Description: Sets notifications for the stored bookings in this device to snooze.
        Usage: Requires user role: ADMIN, USER
        Arguments:
        Id:String (0, 128), The ID of the notification snooze setting.
        SecondsToSnooze:Integer (1..3600), The duration of the snooze period, in seconds. Default value: 300
        """
        payload = f"<Command>\r\n\t<Bookings>\r\n\t\t<NotificationSnooze>\r\n\t\t\t<Id>{Id}</Id><SecondsToSnooze>{SecondsToSnooze}</SecondsToSnooze>\r\n\t\t</NotificationSnooze>\r\n\t</Bookings>\r\n</Command>"
        return self.__command_parser_return(payload)
    
    
        
    def __command_parser_return(self,payload):
        try:
            url = f"http://{self.address}/putxml"
            headers = {
              'Content-Type': 'text/xml',
            }
            response = requests.post(url, headers=headers,auth=HTTPBasicAuth(self.username,self.password), data=payload,verify= self.ssl_verify)
            response_json = jxmlease.parse(response.text)
            if response.status_code == 200:
                if "OK" in response.text:
                    return "OK\n"
                elif "Error" in response.text:
                    print(f"Something went wrong, Couldn't verify the Command.Please check and run again. Returned Error:\n{response_json}")
                    return(response_json)
            else:
                if response.status_code == 401:
                    raise Exception("Authorisation Failed , Please check Credentials\n")
                elif (response.status_code==400):
                    raise Exception("Connection Failed , Please check Connection\n")
                else:
                    raise Exception(f"Error: {response.status_code}")
        except Exception as e:
            return(str(e))
    
    def __post_parser_return(self,payload,output_debug):
        try:
            url = f"http://{self.address}/putxml"
            headers = {
              'Content-Type': 'text/xml',
            }
            response = requests.post(url, headers=headers,auth=HTTPBasicAuth(self.username,self.password), data=payload, verify=self.ssl_verify)
            response_json = jxmlease.parse(response.text)
            if response.status_code == 200:
                if "Success" in response.text:
                    if output_debug:
                        print(response_json)
                    return(response_json)
                elif "Error" in response.text:
                    error = jxmlease.parse(response.text)['Configuration']['Error']['Details']
                    raise Exception(f"Error: {error}")
                else:
                    return(response_json)
            else:
                if response.status_code == 401:
                    raise Exception("Authorisation Failed , Please check Credentials\n")
                elif (response.status_code==400):
                    raise Exception("Connection Failed , Please check Connection\n")
                else:
                    raise Exception(f"Error: {response.status_code}")
        except Exception as e:
            if output_debug:
                print(e)
            return(e)
    
    def __return_type_parser(response,return_type):
        if return_type == "json":
            return jxmlease.parse(response.text)
        elif return_type == "xml":
            return response.text
        else:
            raise Exception("Unidentified return type requested, please choose xml or json")