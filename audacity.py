#!/usr/bin/env python
# 2017 kojima changed https://github.com/davidavdav/audacity.py (c) 2016 David A. van Leeuwen
# 
#
# 
import xml.etree.ElementTree as ET
import wave, os, numpy, struct

class Aup:
	def __init__(self, aupfile):
		fqpath = os.path.join(os.path.curdir, aupfile)
		dir = os.path.dirname(fqpath)
		xml = open(aupfile)
		self.tree = ET.parse(xml)
		self.root = self.tree.getroot()
		self.rate = float(self.root.attrib["rate"])
		ns = {"ns":"http://audacity.sourceforge.net/xml/"}
		self.project = self.root.attrib["projname"]
		self.files = []
		self.labels= []
		for channel, wavetrack in enumerate(self.root.findall("ns:wavetrack", ns)):
			track_channel=wavetrack.attrib["channel"]
			aufiles = []
			for b in wavetrack.iter("{%s}simpleblockfile" % ns["ns"]):
				filename = b.attrib["filename"]
				d1 = filename[0:3]
				d2 = "d" + filename[3:5]
				file = os.path.join(dir, self.project, d1, d2, filename)
				if not os.path.exists(file):
					raise IOError("File missing in %s: %s" % (self.project, file))
				else:
					aufiles.append((file, int(b.attrib["len"]),track_channel))
			self.files.append(aufiles)
		for channel, labeltrack in enumerate(self.root.findall("ns:labeltrack", ns)):
			labelset=[]
			for b in labeltrack.iter("{%s}label" % ns["ns"]):
				l=(float(b.attrib["t"]), float(b.attrib["t1"]), b.attrib["title"])
				labelset.append(l)
			self.labels.append(labelset)

		self.nchannels = len(self.files)
		self.aunr = -1

	def open(self, channel):
		if not (0 <= channel < self.nchannels):
			raise ValueError("Channel number out of bounds")
		self.channel = channel
		self.aunr = 0
		self.offset = 0
		return self

	def close(self):
		self.aunr = -1

	## a linear search (not great)
	def seek(self, pos):
		if self.aunr < 0:
			raise IOError("File not opened")
		s = 0
		i = 0
		length = 0
		for i, f in enumerate(self.files[self.channel]):
			s += f[1]
			if s > pos:
				length = f[1]
				break
		if pos >= s:
			raise EOFError("Seek past end of file")
		self.aunr = i
		self.offset = pos - s + length

	def read(self):
		if self.aunr < 0:
			raise IOError("File not opened")
		while self.aunr < len(self.files[self.channel]):
			with open(self.files[self.channel][self.aunr][0],"rb") as fd:
				track_ch=self.files[self.channel][self.aunr][2]
				if track_ch=="0":
					fd.seek((self.offset - self.files[self.channel][self.aunr][1]) * 2, 2)
				else:
					fd.seek((self.offset - self.files[self.channel][self.aunr][1]) * 4, 2)
				data = fd.read()
				yield data,track_ch
			self.aunr += 1
			self.offset = 0

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()

	def get_labels(self, channel):
		if not (0 <= channel <len(self.labels)):
			raise ValueError("Channel number out of bounds")
		return self.labels[channel]

	def towav(self, filename, channel, start=0, stop=None):
		wav = wave.open(filename, "w")
		wav.setnchannels(1)
		wav.setsampwidth(2)
		wav.setframerate(self.rate)
		scale = 1 << 15
		if stop:
			length = int(self.rate * (stop - start)) ## number of samples to extract
		with self.open(channel) as fd: #fd=self
			fd.seek(int(self.rate * start))
			for data,track_ch in fd.read():
				if track_ch=="0":
					shorts = numpy.frombuffer(data, numpy.short)
				else:
					shorts = numpy.short(numpy.clip(numpy.frombuffer(data, numpy.float32) * scale, -scale, scale-1))
				if stop and len(shorts) > length:
					shorts = shorts[range(length)]
				format = "<" + str(len(shorts)) + "h"
				wav.writeframesraw(struct.pack(format, *shorts))
				if stop:
					length -= len(shorts)
					if length <= 0:
						break
			wav.writeframes(bytes(b'')) ## sets length in wavfile
		wav.close()
