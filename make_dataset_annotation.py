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


outpath="data_annotation/"
os.makedirs(outpath,exist_ok=True)

def get_out_wav_filename(aupfilename):
	fname,ext =  os.path.splitext(filename)
	wavfilename=fname+".wav"
	wavbasename=os.path.basename(wavfilename)
	# removing spaces
	out=outpath+"_".join(wavbasename.split(" "))
	return out


with open("convert_annotation.sh","w") as fp:
	for filename in sys.argv[1:]:
		aup = audacity.Aup(filename)
		fname,ext =  os.path.splitext(filename)
		wavfilename=fname+".wav"
		aup2wavfile(aup,fname)
		out=get_out_wav_filename(filename)
		for label in aup.get_labels(0):
			t0=label[0]
			t1=label[1]
			l=label[2]
			interval=t1-t0
			if interval<=0.0:
				print("[ERROR]",wavfilename)
				continue
			outfilename=out+"_"+str(t0)+"-"+str(t1)+".wav"
			mel=out+"_"+str(t0)+"-"+str(t1)+".mel.npy"
			mfcc=out+"_"+str(t0)+"-"+str(t1)+".mfcc.npy"
			cmd="sox \"%s\" \"%s\" trim %f %f"%(wavfilename,outfilename,t0,interval)
			if l not in label_mapping:
				label_mapping[l]=len(label_mapping)
			label_data[outfilename]={
					"label":label_mapping[l],
					"label_name":l,#.decode('utf-8'),
					"mel":[mel],
					"mfcc":[mfcc],
					"t0":t0,
					"t1":t1}
			fp.write(cmd)
			fp.write("\n")
with codecs.open("data.annotation.json","w",'utf-8') as fp:
	fp.write(json.dumps(label_data, indent=4, ensure_ascii=False))

out_label={}
for k,v in label_mapping.items():
	out_label[v]=k
with codecs.open("label.annotation.json","w",'utf-8') as fp:
	fp.write(json.dumps(out_label, indent=4, ensure_ascii=False))
print("Please run: sh ./convert_annotation.sh")

"""
print("checking overlap ...." file=sys.stderr)
for el in itertools.combinations(label_data.items(),2):
	l_1=el[0][1]["label"]
	t0_1=el[0][1]["t0"]
	t1_1=el[0][1]["t1"]
	l_2=el[1][1]["label"]
	t0_2=el[1][1]["t0"]
	t1_2=el[1][1]["t1"]
	if not (t1_2<t0_1 or t1_1<t0_2):#overlap
		print(el[0][0],l_1)
		print(el[1][0],l_2)
		print("======")
"""



