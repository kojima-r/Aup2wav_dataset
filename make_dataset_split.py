# coding: utf-8
import audacity
import sys
import json
import itertools
import codecs
import os
label_data={}
label_mapping={}
if len(sys.argv)<2:
	print("usage: python make_dataset.py <*.aup>")
	quit
def aup2wavfile(aup,filename):
	channel=0
	with aup.open(channel) as fd:
		data = fd.read()
	print("[SAVE]",wavfilename, file=sys.stderr)
	aup.towav(wavfilename,channel, start=0, stop=None)

outpath="data_split/"
os.makedirs(outpath,exist_ok=True)

def get_out_wav_filename(aupfilename):
	fname,ext =  os.path.splitext(filename)
	wavfilename=fname+".wav"
	wavbasename=os.path.basename(wavfilename)
	# removing spaces
	out=outpath+"_".join(wavbasename.split(" "))
	return out

with open("convert_split.sh","w") as fp:
	for filename in sys.argv[1:]:
		fname,ext =  os.path.splitext(filename)
		wavfilename=fname+".wav"
		if ext==".aup":
			aup = audacity.Aup(filename)
			aup2wavfile(aup,wavfilename)
		out=get_out_wav_filename(filename)
		#cmd="echo \""+wavfilename+"\" | adintool -out file -filename "+out+" -lv 1000 -zc 300 -in file"
		cmd="echo \""+wavfilename+"\" | adintool -out file -filename "+out+" -lv 400 -zc 200 -in file"
		fp.write(cmd)
		fp.write("\n")

print("Please run: sh ./convert_split.sh > convert_split.log")
