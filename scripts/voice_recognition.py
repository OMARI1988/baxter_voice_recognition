#!/usr/bin/env python

import rospy
import sys

import alsaaudio, wave

import numpy as np
import psw
import gapi
import commands
from ros_mary_tts.srv import *
import baxter_interface
from baxter_interface import CHECK_VERSION
from copy import deepcopy
from std_msgs.msg import (
    Empty,
    Bool,
)
from robot_functions import *
from baxter_demos.msg import obj_hypotheses,action

#------------------------------------------------------------------#
def speak(x):
    rospy.wait_for_service('ros_mary')
    try:
        add_two_ints = rospy.ServiceProxy('ros_mary',ros_mary)
        resp1 = add_two_ints(x)
    except rospy.ServiceException, e:
        print "Service call failed: %s"%e

#------------------------------------------------------------------#
speech = gapi.Speech('sp')
COUNTER = 0

if len(sys.argv)==2:
	if sys.argv[1] in gapi.languages.keys():
		speech.lang = gapi.languages[sys.argv[1]]
	elif sys.argv[1] in gapi.languages.values():
		speech.lang = sys.argv[1]

def handler(fileName):
	global speech,COUNTER
	translator = gapi.Translator(speech.lang, 'en-uk')
	try:
		cfileName = psw.convert(fileName)
		phrase = speech.getText(cfileName)
		import os
		os.remove(fileName)
		os.remove(cfileName)

		all_phrases = {}
		count = 0
		max_key = 0
		max_value = 0
		dictionary_words = ['pick','hello','Lucas','lucas','wake','sleep','work','working','yourself','blue','green','red','near','far','right','left']
		hyp = {}
                hyp['valid_dir_hyp'] = ['left','right','below','above']
                hyp['valid_dis_hyp'] = ['near','far']
                hyp['valid_HSV_hyp'] = ['red','blue','green','yellow','black']
                #commands = {}
                #commands[0] = 'pick up the green object'
                #commands[1] = 'pick up the blue object below the green object'
                #commands[2] = 'pick up the blue object far from the green object'
		for j in phrase:
			all_phrases[count] = {}
			all_phrases[count]['text'] = str(j['text'])
			all_phrases[count]['score'] = 0

			for i in dictionary_words:
				if i in all_phrases[count]['text']:
					all_phrases[count]['score'] += 1

			if max_value < all_phrases[count]['score']:
				max_value = all_phrases[count]['score']
				max_key = count

			print 'phrase '+str(count+1)+' : ',str(j['text']),' score : ',str(all_phrases[count]['score'])

			count += 1
		
		phrase = all_phrases[max_key]['text']
		all_words = phrase.split(' ')
		words = phrase.split(' ')
		for i in range(len(words)):
			words[i] = str(words[i])
			all_words[i] = str(all_words[i])
			print all_words[i]

		print 'the phrase is:',phrase

		if 'wake' in words or 'working' in words:
			speak('Ready to work!, sir.')
			Tuck_arms(False)

		elif 'sleep' in words:
			speak('Going to sleep!, sir.')
			Tuck_arms(True)

		elif 'yourself' in words:
			speak('Welcome to the school of computing! my name is Lucas. Which stands for. Leeds university cognative artificial system. Researchers here in leeds are teaching me how to become a smarter robot! so that I can help humans in their daily activities! One of the many interesting things I can do is, you can ask me to pick up an object and I will pick it up for you! Please try and ask me to pick something!')

		elif 'pick' in words:
			sentence = phrase
			#sentence = commands[COUNTER]
			#COUNTER += 1
	                words = sentence.split(' ')
	                action = ''
	                obj1 = ''
	                obj2 = ''
	                dir_rel = ''
	                dis_rel = ''
                        if 'pick' in words:     action='pick'
                        if 'put' in words:     action='put'
                        
                        look_for_relations = 0
                        for i in words:
                        
                                if look_for_relations:
                                        if i in hyp['valid_dir_hyp']:     dir_rel = i
                                        if i in hyp['valid_dis_hyp']:     dis_rel = i
                                
                                if i in hyp['valid_HSV_hyp'] and look_for_relations == 0:
                                        look_for_relations = 1
                                        obj1 = i
                                elif i in hyp['valid_HSV_hyp'] and look_for_relations == 1:
                                        look_for_relations = 0
                                        obj2 = i
                                        
                        print action,obj1,obj2,dir_rel,dis_rel
                                
                        
	                #print Learn.hyp['valid_HSV_hyp']
	                #print Learn.hyp['valid_dis_hyp']
	                #print Learn.hyp['valid_dir_hyp']
                        pub2.publish([action],[obj1],[obj2],[dir_rel],[dis_rel])

		elif 'lucas' in words or 'hello' in words:
			speak('Hello, sir.')
		
	except Exception, e:
		print "Unexpected error:", sys.exc_info()[0], e
	return True

print 'Speech to text recognition starting ..'

pub2 = rospy.Publisher('/action_from_voice', action, queue_size=1)
#pub2 = rospy.Publisher('obj_manipulation_voice', obj_hypotheses, queue_size=1)
rospy.init_node('Voice_recognition')
mic = psw.Microphone()
print 'sampling...'
sample = np.array(mic.sample(200))
print 'done'

speak('Ready.')
mic.listen(handler, sample.mean(), sample.std())
