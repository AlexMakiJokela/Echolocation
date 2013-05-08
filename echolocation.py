import datetime
import Tkinter as tk
import pyaudio
import collections
import time
import sys
import wave
import mess_deprecated

#TODO:
#Improve GUI layout
#Add in waveforms to GUI
#Build/test butterworth filter stuff
#Test on actual hardware
#Clean up code





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
	def __init__(self, master, title="Sonic Eye", start_vol="50",start_slowdown="2",start_dist="3", start_onoff="Off", 
				start_automanual="Manual", self_chirpstartnum="0"):
		tk.Frame.__init__(self,master)
		self.title=title
		self.grid()

		self.onOff=tk.StringVar()
		self.onOff.set(start_onoff)

		self.volume=tk.StringVar()
		self.volume.set(start_vol)
		
		self.distance=tk.StringVar()
		self.distance.set(start_dist)

		self.slowdown=tk.StringVar()
		self.slowdown.set(start_slowdown)

		self.automanual=tk.StringVar()
		self.automanual.set(start_automanual)

		self.chirpdistancelabel=tk.StringVar()
		self.chirpdistancelabel.set("Set Chirp Distance")

		self.possible_chirps=collections.defaultdict()
		self.chirplist=["PLAYBACK"]
		self.possible_chirps["PLAYBACK"]="playbackexample.wav"
		self.chirp_to_play_num=tk.StringVar()
		self.chirp_to_play_name=tk.StringVar()
		self.chirp_to_play_num.set(self_chirpstartnum)
		self.chirp_to_play_name.set(self.chirplist[int(self.chirp_to_play_num.get())])
		if self.chirp_to_play_name.get() in self.possible_chirps:
			self.chirp_to_play_sound=wave.open(self.possible_chirps[self.chirplist[int(self.chirp_to_play_num.get())]])
		else:
			self.chirp_to_play_name.set("Default")
			self.chirp_to_play_sound=wave.open("some_filename.wav") #fix later

		self.last_distance=tk.StringVar()
		self.last_distance.set(start_dist)

		self.createWidgets()
		master.bind("<Left>",self.DecreaseDistance)
		master.bind("<Right>",self.IncreaseDistance)
		master.bind("<Up>",self.DecreaseSlowdown)
		master.bind("<Down>",self.IncreaseSlowdown)
		master.bind("<minus>",self.DecreaseVolume)
		master.bind("<equal>",self.IncreaseVolume)
		master.bind("<c>",self.CycleChirp)
		master.bind("<1>",self.PlayOneMeterChirp)
		master.bind("<2>",self.PlayThreeMeterChirp)
		master.bind("<3>",self.PlayTenMeterChirp)
		master.bind("<4>",self.PlayThirtyMeterChirp)
		master.bind("<space>",self.RepeatLastChirp)
		master.bind("<m>",self.PlayManualDistanceChirp)
		master.bind("<a>",self.AutoManualSwitch)
		master.bind("<o>",self.OnOffSwitch)
		

#ERASE LATER - STATUS is working on getting the tk.button to update in real time based on the tk boolean var onOff

	def createWidgets(self):

		self.onOffButton		=tk.Button(self, textvariable=self.onOff,command=self.OnOffSwitch,relief=tk.SUNKEN)
		self.onOffStatus		=tk.Label(self)
		self.modeButton			=tk.Button(self, textvariable=self.automanual,command=self.AutoManualSwitch)

		self.chirpSelFrame		=tk.Frame(self)
		self.chirpSelText		=tk.Label(textvariable=self.chirp_to_play_name,width=2,height=2,font=('Arial','40'))
		self.chirpSwitchButton	=tk.Button(self, text='Switch Chirp',	command=self.CycleChirp)	

		self.volFrame			=tk.Frame(self)
		self.volText	 		=tk.Label(textvariable=self.volume,width=2,height=2,font=('Arial','40'))
