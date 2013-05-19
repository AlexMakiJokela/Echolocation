from __future__ import division
import wave
import numpy as np
import scipy.signal
import time
import struct
import pyaudio
import collections

def generate_rampswoop(sampling_rate, duration, start_f, end_f, harmonic_start, harmonic_num, cosramp_duration, inverted=False):
    t=np.arange(0,duration,1/sampling_rate)
    t=t[1:]
    start_f=start_f/harmonic_start
    end_f=end_f/harmonic_start

    log_sf=np.log(start_f)
    log_ef=np.log(end_f)
    log_freq=np.arange(0,len(t)+1)
    log_freq=log_freq/max(log_freq)
    log_freq=log_freq*(log_ef-log_sf)
    log_freq=log_freq+log_sf
    freq=np.exp(log_freq)

    phase_cont = 1/sampling_rate * freq * 2 * np.pi

    phase = np.cumsum(phase_cont)

    swoop=np.array(0)

    for i in range(harmonic_start,harmonic_num+1):
        swoop=swoop+(np.cos(i*phase))

    swoop=swoop/max(swoop)

    envelope=np.ones(swoop.shape)
    cosramp_samples = np.round(cosramp_duration*sampling_rate)
    xx=np.linspace(0,np.pi,cosramp_samples)
    cosramp = 0.5 + 0.5*np.cos(xx)
    envelope[0:cosramp_samples]=cosramp[::-1]
    envelope[-cosramp_samples:]=cosramp

    swoop=swoop*envelope
    swoop=swoop.flatten(1)
    if inverted:
        swoop=swoop[::-1]
    #print np.max(swoop), np.min(swoop)
    whole_shebang=collections.defaultdict()
    whole_shebang["chirp"]=swoop
    whole_shebang["sampling_rate"]=sampling_rate
    whole_shebang["duration"]=duration
    whole_shebang["start_f"]=start_f
    whole_shebang["end_f"]=end_f
    whole_shebang["inverted"]=inverted

    return whole_shebang

#highpass butterworth filtering of data x, with sampling rate Fs, and frequency cutoff c.
def highpass_filter(x,Fs,c):
    nyquist = Fs/2.0;
    b,a = scipy.signal.butter(5,c/nyquist,'highpass',output='ba');
    y = scipy.signal.lfilter(b,a,x);
    return y

#lowpass butterworth filtering of data x, with sampling rate Fs, and frequency cutoff c.
def lowpass_filter(x,Fs,c):
    nyquist = Fs/2.0;
    b,a = scipy.signal.butter(5,c/nyquist,'lowpass',output='ba');
    y = scipy.signal.lfilter(b,a,x);
    return y

def process_input_signal(input_signal,F_SAMP_ULTRA,chirp_low_freq,chirp_bandwidth, RECORD_DELAY, chirp_duration, echo_wait, slowdown_ratio): 

    for jj in [0,1]:
        input_signal[:,jj] = highpass_filter(input_signal[:,jj], F_SAMP_ULTRA, 0.9*chirp_low_freq*1000)
        input_signal[:,jj] = lowpass_filter(input_signal[:,jj], F_SAMP_ULTRA, 1.0/0.9 * (chirp_low_freq + chirp_bandwidth)*1000)
    eind = np.floor((RECORD_DELAY*F_SAMP_ULTRA)) #silence in beginning
    
    #Create a rough range around where we expect to see the beginning of the chirp
    cut_range = np.arange(int(eind-2000),int(eind+5000))
    if np.max(cut_range) > input_signal.shape[0]:
        cut_range = cut_range - (np.max(cut_range) - input_signal.shape[0]+1) 
        eind = eind - (np.max(cut_range) - input_signal.shape[0]+1 )
    
    #Take just that range, and normalize it
    msig = np.abs(input_signal[cut_range,:]).max(1)
    msig = np.convolve(msig,np.ones((100)), 'same' )

    #Set mind to the first part where the chirp begins 
    try: 
        mind = np.min( np.where( msig > 12*msig[0] ) )
    except:
        mind = 0

    #Add the cut-out beginning to mind
    mind = mind + (eind-2000)

    #Hey, a little margin never hut anyone
    gd = mind - 50
    
    #How long we expect the whole shebang to last. Or at least the important part of the whole shebang. 
    ACQUISITION_DURATION = echo_wait + chirp_duration*0.001
    ACQ_samp = np.floor(ACQUISITION_DURATION * F_SAMP_ULTRA)
    input_signal_cut = input_signal
     
    #Cut the clip so that it only contains the chirps
    if input_signal.shape[0] > (np.min(gd)+ACQ_samp):
        input_signal_cut = input_signal_cut[np.min(gd):(np.min(gd)+ACQ_samp), : ]  
    else:
        input_signal_cut = input_signal_cut[np.min(gd):]
    #Actually we'll just play it back at this speed
    playback_FS = int(np.floor(F_SAMP_ULTRA / slowdown_ratio))
    return input_signal_cut, playback_FS


