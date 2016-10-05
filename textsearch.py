#!/usr/bin/env python3

from codecs import open
from os import listdir,stat
from os.path import join as pathjoin,isfile,isdir,splitext
from sys import argv

excludedirs = set('.git .svn __pycache__'.split())
excludeexts = set('.exe .bin .png .jpg .gif .jar .pyc .pyo .pyd .whl .class .war .dll .zip .7z .gz .ttf .afm .eot'.split())
maxfilesize = 1024*1024

search = ' '.join(argv[1:])
print('Text searching for "%s"...' % search)
i = 0
def walkdir(root):
	global i
	files = listdir(root)
	files = set(files) - excludedirs
	files = [f for f in files if splitext(f)[1] not in excludeexts]
	files = [pathjoin(root, f) for f in files]
	dirs,files = [f for f in files if isdir(f)],[f for f in files if isfile(f)]
	#print(dirs, files)
	for f in files:
		if stat(f).st_size > maxfilesize:
			continue
		try:
			with open(f, encoding='ascii', errors='ignore') as r:
				data = r.read()
				index = data.index(search)
				found = '.'.join(data[index-10:index+len(search)+20].split())
				print('%s: %s' % (f.replace('\\','/'), found))
			if i%877:
				print('/-\|'[i%4],end='\r')
			i += 1
		except:
			pass
	for d in dirs:
		walkdir(d)
walkdir('.')
