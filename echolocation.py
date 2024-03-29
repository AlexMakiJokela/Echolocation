import datetime
import Tkinter as tk
import numpy as np
import pyaudio
from scipy.io import wavfile
import collections
import time
import sys
import thread
import Queue
import wave
import mess_deprecated
import echo_sound_functions

#TODO:
#Improve GUI layout
#Add in waveforms to GUI
#Build/test butterworth filter stuff
#Test on actual hardware
#Clean up code


#Oh damn I'm coding drunk!
#Tocheck: Chirp switching logic
#Tocheck: Save wav file for hardcoding silence gap logic
#Tocheck: New chirp logic
#Toset: The L button for switchin' chirps
#GET ON IT.


#taken from effbot.org/zone/tkinter-entry-validate.htm
#modified to only accept numbers
#highly possible that it's not in use

class ValidatingEntry(tk.Entry):
    # base class for validating entry widgets

    def __init__(self, master, value="", **kw):
        apply(tk.Entry.__init__, (self, master), kw)
        self.__value = value
        self.__variable = tk.StringVar()
        self.__variable.set(value)
        self.__variable.trace("w", self.__callback)
        self.config(textvariable=self.__variable)

    def __callback(self, *dummy):
        value = self.__variable.get()
        newvalue = self.validate(value)
        if newvalue is None:
            self.__variable.set(self.__value)
        elif newvalue != value:
            self.__value = newvalue
            self.__variable.set(self.newvalue)
        else:
            self.__value = value

    def validate(self, value):
        # override: return value, new value, or None if invalid
        return value

class MaxLengthEntry(ValidatingEntry):

    def __init__(self, master, value="", maxlength=None, **kw):
        self.maxlength = maxlength
        apply(ValidatingEntry.__init__, (self, master), kw)

    def validate(self, value):
        if self.maxlength is None or ((len(value) <= self.maxlength) and value.isdigit()) or len(value)==0:
            return value
        return None # new value too long




