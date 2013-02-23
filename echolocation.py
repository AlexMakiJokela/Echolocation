import datetime
import Tkinter as tk
import audioop#?
#find python audio libraries

class The_GUI(tk.Frame):
	def __init__(self, master=None):
		tk.Frame.__init__(self,master)
		self.grid()
		self.createWidgets()

	def createWidgets(self):
		self.onOffButton=tk.Button(self, text='On/Off',command=self.quit)
		self.onOffButton.grid()



if __name__=="__main__":
	the_gui=The_GUI()
	the_gui.master.title="Sonic Eye"
	the_gui.mainloop()































# # define some essential parameters
# F_SAMP_ULTRA = 192000
# F_SAMP_HEAD = 44100
# dospecgram = 0


# #parameters adjusted by the gui
# #global echo_distance slowdown_ratio chirp_duration chirp_low_freq chirp_bandwidth keep_running run_once save_filename signal_type

# display_stuff = 1

# #install a better switch here later
# signal_type = 'ramp swoop'
# #signal_type = 'white noise'

# #Was commented out - delete if unnec
# #echo_distance = 10;
# #slowdown_ratio = 20; % how much to time stretch the echoes by
# #chirp_duration = 5;%bats are 2e-3 to 5e-3
# #chirp_low_freq = 25;
# #chirp_bandwidth = 48 - chirp_low_freq;%bat minimum is around 2.5e4 to 3e4 in those bats which chirp



# SILENCE_LENGTH = 0.08 # the end of the chirp gets cut off if not for this
# #SILENCE_LENGTH = 0.005 # the end of the chirp gets cut off if not for this
# #PLAY_DELAY = 1; % pause this long at the beginning, so there's time for audio recordign to start
# PLAY_DELAY = 0 # pause this long at the beginning
# # if we want to generate a harmonic stack instead of a single frequency
# HARMONIC_START = 1
# HARMONIC_END = 1
# #RECORD_DELAY = 0.744;
# RECORD_DELAY = 0.75

# PROC_DELAY = 0 # start recording this much early to avoid blank space between repeats

# keep_running = 0
# run_once = 0
# save_filename = 'test_run' #implement some kind of datestamp

# # start the GUI
# echo_gui=Tkinter.Tk()
# downshift_slider=Tkinter.Scale(echo_gui,from_=0,to=100, command=set_downshift) #Note: Figure out logic for setting variables iteratively here

# #ID_ULTRA_IN = 1;
# #ID_ULTRA_OUT = 2;
# #ID_HEAD_OUT = 2;
# ID_ULTRA_IN = -1
# ID_ULTRA_OUT = -1
# ID_HEAD_OUT = -1
# # set the audio IDs appropriately


# #draw out the gui and audio logic later and port to appropriate python modules




# audinf = audiodevinfo(); #rewrite all the audio stuff
# for i = 1:length(audinf.input)
#     if strfind( audinf.input(i).Name, 'Line (Juli@ Audio)' )
#         ID_ULTRA_IN = audinf.input(i).ID;
#     end
# end
# for i = 1:length(audinf.output)
#     if strfind( audinf.output(i).Name, 'Speakers (Juli@ Audio)' )
#         ID_ULTRA_OUT = audinf.output(i).ID;
#     end
#     if strfind( audinf.output(i).Name, 'GIGAPort HD' ) %'Speakers (High Definition Audio Device)' )
#         ID_HEAD_OUT = audinf.output(i).ID;
#     end
# end