#if __name__=='__main__':
#   rs= generate_rampswoop(192000,0.005,25000,25000+48000,1,1,0.0005)
  # sdrate=int(192000/25)


  # p = pyaudio.PyAudio()
  # FORMAT=pyaudio.paInt16
  # CHUNK=2048
  # rsi=rs* 32767 
# # print rs
  # rswave=rsi.astype(np.int)
# # print rswave
  # signal = "".join((wave.struct.pack('h', item) for item in rswave))
# # print signal
# # rsi=rs* 32767 
# # rswave=rsi.astype(np.int)
# # print rswave
  # #wavstr= rs.astype(np.float32).tostring()
# # print wavstr
# # rslist=rs.astype(np.float32).tolist()           #stopping point: GET THE DAMNED FILE TO WRITE PROPER. Jesus.
# # ili=iter(rslist)
  # #scipy.io.wavfile.write("temporary.wav",int(192000/25),rswave)

  # writewav=wave.open("temporary.wav",'wb')
# # writewav.setparams((1,2,sdrate,0,'NONE','Uncompressed'))
  # writewav.setnchannels(1)
  # writewav.setsampwidth(p.get_sample_size(FORMAT))
  # writewav.setframerate(sdrate)
# # wf.writeframes(b''.join(frames))
  # writewav.writeframes(str(signal)) #try tostring
  # writewav.close()

#   time.sleep(2)
#   wf=wave.open("temporary2.wav",'rb')

#   def pcallback(in_data, frame_count, time_info, status):
#       data = wf.readframes(frame_count)
#       print in_data,frame_count, time_info,status
#       print status
#       return (data, pyaudio.paContinue)

#   stream=p.open(format=FORMAT,
#                 channels=wf.getnchannels(),
#                 rate=wf.getframerate(),
#                 output=True,
#                 stream_callback=pcallback)

#   stream.start_stream()

#   while stream.is_active():
#       time.sleep(0.1)
#       print "xx"
#   stream.stop_stream()
#   stream.close()

#   wf.close()
#   p.terminate()

#   print "x"

#   time.sleep(2)
#   wf=wave.open("temporary2.wav",'rb')
#   p = pyaudio.PyAudio()

#   #def callback(in_data, frame_count, time_info, status):
#   #    data = wf.readframes(frame_count)
#   #    return (data, pyaudio.paContinue)

#   stream = p.open(format=FORMAT,
#                 channels=wf.getnchannels(),
#                 rate=wf.getframerate(),
#                 output=True)

#   stream.start_stream()

#   #while stream.is_active():
#   #    time.sleep(0.1)
#   data = wf.readframes(CHUNK)

#   while data != '':
#       stream.write(data)
#       data = wf.readframes(CHUNK)
#       print data

#   stream.close()

#   p.terminate()

#   print "y"
#   time.sleep(2)
#   wf=wave.open("temporary2.wav",'rb')

#   p = pyaudio.PyAudio()
#   def pcallback(in_data, frame_count, time_info, status):
#       data = wf.readframes(frame_count)
#       print in_data,frame_count, time_info,status
#       print status
#       return (data, pyaudio.paContinue)

#   stream=p.open(format=p.get_format_from_width(wf.getsampwidth()),
#                 channels=wf.getnchannels(),
#                 rate=wf.getframerate(),
#                 output=True,
#                 stream_callback=pcallback)

#   stream.start_stream()

#   while stream.is_active():
#       time.sleep(0.1)
#       print "xx"
#   stream.stop_stream()
#   stream.close()

#   wf.close()
#   p.terminate()

