#author: Cabbache
#19/3/2019

import cv2
import requests
import urllib
import time
import os
from thread import *

def lastIndex(string, char):
	index = -1
	for x in xrange(len(string)):
		if string[x] == char:
			index = x
	return index

def getTags(html):
	html = html.encode('utf-8').strip()
	tagStack = []
	tags = []
	char = 0
	grab = False
	while char < len(html):
		if html[char] == '<' and html[char+1] != '/':
			currTag = ""
			char += 1
			while html[char] != '>':
				currTag += html[char]
				char += 1
			splits = currTag.split('=')
			attrs = []
			for x in xrange(len(splits)-1):
				spac = splits[x].split(' ')
				attrs.append([spac[-1], splits[x+1][0:lastIndex(splits[x+1], ' ')]])
				attrs[-1][1] = attrs[-1][1].replace('"', '')
			tagStack.append([currTag.split(' ')[0], attrs])
		elif html[char:char+2] == "</":
			currTagName = ""
			char += 2
			while html[char] != '>':
				currTagName += html[char]
				char += 1
			tagStack.append([currTagName, False])		
		elif html[char:char+2] == "/>":
			tagStack.pop()
			pass
		char += 1
	return tagStack

def getCamList(country):
	req = requests.get("https://www.skylinewebcams.com/en/webcam/"+country+".html")
	response = req.text
	tags = getTags(response)
	camList = []
	for x in xrange(len(tags)):
		try:
			if tags[x][0] != "li" or tags[x][1][0][0] != "class" or tags[x][1][0][1] != "webcam":
				continue
		except:
			continue
		url = tags[x+1][1][0][1]
		if len(url) < 2:
			continue
		url = "https://www.skylinewebcams.com" + url
		description = tags[x+4][1][2][1] if tags[x+4][0] == "img" else url.split('/')[-1]
		camList.append([url, description])
	return camList

def intSplit(string, deli):
	splits = []
	tmpLine = ""
	for char in string:
		if ord(char) != deli:
			tmpLine += char
			continue
		splits.append(tmpLine)
		tmpLine = ""
	return splits

def getUrls(cookie):
	req2 = requests.get("https://hddn01.skylinewebcams.com/live.m3u8?a="+cookie)
	names = []
	for line in intSplit(req2.text, 10):
		if "https:" in line:
			names.append(line)
	return names

def initSession(camUrl):
	req = requests.get(camUrl)
	sessCookie = req.headers['Set-Cookie'].split(";")[0].split("=")[1]
	return sessCookie

def getStream(cam, sid):
	lastVidNum = 0
	sid = str(sid)
	visited = []
	while True:
		cookie = initSession(cam[0])
		while True:
			urls = getUrls(cookie)
			if len(urls) == 0:
				break
			for url in urls:
				if url in visited:
					continue
				urllib.urlretrieve(url, sid+"vid"+str(lastVidNum)+".ts")
				visited.append(url)
				lastVidNum += 1

print "Getting country list..."
req = requests.get("https://www.skylinewebcams.com/en/webcam.html")
countryList = []
for tag in getTags(req.text):
	try:
		if tag[0] == "a" and tag[1][1][0] == "class" and tag[1][1][1] == "menu-item":
			countryList.append(tag[1][0][1].split('/')[-1].split(".html")[0])
	except:
		continue

for x in xrange(len(countryList)):
	print "["+str(x+1)+"] " + countryList[x]

country = countryList[int(raw_input("Choose country >> "))-1]
num_cams = int(raw_input("Enter num_cams >> "))
decMotion = raw_input("detect motion? [y/n]") == 'y'
print("downloading stream from %s cameras in %s" % (num_cams, country))

cmList = getCamList(country)
for x in xrange(min(num_cams, len(cmList))):
	start_new_thread(getStream, (cmList[x], x,))

caps = []#[[cap, streamId, vidId, open], [...]]
fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
initTime = time.time()
while True:
	for x in range(len(caps)):
		if not caps[x][3]:
			if not os.path.isfile(str(caps[x][1])+"vid"+str(caps[x][2]+2)+".ts"):
				continue
			caps[x][0] = cv2.VideoCapture(str(caps[x][1])+"vid"+str(caps[x][2]+1)+".ts")
			caps[x][2] += 1
			caps[x][3] = True
		ret, frame = caps[x][0].read()
		if not ret:
			caps[x][0].release()
			caps[x][3] = False
			os.remove(str(caps[x][1])+"vid"+str(caps[x][2])+".ts")
			continue
		if decMotion:
			motion = caps[x][4].apply(frame)
			motion = cv2.resize(motion, (400, 300))
			cv2.imshow(cmList[caps[x][1]][1], motion)
		else:
			cv2.imshow(cmList[caps[x][1]][1], cv2.resize(frame, (400, 300)))
		cv2.waitKey(25)
	if time.time() - initTime > 15:#dirty
		continue
	files = os.listdir(".")
	for ts in files:
		name = ts.split(".")
		if len(name) <= 0:
			continue
		if name[-1] != "ts":
			continue
		label = name[0].split("vid")
		if len(label) != 2:
			continue
		streamId = int(label[0])
		vidId = int(label[1])
		there = False
		for x in xrange(len(caps)):
			if caps[x][1] == streamId:
				there = True
				break
		if not there and os.path.isfile(str(streamId)+"vid0.ts") and vidId == 1:
			caps.append([cv2.VideoCapture(str(streamId)+"vid0.ts"), streamId, 0, True, cv2.bgsegm.createBackgroundSubtractorMOG()])