class The_GUI(tk.Frame):
    def __init__(self, master, title="Sonic Eye", start_vol="50",start_slowdown="25",start_dist="3", start_onoff="On", 
                start_automanual="Manual", self_chirpstart="1-Default"):
        tk.Frame.__init__(self,master)
        self.title=title
        self.grid()

        self.onOff=tk.StringVar()
        self.onOff.set(start_onoff)

        self.volume=tk.StringVar() #Volume doesn't do anything yet
        self.volume.set(start_vol)
        
        self.distance=tk.StringVar()
        self.distance.set(start_dist)

        self.slowdown=tk.StringVar()
        self.slowdown.set(start_slowdown)

        self.automanual=tk.StringVar()
        self.automanual.set(start_automanual)

        self.chirpdistancelabel=tk.StringVar()
        self.chirpdistancelabel.set("Play Chirp")

        self.possible_chirps=collections.defaultdict()
        self.possible_chirps["1-Default"]=echo_sound_functions.generate_rampswoop(192000,0.005,25000,52000,1,1,0.0005) 
        self.possible_chirps["2-Long"]=echo_sound_functions.generate_rampswoop(192000,0.02,25000,52000,1,1,0.002)    
        self.possible_chirps["3-Inverted"]=echo_sound_functions.generate_rampswoop(192000,0.005,25000,52000,1,1,0.0005,inverted=True)
        self.possible_chirps["4-Long Inverted"]=echo_sound_functions.generate_rampswoop(192000,0.02,25000,52000,1,1,0.002, inverted=True)
        self.chirp_to_play_name=tk.StringVar()
        self.chirp_to_play_name.set(self_chirpstart)

        self.last_distance=tk.StringVar()
        self.last_distance.set(start_dist)
        self.ultra_in,self.ultra_out,self.head_out=self.get_channels()
        self.channel_list=[self.ultra_in,self.ultra_out,self.head_out]
        self.swoop=self.possible_chirps[self.chirp_to_play_name.get()]
        self.createWidgets()
        master.bind("<Left>",self.DecreaseDistance)   #Set these a little differently
        master.bind("<Right>",self.IncreaseDistance)
        master.bind("<Up>",self.DecreaseSlowdown)
        master.bind("<Down>",self.IncreaseSlowdown)
        master.bind("<minus>",self.DecreaseVolume)
        master.bind("<equal>",self.IncreaseVolume)
        master.bind("c",self.CycleChirp)
        master.bind("1",self.PlayOneMeterChirp)
        master.bind("2",self.PlayThreeMeterChirp)
        master.bind("3",self.PlayTenMeterChirp)
        master.bind("4",self.PlayThirtyMeterChirp)
        master.bind("<space>",self.RepeatLastChirp)
        master.bind("<m>",self.PlayManualDistanceChirp)
        master.bind("<a>",self.AutoManualSwitch)
        master.bind("<o>",self.OnOffSwitch)
        
    def get_channels(self):
        ultra_in=1
        ultra_out=10
        head_out=9
        pa = pyaudio.PyAudio()
        chans=pa.get_device_count()
        for x in range(0,chans):
            nam=pa.get_device_info_by_index(x)['name']
            if 'Line (Juli@ Audio)' in nam:
                ultra_in=x
            if 'Speakers (Juli@ Audio)' in nam:
                ultra_out=x
            if 'GIGAPort HD' in nam:
                head_out=x
        return ultra_in, ultra_out, head_out
        
    def createWidgets(self):
    
        self.OOAMFrame          =tk.Frame(self)
        self.onOffButton        =tk.Button(self, textvariable=self.onOff,command=self.OnOffSwitch,font=('Arial','20'))
        self.onOffStatus        =tk.Label(self)
        self.modeButton         =tk.Button(self, textvariable=self.automanual,width=10,command=self.AutoManualSwitch,font=('Arial','20'))

        self.chirpSelFrame      =tk.Frame(self)
        self.chirpSelTitle      =tk.Label(text="Chirp Type: ",width=12,font=('Arial','20'))
        self.chirpSelText       =tk.Label(textvariable=self.chirp_to_play_name,width=15,font=('Arial','15'))
        self.chirpSwitchButton  =tk.Button(self, text='Change',   command=self.CycleChirp,font=('Arial','15'))    

       # self.volFrame           =tk.Frame(self)
       # self.volText            =tk.Label(textvariable=self.volume,width=2,height=2,font=('Arial','40'))
       # self.volTextInput       =tk.Entry(self,textvariable=self.volume)
       # self.volTextInput       =MaxLengthEntry(self, value=self.volume, maxlength=2,width=4,font=('Arial','40'))
       # self.volUpButton        =tk.Button(self, text='+',font=('Arial','50'),width=2,  command=self.IncreaseVolume)
       # self.volDownButton      =tk.Button(self, text='-',font=('Arial','50'),width=2,  command=self.DecreaseVolume)
        
        self.slowdownFrame      =tk.Frame(self)
        self.slowdownTitle      =tk.Label(text="Slowdown",font=('Arial','30'))
        self.slowdownText       =tk.Label(textvariable=self.slowdown,width=2,font=('Arial','20'))
        self.slowdownUpButton   =tk.Button(self, text='+',  command=self.IncreaseSlowdown,font=('Arial','20'))
        self.slowdownDownButton =tk.Button(self, text='-',  command=self.DecreaseSlowdown,font=('Arial','20'))
        
        self.distanceFrame      =tk.Frame(self)
        self.distanceTitle      =tk.Label(text="Distance",font=('Arial','30'))
        self.distanceText       =tk.Label(textvariable=self.distance,width=2,font=('Arial','20'))
        self.distanceUpButton   =tk.Button(self, text='+',  command=self.IncreaseDistance,font=('Arial','20'))
        self.distanceDownButton =tk.Button(self, text='-',  command=self.DecreaseDistance,font=('Arial','20'))
                

        #self.slowdownTextInput =tk.Entry(self, text='Slowdown')
        #self.slowdownScale         =tk.Scale(self)
        #self.distanceTextInput     =tk.Entry(self, text='dist')
        #self.distanceScale         =tk.Scale(self)
        self.chirpButtonFrame   =tk.Frame(self)
        self.chirpButtonInstr   =tk.Label(textvariable=self.chirpdistancelabel,font=('Arial','20'),width=20)
        self.chirpButton1m      =tk.Button(self.chirpButtonFrame,text='1M',command=self.PlayOneMeterChirp,font=('Arial','12'))
        self.chirpButton3m      =tk.Button(self.chirpButtonFrame,text='3M',command=self.PlayThreeMeterChirp,font=('Arial','12'))
        self.chirpButton10m     =tk.Button(self.chirpButtonFrame,text='10M',command=self.PlayTenMeterChirp,font=('Arial','12'))
        self.chirpButton30m     =tk.Button(self.chirpButtonFrame,text='30M',command=self.PlayThirtyMeterChirp,font=('Arial','12'))
        self.chirpButtonRepeatLast  =tk.Button(self.chirpButtonFrame,text='Repeat Last',command=self.RepeatLastChirp,font=('Arial','12'))
        self.chirpButtonManual  =tk.Button(self.chirpButtonFrame,text='Manual Distance',command=self.PlayManualDistanceChirp,font=('Arial','12'))

        self.OOAMFrame.grid(row=0,column=0,pady=10)
        self.onOffButton.grid(row=0,column=0,padx=5,in_=self.OOAMFrame)
     #   self.modeButton.grid(row=0,column=1,padx=5,in_=self.OOAMFrame)
        
        self.chirpSelFrame.grid(row=1,column=0,pady=20)
        self.chirpSelTitle.grid(row=0,column=0,in_=self.chirpSelFrame)
        self.chirpSelText.grid(row=0,column=1,in_=self.chirpSelFrame)
        self.chirpSwitchButton.grid(row=0,column=2,ipadx=5,in_=self.chirpSelFrame)

       # self.volFrame.grid( row=2,column=0,pady=10)
       # self.volText.grid(column=0,row=0,in_=self.volFrame)
       # self.volUpButton.grid(column=1,row=0,in_=self.volFrame)
       # self.volDownButton.grid(column=1,row=1,in_=self.volFrame)

        self.slowdownFrame.grid(row=2,column=0,pady=10)
        self.slowdownTitle.grid(row=0,column=1,in_=self.slowdownFrame)
        self.slowdownText.grid(row=1,column=1,in_=self.slowdownFrame)
        self.slowdownUpButton.grid(row=1,column=2,ipadx=5,in_=self.slowdownFrame)
        self.slowdownDownButton.grid(row=1,column=0,ipadx=5,in_=self.slowdownFrame)

        self.distanceFrame.grid(row=3,column=0,pady=10)
        self.distanceTitle.grid(row=0,column=1,in_=self.distanceFrame)
        self.distanceText.grid(row=1,column=1,in_=self.distanceFrame)
        self.distanceUpButton.grid(row=1,column=2,ipadx=5,in_=self.distanceFrame)
        self.distanceDownButton.grid(row=1,column=0,ipadx=5,in_=self.distanceFrame)

        self.chirpButtonFrame.grid(column=0,padx=50,pady=30 )
        self.chirpButtonInstr.grid(row=0,column=0, in_=self.chirpButtonFrame)
        self.chirpButton1m.grid(row=0,column=1,in_=self.chirpButtonFrame)
        self.chirpButton3m.grid(row=0,column=2,in_=self.chirpButtonFrame)
        self.chirpButton10m.grid(row=0,column=3,in_=self.chirpButtonFrame)
        self.chirpButton30m.grid(row=0,column=4,in_=self.chirpButtonFrame)
        self.chirpButtonRepeatLast.grid(row=0,column=5,in_=self.chirpButtonFrame)
        self.chirpButtonManual.grid(row=0,column=6,in_=self.chirpButtonFrame)


    def OnOffSwitch(self, event = None):
        onoff=self.onOff.get()
        if onoff=="On":
            self.onOff.set("Off")
        elif onoff=="Off":
            self.onOff.set("On")
        else:
            self.onOff.set("PROBLEM")

    def AutoManualSwitch(self, event = None):
        automanual=self.automanual.get()
        if automanual=="Manual":
            self.automanual.set("Automatic")
            self.chirpdistancelabel.set("Set Chirp Distance")
      #      self.gofullauto()
        elif automanual=="Automatic":
            self.automanual.set("Manual")
            self.chirpdistancelabel.set("Play Chirp")
        else:
            self.automanual.set("PROBLEM")

  #  def gofullauto(self, event= None):
   #     automanual=self.automanual.get()
   #     while automanual=='Automatic':
   #         self.PlayManualDistanceChirp()
   #         automanual=self.automanual.get()
            
    def CycleChirp(self, event = None):
        ctpn=self.chirp_to_play_name.get()
        for i,chirp in enumerate(sorted(self.possible_chirps.keys())):
            if ctpn==chirp:
                if i<len(self.possible_chirps)-1:
                    newchirptoget=sorted(self.possible_chirps.keys())[i+1]
                else:
                    newchirptoget=sorted(self.possible_chirps.keys())[0]
                self.chirp_to_play_name.set(newchirptoget)
        self.swoop=self.possible_chirps[self.chirp_to_play_name.get()]

    def IncreaseVolume(self, event = None):
        volume=int(self.volume.get())
        if volume < 100:
            self.volume.set(str(volume+1))
        else:
            pass

    def DecreaseVolume(self, event = None):
        volume=int(self.volume.get())
        if volume > 0:
            self.volume.set(str(volume-1))
        else:
            pass

    def IncreaseDistance(self, event = None):
        distance=int(self.distance.get())
        if distance < 100:
            self.distance.set(str(distance+1))
        else:
            pass

    def DecreaseDistance(self, event = None):
        distance=int(self.distance.get())
        if distance > 0:
            self.distance.set(str(distance-1))
        else:
            pass

    def IncreaseSlowdown(self, event = None):
        slowdown=int(self.slowdown.get())
        if slowdown < 100:
            self.slowdown.set(str(slowdown+1))
        else:
            pass

    def DecreaseSlowdown(self, event = None):
        slowdown=int(self.slowdown.get())
        if slowdown > 0:
            self.slowdown.set(str(slowdown-1))
        else:
            pass
        
    def PlayManualDistanceChirp(self, event = None):
        distance=int(self.distance.get())
        slowdown=int(self.slowdown.get())
        EchoAndPlayback(self.swoop,distance,slowdown,self.channel_list)
        self.last_distance.set(str(distance))

    def PlayOneMeterChirp(self, event = None):
        onoff=self.onOff.get()
        if onoff=="On":
            automanual=self.automanual.get()
            if automanual=='Manual':
                slowdown=int(self.slowdown.get())
                EchoAndPlayback(self.swoop,1,slowdown,self.channel_list)
            elif automanual=='Automatic': 
                self.distance.set(str(1))
            self.last_distance.set("1")

    def PlayThreeMeterChirp(self, event = None):
        onoff=self.onOff.get()
        if onoff=="On":
            automanual=self.automanual.get()
            if automanual=='Manual':
                slowdown=int(self.slowdown.get())
                EchoAndPlayback(self.swoop,3,slowdown,self.channel_list)
            elif automanual=='Automatic': 
                self.distance.set(str(3))
            self.last_distance.set("3")

    
    def PlayTenMeterChirp(self, event = None):
        onoff=self.onOff.get()
        if onoff=="On":
            automanual=self.automanual.get()
            if automanual=='Manual':
                slowdown=int(self.slowdown.get())
                EchoAndPlayback(self.swoop,10,slowdown,self.channel_list)
            elif automanual=='Automatic': 
                self.distance.set(str(10))
            self.last_distance.set("10")

    
    def PlayThirtyMeterChirp(self, event = None):
        onoff=self.onOff.get()
        if onoff=="On":
            automanual=self.automanual.get()
            if automanual=='Manual':
                slowdown=int(self.slowdown.get())
                EchoAndPlayback(self.swoop,30,slowdown,self.channel_list)
            elif automanual=='Automatic': 
                self.distance.set(str(30))
            self.last_distance.set("30")

    def RepeatLastChirp(self, event = None):
        onoff=self.onOff.get()
        if onoff=="On":
            automanual=self.automanual.get()
            if automanual=='Manual':
                slowdown=int(self.slowdown.get())
                last_dist=int(self.last_distance.get())
                EchoAndPlayback(self.swoop,last_dist,slowdown,self.channel_list)
    



