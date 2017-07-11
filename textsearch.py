#!/usr/bin/env python3

from __future__ import print_function
import multiprocessing as mp
import os
from os.path import join as pathjoin
from sys import argv,stderr,exit


excludedirs = set('.git .svn __pycache__'.split())
excludeexts = set('exe bin png jpg gif tga ppm ico icns psd wav mp3 ttf afm eot zip 7z gz jar pyc pyo pyd whl class war dll obj pch pdb ilk suo'.split())
maxfilesize = 1024*1024

case_insensitive = '--case-insensitive' in argv or '-i' in argv
progress = '--progress' in argv or '-p' in argv
argv = [a for a in argv if a not in {'--case-insensitive','-i','--progress','-p'}]

toprint = (lambda a: a) if case_insensitive else (lambda a: a.decode('utf8','ignore'))
bin2string = lambda b: b.__str__()[2:-1].lower()

search = ' '.join(argv[1:])
if not search:
    exit(1)
search = search.lower() if case_insensitive else search.encode()


def search_thread_entry(workq,):
    while True:
        f,size = workq.get()
        if size <= 0:
            break
        if progress:
            print(f, end='                            \r', file=stderr)
        try:
            fd = os.open(f, os.O_BINARY|os.O_RDONLY)
        except:
            continue
        data = os.read(fd, size)
        os.close(fd)
        if case_insensitive:
            try:
                data = data.decode('utf8').lower()
            except UnicodeDecodeError:
                # Fast conversion of binary or non-utf8 file.
                data = bin2string(data)
        index = data.find(search, 0)
        while index >= 0:
            found = toprint(data[index-10:index+len(search)+20]).replace('\n', ' ').replace('\r', ' ')
            print('%s: %s' % (f, found))
            index = data.find(search, index+len(search))


def walkdir(workq, root):
    try:
        files = os.scandir(root)
    except:
        return 0
    files = [(f,f.is_dir()) for f in files]
    dirs,files = [f.name for f,isdir in files if isdir],[(f.path,f.stat().st_size) for f,isdir in files if not isdir]
    dirs = set(dirs) - excludedirs
    dirs = [pathjoin(root, d).replace('\\','/') for d in dirs]
    files = [(f.replace('\\','/'),size) for f,size in files if size and size < maxfilesize and f.rpartition('.')[2] not in excludeexts]
    filecnt = len([workq.put((f,size)) for f,size in files])
    for d in dirs:
        filecnt += walkdir(workq, d)
    return filecnt


def run():
    workq = mp.Queue()
    search_procs = [mp.Process(target=search_thread_entry, args=(workq,)) for _ in range(3)]
    [p.start() for p in search_procs]

    filecnt = walkdir(workq, '.')
    [workq.put(('*',-1)) for _ in search_procs]
    [p.join() for p in search_procs]
    if progress:
        print(' '*79, end='\r', file=stderr)
    print('Searched %i files.' % filecnt, file=stderr)


if __name__ == '__main__':
    mp.freeze_support()
    run()
