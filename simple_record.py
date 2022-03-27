#!/usr/bin/env python3

import queue
import sounddevice as sd
import soundfile as sf
import time
import sys
import os
import uuid
import ffmpeg
import random

import threading


## Text source

class Source():

	def generate_source(filename):
		
		source = open(filename).read().replace("\n", " ").replace("  ", ".")

		excluded = ["(", ")", ":", "_", "-", "[", "]", "»", "«", "º", "ª"]

		parrafos = []

		for parrafo in source.split("."):
			
			palabras = parrafo.split(" ")
			
			while "" in palabras:
				
				palabras.remove("")
				
			parrafo = " ".join(palabras)

			if len(palabras) > 6 and len(palabras) < 20 and all(x not in parrafo for x in excluded) and parrafo[0].isupper():

				parrafos.append(parrafo)

		return parrafos


class Recorder():
	
	sample_rate = 44100
	channels = 1
	file_format = "WAV"
	file_options = "PCM_16"
	
	def __init__(self, path):
		self.filename = path+"/"+str(uuid.uuid4())+".wav"
		self.filename_tmp = path+"/"+str(uuid.uuid4())+"_tmp.wav"
		self.file =  sf.SoundFile(self.filename_tmp, mode='x', samplerate=self.sample_rate, channels=self.channels, subtype=self.file_options)
		self.stream = sd.InputStream(samplerate=self.sample_rate, device=7, channels=self.channels, callback=self.save_block)

	def save_block(self, indata, frames, time, status):
		self.file.write(indata.copy())

	def start(self):
		self.stream.start()
		
	def stop(self):
		self.stream.stop()
		self.stream.close()
		self.file.close()
		


## Main loop 

parrafos = Source.generate_source("text/pg66373.txt")

log = open("record_log.txt", "a")

path = "wav"

start = 167

t_total = 0

#random.shuffle(parrafos)

for parrafo in parrafos[start:]:
	
	done = False
	
	while done == False:

		print(">>>",parrafo)

		v = input("[ ENTER ] Start recording, [ s ] Skip, [ q ] Quit\n> ")
		
		if v == "s":
			done = True
			continue
		
		elif v == "q":
			quit()
			
		r = Recorder(path)
		r.start()
		
		t0 = time.time()
		
		
		v = input("[ ENTER ] Finish recording, [ r ] Redo last sentence, [ q ] Quit\n> ")
		
		r.stop()
		
		t1 = time.time()
		
		if v == "q":
			os.remove(r.filename_tmp)
			quit()

		elif v == "":
			
			if t1-t0 < 1:
				
				print("Too short!")
				
				os.remove(r.filename_tmp)
			
			else:
				
				t_total += t1-t0
			
				done = True
		
				info = ffmpeg.probe(r.filename_tmp)
				
				ffmpeg.input(r.filename_tmp, ss=0.25, t=(float(info['streams'][0]['duration'])-0.5)).output(r.filename, ar=22050).global_args('-loglevel', 'quiet').overwrite_output().run()
				
				os.remove(r.filename_tmp)
				
				log_line = f"{r.filename}|{parrafo}\n"
				
				log.write(log_line)
				
				print("Tiempo total:", t_total)
				
		else:
			
			os.remove(r.filename_tmp)
		
log.close()
		


	