def EchoAndPlayback(swoopdict,echo_distance, slowdown, channel_list): #also incorporate chirp type, slowdown, volume. Pass in the chirp as a variable instead of reading from file each time
    #SILENCE_LENGTH = 0.08 # the end of the chirp gets cut off if not for this
    #PLAY_DELAY = 0 # pause this long at the beginning
    # if we want to generate a harmonic stack instead of a single frequency
    #HARMONIC_START = 1
    #HARMONIC_END = 1
    #RECORD_DELAY = 0.75
    print "Echo",echo_distance,slowdown
    echo_wait = echo_distance * 2 /313.3
    ultra_in=channel_list[0]
    ultra_out=channel_list[1]
    head_out=channel_list[2]
    #Chirp output settings

    CHIRP_INPUT_FILENAME="swoop.wav"
    the_recording=[]


    swoop=swoopdict["chirp"]
    
    #Microphone input settings
    FORMAT=pyaudio.paInt16
    CHANNELS=2
    F_SAMP_ULTRA = 192000
    F_SAMP_HEAD = 44100
    SILENCE_LENGTH = 0.08
    PLAY_DELAY = 0.0
    RECORD_DELAY=0.120 #based on empirical evidence - see echo_1_bp.wav, echo_3_bp.wav, etc
    LAST_CHIRP_FILENAME="current_echo.wav"
    CHUNK=4096
    chirp_duration = swoopdict["duration"] #bats are 2e-3 to 5e-3
    chirp_low_freq = swoopdict["start_f"]
    chirp_bandwidth = swoopdict["end_f"]-swoopdict["start_f"] #bat minimum is around 2.5e4 to 3e4 in those bats which chirp
    print swoop.shape
    swoop=np.hstack((np.zeros(np.ceil(F_SAMP_ULTRA*PLAY_DELAY)),swoop,np.zeros(np.ceil(F_SAMP_ULTRA*(SILENCE_LENGTH+echo_wait)))))
    swoop=swoop*32767
    swoop=swoop.astype(np.int16)
    print swoop.shape
    writewav=wave.open(CHIRP_INPUT_FILENAME,'wb')
    writewav.setnchannels(1)
    writewav.setframerate(F_SAMP_ULTRA)
    writewav.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
    writewav.writeframes(swoop.tostring())
    writewav.close()
    
    
    
    def play_callback(in_data, frame_count, time_info, status):
        data = chirp.readframes(frame_count)
        return (data, pyaudio.paContinue)

    # def record_callback(in_data, frame_count, time_info, status):
        # current_duration=instream.get_time()-instream.start
        # the_recording.append(in_data)
        # print in_data
        # print current_duration
        # if current_duration>echo_wait:
            # return (in_data, pyaudio.paComplete)
        # else: 
            # return (in_data, pyaudio.paContinue)
            
    chirp=wave.open(CHIRP_INPUT_FILENAME)
    pplay=pyaudio.PyAudio()
    precord=pyaudio.PyAudio()
    frames=[]
    outstream=pplay.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=F_SAMP_ULTRA,
                    output=True,
                    output_device_index=ultra_out,
                    stream_callback=play_callback)#3,
                    #3stream_callback=play_callback)

    instream=precord.open(format=pyaudio.paFloat32,
        channels=CHANNELS,
        rate=F_SAMP_ULTRA,
        input=True,
        input_device_index=ultra_in)
    print "1-",time.clock()
    outstream.start_stream()
    print "2-",time.clock()
    instream.start_stream()
    print "3-",time.clock()
    print "Playing chirp and recording...",echo_distance,slowdown
