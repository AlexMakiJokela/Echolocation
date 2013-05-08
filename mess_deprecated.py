import datetime
import Tkinter as tk
import pyaudio
import time
import sys
import wave





def WireWithCallback():
	WIDTH = 2
	CHANNELS = 2
	RATE = 44100

	p = pyaudio.PyAudio()

	first=True 
	
	howlong=4.6

	def callback(in_data, frame_count, time_info, status):
		current_duration=stream.get_time()-stream.start
		print stream.get_time()
		if current_duration>howlong:
			return (in_data, pyaudio.paComplete)
		else: 
			return (in_data, pyaudio.paContinue)

	stream = p.open(format=p.get_format_from_width(WIDTH),
	                channels=CHANNELS,
	                rate=RATE,
	                input=True,
	                output=True,
	                stream_callback=callback)

	stream.start_stream()
	stream.start=stream.get_time()
#	time.sleep(5)
	while stream.is_active():
	    time.sleep(0.1)

	stream.stop_stream()
	stream.close()

	p.terminate()




def DamnItHowDoCallbacksWorkWithPyAudio(): #obviously this is not going in the final code.


	CHIRP_INPUT_FILENAME="testing.wav"
	swoop=wave.open(CHIRP_INPUT_FILENAME)

	def play_callback(in_data, frame_count, time_info, status):
	    data = swoop.readframes(frame_count)
	    return (data, pyaudio.paContinue)

	pplay=pyaudio.PyAudio()
	outstream=pplay.open(format=pplay.get_format_from_width(swoop.getsampwidth()),
					channels=swoop.getnchannels(),
					rate=swoop.getframerate(),
					output=True,
					stream_callback=play_callback)

	outstream.start_stream()
	while outstream.is_active():
		time.sleep(0.1)
	outstream.stop_stream()
	outstream.close()
	pplay.terminate()


def PlaySwoopFromSpeaker(): #testing
	CHUNK=1024
	swoop=wave.open("chirpexample.wav")
	p=pyaudio.PyAudio()
	stream=p.open(format=p.get_format_from_width(swoop.getsampwidth()),
                channels=swoop.getnchannels(),
                rate=swoop.getframerate(),
                output=True)

	data = swoop.readframes(CHUNK)

	while data != '':
	    stream.write(data)
	    data = swoop.readframes(CHUNK)

	stream.stop_stream()
	stream.close()


def RecordThings():
	CHUNK=1024
	FORMAT=pyaudio.paInt16
	CHANNELS=2
	RATE=44100
	RECORD_SECONDS=5
	WAVE_OUTPUT_FILENAME="testing.wav"

	p=pyaudio.PyAudio()

	stream=p.open(format=FORMAT,
		channels=CHANNELS,
		rate=RATE,
		input=True,
		frames_per_buffer=CHUNK)
	print ("* recording")
	frames=[]
	for i in range(0,int(RATE/CHUNK*RECORD_SECONDS)):
		data=stream.read(CHUNK)
		frames.append(data)
	print ("* done recording")
	stream.stop_stream()
	stream.close()
	p.terminate()
	wf=wave.open(WAVE_OUTPUT_FILENAME,'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()


	#data=swoop.readframes(CHUNK)
	#while data != '':
#		stream.write(data)
#		data=swoop.readframes(CHUNK)
	#stream.stop_stream()
	#stream.close()

	

	# p=pyaudio.PyAudio()

	# stream=p.open(format=FORMAT,
	# 	channels=CHANNELS,
	# 	rate=RATE,
	# 	input=True,
	# 	frames_per_buffer=CHUNK)
	# print ("* recording")
	# frames=[]
	# for i in range(0,int(RATE/CHUNK*RECORD_SECONDS)):
	# 	data=stream.read(CHUNK)
	# 	frames.append(data)
	# print ("* done recording")
	# stream.stop_stream()
	# stream.close()
	# p.terminate()
	# wf=wave.open(WAVE_OUTPUT_FILENAME,'wb')
	# wf.setnchannels(CHANNELS)
	# wf.setsampwidth(p.get_sample_size(FORMAT))
	# wf.setframerate(RATE)
	# wf.writeframes(b''.join(frames))
	# wf.close()



	