#		self.volTextInput		=tk.Entry(self,textvariable=self.volume)
#		self.volTextInput		=MaxLengthEntry(self, value=self.volume, maxlength=2,width=4,font=('Arial','40'))
		self.volUpButton		=tk.Button(self, text='+',font=('Arial','50'),width=2,height=2,	command=self.IncreaseVolume)
		self.volDownButton		=tk.Button(self, text='-',font=('Arial','50'),width=2,			command=self.DecreaseVolume)
		
		self.slowdownFrame		=tk.Frame(self)
		self.slowdownText		=tk.Label(textvariable=self.slowdown,width=2,height=2,font=('Arial','40'))
		self.slowdownUpButton	=tk.Button(self, text='+',	command=self.IncreaseSlowdown)
		self.slowdownDownButton	=tk.Button(self, text='-',	command=self.DecreaseSlowdown)
		
		self.distanceFrame		=tk.Frame(self)
		self.distanceText		=tk.Label(textvariable=self.distance,width=2,height=2,font=('Arial','40'))
		self.distanceUpButton	=tk.Button(self, text='+',	command=self.IncreaseDistance)
		self.distanceDownButton	=tk.Button(self, text='-',	command=self.DecreaseDistance)
				

		#self.slowdownTextInput	=tk.Entry(self, text='Slowdown')
		#self.slowdownScale 		=tk.Scale(self)
		#self.distanceTextInput 	=tk.Entry(self, text='dist')
		#self.distanceScale 		=tk.Scale(self)
		self.chirpButtonFrame   =tk.Frame(self)
		self.chirpButtonInstr	=tk.Label(textvariable=self.chirpdistancelabel)
		self.chirpButton1m 		=tk.Button(self.chirpButtonFrame,text='1M',command=self.PlayOneMeterChirp)
		self.chirpButton3m 		=tk.Button(self.chirpButtonFrame,text='3M',command=self.PlayThreeMeterChirp)
		self.chirpButton10m 	=tk.Button(self.chirpButtonFrame,text='10M',command=self.PlayTenMeterChirp)
		self.chirpButton30m 	=tk.Button(self.chirpButtonFrame,text='30M',command=self.PlayThirtyMeterChirp)
		self.chirpButtonRepeatLast 	=tk.Button(self.chirpButtonFrame,text='Repeat Last',command=self.RepeatLastChirp)
		self.chirpButtonManual 	=tk.Button(self.chirpButtonFrame,text='Manual Distance',command=self.PlayManualDistanceChirp)

		self.onOffButton.grid(row=0,column=0)
		self.modeButton.grid(row=0,column=1)
		
		self.chirpSelFrame.grid(row=1,column=0,pady=30)
		self.chirpSelText.grid(column=0,in_=self.chirpSelFrame)
		self.chirpSwitchButton.grid(column=1,row=0,ipadx=5,in_=self.chirpSelFrame)

		self.volFrame.grid(	row=2,column=0,pady=30)
		self.volText.grid(column=0,row=0,in_=self.volFrame)
		self.volUpButton.grid(column=1,row=0,in_=self.volFrame)
		self.volDownButton.grid(column=1,row=1,in_=self.volFrame)

		self.slowdownFrame.grid(row=3,column=0,pady=30)
		self.slowdownText.grid(column=0,in_=self.slowdownFrame)
		self.slowdownUpButton.grid(column=1,row=0,ipadx=5,in_=self.slowdownFrame)
		self.slowdownDownButton.grid(column=1,row=1,padx=20,in_=self.slowdownFrame)

		self.distanceFrame.grid(row=4,column=0,pady=30)
		self.distanceText.grid(column=0,in_=self.distanceFrame)
		self.distanceUpButton.grid(column=1,row=0,padx=20,in_=self.distanceFrame)
		self.distanceDownButton.grid(column=1,row=1,padx=20,in_=self.distanceFrame)

		self.chirpButtonFrame.grid(column=0,padx=50)
		self.chirpButtonInstr.grid(row=0,column=0,columnspan=4, in_=self.chirpButtonFrame)
		self.chirpButton1m.grid(row=1,column=0,in_=self.chirpButtonFrame)
		self.chirpButton3m.grid(row=1,column=1,in_=self.chirpButtonFrame)
		self.chirpButton10m.grid(row=1,column=2,in_=self.chirpButtonFrame)
		self.chirpButton30m.grid(row=1,column=3,in_=self.chirpButtonFrame)
		self.chirpButtonRepeatLast.grid(row=2,column=0,columnspan=4,in_=self.chirpButtonFrame)


	def OnOffSwitch(self, event = None):
		onoff=self.onOff.get()
		if onoff=="On":
			self.onOff.set("Off")
		elif onoff=="Off":
			self.onOff.set("On")
		else:
			self.onOff.set("PROBLEM")

	def AutoManualSwitch(self, event = None):
		onoff=self.automanual.get()
		if onoff=="Manual":
			self.automanual.set("Automatic")
			self.chirpdistancelabel.set("Set Chirp Distance")
		elif onoff=="Automatic":
			self.automanual.set("Manual")
			self.chirpdistancelabel.set("Play Chirp")
		else:
			self.automanual.set("PROBLEM")

	def CycleChirp(self, event = None):
		chirpnum=int(self.chirp_to_play_num.get())
		if chirpnum>=(len(self.possible_chirps)-1):
			chirpnum=0
		else:
			chirpnum+=1
		self.chirp_to_play_num.set(str(chirpnum))
		self.chirp_to_play_name.set(self.chirplist[int(self.chirp_to_play_num.get())])
		if self.chirp_to_play_name.get() in self.possible_chirps:
			self.chirp_to_play_sound=wave.open(self.possible_chirps[self.chirplist[int(self.chirp_to_play_num.get())]])
		else:
			self.chirp_to_play_name.set("Default")
			self.chirp_to_play_sound=wave.open("some_filename.wav") #fix later

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
		EchoAndPlayback(self.chirp_to_play_sound,distance,slowdown)
		self.last_distance.set(str(distance))

	def PlayOneMeterChirp(self, event = None):
		slowdown=int(self.slowdown.get())
		EchoAndPlayback(self.chirp_to_play_sound,1,slowdown)
		self.last_distance.set("1")

	def PlayThreeMeterChirp(self, event = None):
		slowdown=int(self.slowdown.get())
		EchoAndPlayback(self.chirp_to_play_sound,3,slowdown)
		self.last_distance.set("3")
	
	def PlayTenMeterChirp(self, event = None):
		slowdown=int(self.slowdown.get())
		EchoAndPlayback(self.chirp_to_play_sound,10,slowdown)
		self.last_distance.set("10")
	
	def PlayThirtyMeterChirp(self, event = None):
		slowdown=int(self.slowdown.get())
		EchoAndPlayback(self.chirp_to_play_sound,30,slowdown)
		self.last_distance.set("30")

	def RepeatLastChirp(self, event = None):
		slowdown=int(self.slowdown.get())
		EchoAndPlayback(self.chirp_to_play_sound,last_dist,slowdown)
	