#   time.sleep(2)
    elapsed=0.0
    tic=time.clock()
    print "4-",time.clock()
    while outstream.is_active():
        data=instream.read(CHUNK)
        frames.append(data)
        toc=time.clock()
        elapsed=toc-tic
#       time.sleep(0.05)

    print "5-",time.clock()
    instream.stop_stream()
    instream.close()
    outstream.stop_stream()
    outstream.close()
    pplay.terminate()
    precord.terminate()
    chirp.close()
  #  print np.max(frames),np.min(frames)
  #  print len(frames)
   # print "x"
    #print the_recording
    frames=b''.join(frames)
  #  print len(frames)
    frames=np.fromstring(frames, dtype=np.float32)
    #frames=frames/32767.0
    #print frames
    frames=frames.reshape((-1,2))


    #SAVE TO FILE: just here for figuring out cutoff timing
    tosave=frames*32767
    tosave=tosave.astype(np.int16)
    tosave=tosave.tostring()
    wavfilnam="chirp_samples/echo_"+str(echo_distance)+"_bp.wav"
    savewave=wave.open(wavfilnam,"wb")
    savewave.setnchannels(2) ##MIGHT BE 1
    savewave.setframerate(F_SAMP_ULTRA)
    savewave.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    savewave.writeframes(tosave)
    savewave.close()
    #print np.max(frames),np.min(frames)
   # print frames
    #time.sleep(20)
 #   print frames
