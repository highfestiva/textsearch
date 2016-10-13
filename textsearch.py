#!/usr/bin/env python3

from os import listdir,stat
from os.path import join as pathjoin,isfile,isdir,splitext
from sys import argv,stderr

excludedirs = set('.git .svn __pycache__'.split())
excludeexts = set('.exe .bin .png .jpg .gif .tga .ppm .ico .icns .psd .wav .mp3 .ttf .afm .eot .zip .7z .gz .jar .pyc .pyo .pyd .whl .class .war .dll .obj .pch .pdb .ilk .suo'.split())
maxfilesize = 1024*1024

tostr = lambda b: b.decode('ascii','ignore')

search = ' '.join(argv[1:]).encode()
print('Text searching for "%s"...' % tostr(search))
i = 0
def walkdir(root):
	global i
	files = listdir(root)
	files = set(files) - excludedirs
	files = [f for f in files if splitext(f)[1] not in excludeexts]
	files = [pathjoin(root, f) for f in files]
	dirs,files = [f for f in files if isdir(f)],[f.replace('\\','/') for f in files if isfile(f)]
	for f in files:
		if stat(f).st_size > maxfilesize:
			continue
		try:
			if not i&0x3ff:
				print(f[:79].ljust(79),end='\r',file=stderr)
			i += 1
			with open(f, 'rb') as r:
				data = r.read()
				while True:
					index = data.index(search)
					found = ' '.join(tostr(data[index-10:index+len(search)+20]).split())
					print('%s: %s' % (f, found))
					data = data[index+1:]
		except:
			pass
	for d in dirs:
		walkdir(d)
walkdir('.')
print(end=' '*79+'\r',file=stderr)