def GenerateTheChirp():
	#If swoop, return the rampswoop with the right parameters
	#or white noise
	#etcetera
	#eventually just do this all in memory. For now, balls to pyaudio's callback convolutedness.
	return




def EchoAndPlayback(swoop,echo_distance, slowdown): #also incorporate chirp type, slowdown, volume. Pass in the chirp as a variable instead of reading from file each time
	#SILENCE_LENGTH = 0.08 # the end of the chirp gets cut off if not for this
	#PLAY_DELAY = 0 # pause this long at the beginning
	# if we want to generate a harmonic stack instead of a single frequency
	#HARMONIC_START = 1
	#HARMONIC_END = 1
	#RECORD_DELAY = 0.75
	echo_wait = echo_distance * 2 /313.3
	#Chirp output settings

	CHIRP_INPUT_FILENAME="temporary2.wav"
	the_recording=[]

	def play_callback(in_data, frame_count, time_info, status):
	    data = chirp.readframes(frame_count)
	    return (data, pyaudio.paContinue)

	def record_callback(in_data, frame_count, time_info, status):
		current_duration=instream.get_time()-instream.start
		the_recording.append(in_data)
		#print current_duration
		if current_duration>echo_wait:
			return (in_data, pyaudio.paComplete)
		else: 
			return (in_data, pyaudio.paContinue)
	
	#Microphone input settings
	FORMAT=pyaudio.paInt16
	CHANNELS=2
	RATE=44100
	WAVE_OUTPUT_FILENAME="current_echo.wav"
	CHUNK=1024
	chirp=wave.open(CHIRP_INPUT_FILENAME)
	pplay=pyaudio.PyAudio()
	precord=pyaudio.PyAudio()
	outstream=pplay.open(format=pplay.get_format_from_width(chirp.getsampwidth()),
					channels=chirp.getnchannels(),
					rate=chirp.getframerate(),
					output=True)#3,
					#3stream_callback=play_callback)

	instream=precord.open(format=FORMAT,
		channels=CHANNELS,
		rate=RATE,
		input=True,
		stream_callback=record_callback)

	instream.start_stream()
	instream.start=instream.get_time()
	outstream.start_stream()
	print "GO"
	time.sleep(2)
	data = chirp.readframes(CHUNK)

	while data != '':
	    outstream.write(data)
	    data = chirp.readframes(CHUNK)

	while instream.is_active():
		time.sleep(0.05)

	outstream.stop_stream()
	outstream.close()
	instream.stop_stream()
	instream.close()

	pplay.terminate()
	precord.terminate()


	wf=wave.open(WAVE_OUTPUT_FILENAME,'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(precord.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(the_recording))
	wf.close()
	wf=wave.open(WAVE_OUTPUT_FILENAME,'rb')

	CHUNK=1024
	p=pyaudio.PyAudio()
	stream=p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True)

	data = wf.readframes(CHUNK)

	while data != '':
	    stream.write(data)
	    data = wf.readframes(CHUNK)

	stream.stop_stream()
	stream.close()
	


if __name__=="__main__":
	root=tk.Tk()
	the_gui=The_GUI(root,title="Sonic Eye")
	the_gui.mainloop()