#   input_signal=frames
    outputsignal,playback_FS=echo_sound_functions.process_input_signal(frames,F_SAMP_ULTRA,chirp_low_freq,chirp_bandwidth, RECORD_DELAY, chirp_duration, echo_wait, slowdown)
 #   print "zz"
    outputsignal=outputsignal*32767
    outputsignal=outputsignal.astype(np.int16)
    #print np.max(outputsignal),np.min(outputsignal)
    frames=outputsignal.tostring()

    #Save the files after processing
    wavfilnam="chirp_samples/echo_"+str(echo_distance)+"_cp.wav"
    savewave=wave.open(wavfilnam,"wb")
    savewave.setnchannels(2) ##MIGHT BE 1
    savewave.setframerate(F_SAMP_ULTRA)
    savewave.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    savewave.writeframes(tosave)
    savewave.close()
   # p=pyaudio.PyAudio()
   # wf = wave.open(LAST_CHIRP_FILENAME, 'wb')
   # wf.setnchannels(CHANNELS)
   # wf.setsampwidth(p.get_sample_size(FORMAT))
   # wf.setframerate(playback_FS)
   # wf.writeframes(frames)
   # wf.close()
   # wf=wave.open(LAST_CHIRP_FILENAME, 'rb')
    CHUNK=4096
    p=pyaudio.PyAudio()
    stream=p.open(format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=playback_FS,
                output=True,
                output_device_index=head_out)

    #data = wf.readframes(CHUNK)
    print "playing"
    #while data != '':
    stream.write(frames)
    print "done"
    #    data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()
    p.terminate()
    #time.sleep( max([0,size(input_signal_cut,1)/playback_FS - ACQUISITION_DURATION - SILENCE_LENGTH - PLAY_DELAY - RECORD_DELAY]) - PROC_DELAY )


def create_swoop_chirp():
    rs= echo_sound_functions.generate_rampswoop(192000,0.005,25000,52000,1,1,0.0005)      
    return rs

def create_long_swoop():
    rs= echo_sound_functions.generate_rampswoop(192000,0.020,25000,52000,1,1,0.002)      
    return rs

def create_inv_swoop():
    rs= echo_sound_functions.generate_rampswoop(192000,0.005,25000,52000,1,1,0.0005, inverted=True)      
    return rs

def create_long_inv_swoop():
    rs= echo_sound_functions.generate_rampswoop(192000,0.020,25000,52000,1,1,0.002, inverted=True)    
    return rs

if __name__=="__main__":
    root=tk.Tk()
    the_gui=The_GUI(root,title="Sonic Eye")
    the_gui.mainloop()


