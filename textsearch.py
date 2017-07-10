#!/usr/bin/env python3

import multiprocessing as mp
import os
from os.path import join as pathjoin
from sys import argv,stderr


excludedirs = set('.git .svn __pycache__'.split())
excludeexts = set('exe bin png jpg gif tga ppm ico icns psd wav mp3 ttf afm eot zip 7z gz jar pyc pyo pyd whl class war dll obj pch pdb ilk suo'.split())
maxfilesize = 1024*1024

case_insensitive = '--case-insensitive' in argv or '-i' in argv
argv = [a for a in argv if a not in ('--case-insensitive','-i')]

tosearch = (lambda a: a.lower()) if case_insensitive else (lambda a: a.encode())
todata = (lambda a: a.decode('utf8').lower()) if case_insensitive else (lambda a: a)
toprint = (lambda a: a) if case_insensitive else (lambda a: a.decode('utf8','ignore'))
bin2string = lambda b: b.__str__()[2:-1].lower()

search = tosearch(' '.join(argv[1:]))
if not search:
    os._exit(1)


def search_thread_entry(workq, resq):
    while True:
        f,size = workq.get()
        if f == '*':
            break
        fd = os.open(f, os.O_BINARY|os.O_RDONLY)
        if fd:
            data = os.read(fd, size)
            os.close(fd)
            try:
                data = todata(data)
            except UnicodeDecodeError:
                # Fast conversion of binary or non-utf8 file.
                data = bin2string(data)
            index = data.find(search, 0)
            while index >= 0:
                found = ' '.join(toprint(data[index-10:index+len(search)+20]).split())
                resq.put('%s: %s' % (f, found))
                index = data.find(search, index+len(search))


def print_thread_entry(resq):
    while True:
        r = resq.get()
        print(r)


def walkdir(root):
    global filecnt
    files = os.scandir(root)
    files = [(f,f.is_dir()) for f in files]
    dirs,files = [f.name for f,isdir in files if isdir],[(f.path,f.stat().st_size) for f,isdir in files if not isdir]
    dirs = set(dirs) - excludedirs
    dirs = [pathjoin(root, d).replace('\\','/') for d in dirs]
    files = [(f.replace('\\','/'),size) for f,size in files if f.rpartition('.')[2] not in excludeexts]
    for f,size in files:
        if size > maxfilesize:
            continue
        filecnt += 1
        workq.put((f,size))
    for d in dirs:
        walkdir(d)


if __name__ == '__main__':
    mp.freeze_support()
    filecnt = 0
    workq = mp.Queue()
    resq = mp.Queue()
    search_procs = [mp.Process(target=search_thread_entry, args=(workq,resq)) for _ in range(3)]
    print_proc = mp.Process(target=print_thread_entry, args=(resq,))
    [p.start() for p in search_procs+[print_proc]]

    walkdir('.')
    [workq.put(('*',-1)) for _ in search_procs]
    [p.join() for p in search_procs]
    print('Searched %i files.' % filecnt, file=stderr)
    os._exit(0)
