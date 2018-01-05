# coding: utf-8
import audacity
import sys
import json
import itertools
import codecs
import re
import os
label_data={}
label_mapping={}
sep=[]
for line in open("convert_split.log"):
	#data2/2017_05_03_04_00_00_start_40dB_x2_pass_00_59_24.aup.wav.0000.wav: 12800 samples (0.80 sec.) [3948200 (246.76s) - 3961000 (247.56s)]
	m= re.match(r'^(.*): .*\[.*\((.*)s\) - .*\((.*)s\)\]',line)
	if m:
		inputfile=m.group(1)
		t0=m.group(2)
		t1=m.group(3)
		sep.append([inputfile,float(t0),float(t1)])

outpath="data_split/"
os.makedirs(outpath,exist_ok=True)

def get_out_wav_filename(aupfilename):
	fname,ext =  os.path.splitext(filename)
	wavfilename=fname+".wav"
	wavbasename=os.path.basename(wavfilename)
	out=outpath+"_".join(wavbasename.split(" "))
	return out
for filename in sys.argv[1:]:
	aup = audacity.Aup(filename)
	out=get_out_wav_filename(filename)
	labels=[]
	for label in aup.get_labels(0):
		t0=label[0]
		t1=label[1]
		l=label[2]
		interval=t1-t0
		if interval<=0.0:
			print("[ERROR]",out,filename)
			continue
		count=0
		for s in sep:
			if s[0].startswith(out):
				#if not (s[2]<t0 or t1<s[1]):#overlap
				if (t0<=s[1] and s[2]<=t1):#including
					labels.append([t0,t1,l,interval,s,count])
					print(t0,t1,l,interval,s,count)
					count+=1
					if l not in label_mapping:
						label_mapping[l]=len(label_mapping)
					mfcc=s[0]+".mfcc.npy"	
					mel=s[0]+".mel.npy"	
					label_data[s[0]]={
						"label":label_mapping[l],
						"label_name":l,#.decode('utf-8'),
						"mel":[mel],
						"mfcc":[mfcc],
						"t0":s[1],
						"t1":s[2]}

with codecs.open("data.split.json","w",'utf-8') as fp:
	fp.write(json.dumps(label_data, indent=4, ensure_ascii=False))

out_label={}
for k,v in label_mapping.items():
	out_label[v]=k
with codecs.open("label.split.json","w",'utf-8') as fp:
	fp.write(json.dumps(out_label, indent=4, ensure_ascii=False))

"""
	print("checking overlap ...." file=sys.stderr)
	for el in itertools.combinations(label_data.items(),2):
		l_1=el[0][1]["label"]
		t0_1=el[0][1]["t0"]
		t1_1=el[0][1]["t1"]
		l_2=el[1][1]["label"]
		t0_2=el[1][1]["t0"]
		t1_2=el[1][1]["t1"]
			print(el[0][0],l_1)
			print(el[1][0],l_2)
			print("======")
	"""
	


