#!/usr/bin/env python3

from os import listdir,stat
from os.path import join as pathjoin,isfile,isdir,splitext
from sys import argv,stderr

excludedirs = set('.git .svn __pycache__'.split())
excludeexts = set('.exe .bin .png .jpg .gif .tga .ppm .ico .icns .psd .wav .mp3 .ttf .afm .eot .zip .7z .gz .jar .pyc .pyo .pyd .whl .class .war .dll .obj .pch .pdb .ilk .suo'.split())
maxfilesize = 1024*1024

case_insensitive,argv = '--case-insensitive' in argv, [a for a in argv if a!='--case-insensitive']

tosearch = (lambda a: a.lower()) if case_insensitive else (lambda a: a.encode())
todata = (lambda a: a.decode('utf8').lower()) if case_insensitive else (lambda a: a)
toprint = (lambda a: a) if case_insensitive else (lambda a: a.decode('utf8','ignore'))
bin2string = lambda b: b.__str__()[2:-1]

search = tosearch(' '.join(argv[1:]))
print('Text searching for "%a"...' % toprint(search))
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
			if not i&0x7f:
				print(f[:79].ljust(79),end='\r',file=stderr)
			i += 1
			with open(f, 'rb') as r:
				data = r.read()
				try:
					data = todata(data)
				except UnicodeDecodeError:
					# Fast conversion of binary or non-utf8 file.
					data = bin2string(data)
				while True:
					index = data.index(search)
					found = ' '.join(toprint(data[index-10:index+len(search)+20]).split())
					print('%s: %s' % (f, found))
					data = data[index+1:]
		except Exception as e:
			pass
	for d in dirs:
		walkdir(d)
walkdir('.')
print(end=' '*79+'\r',file=stderr)
