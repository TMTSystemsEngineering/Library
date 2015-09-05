#!/usr/bin/env python3

# external modules
import os
import sys
from datetime import datetime
import time

# my modules
import DCC
import config as cf
import tree

def traverse(s, tr, collkey, dirpath = './', indent = '', **kwargs):
    # traverse follows the collection structure on the DCC and replicates it on the local disk
    pflag = False
    savefiles = kwargs.get('SaveFiles', False)
    exclude = kwargs.get('Exclude', [])        
    maxfilesize = kwargs.get('MaxFileSize', sys.maxsize)
        
    branch = tr[collkey]
    collist = branch['collections']
    doclist = branch['documents']
    
#     collist = get_collections_in_collection(s, coll, Depth = '1', Print = pflag)
#     doclist = get_files_in_collection(s, coll, Depth = '1', Print = pflag)
    
    cinfo = DCC.getProps(s, collkey, InfoSet = 'Coll', Depth = '0', WriteProp = True)
#     cinfo = dcc_read_collection(s, coll, Depth = '0')
    print(indent,'Files in ', collkey, ': ', cinfo['title'])
    colname = cinfo['title']
    colname = colname.replace('/',' ')
    dirpath = dirpath + colname + '/' 
    if savefiles:
        try:
            os.stat(dirpath)
        except:
            os.mkdir(dirpath) 
    for doc in doclist:
        finfo = DCC.getProps(s, doc, InfoSet = 'DocBasic', WriteProp = True)
        print(indent + '\t',doc)
        print(indent + '\t\tTitle: ',finfo['title'])
        print(indent + '\t\tFileName: ',finfo['filename'],' [',finfo['date'],']' ,' [', finfo['size'],' bytes ]')
        filedirpath = dirpath + finfo.get('title').replace('/',' ') + '/'
        filename = finfo.get('filename')
        if savefiles:
            try:
                os.stat(filedirpath)
            except:
                os.mkdir(filedirpath)
        if not os.path.isfile(filedirpath+filename):
            print(indent + "\t\t\tFile doesn't exist")
            if savefiles:
                if finfo['size'] < maxfilesize:
                    print(indent + "\t\t\tGetting file")
                    DCC.get_file(s, doc, filedirpath, finfo['filename'])
                else:
                    print(indent + "\t\t\tFile size exceeds MaxFileSize of ", maxfilesize, "bytes")
            else:
                print(indent + "\t\t\tSaveFiles is False, so file will not be downloaded")


        elif (datetime.strptime(finfo['date'],'%a, %d %b %Y %H:%M:%S %Z') - datetime(1970,1,1)).total_seconds() > os.path.getctime(filedirpath+filename):
            print(indent + "\t\t\tFile exists, but is out of date:", time.ctime(os.path.getctime(filedirpath+filename)))
            if savefiles:
                if finfo['size'] < maxfilesize:
                    print(indent + "\t\t\tGetting updated file")
                    get_file(s, doc, filedirpath, finfo['filename'])
                else:
                    print(indent + "\t\t\tFile size exceeds MaxFileSize of ", maxfilesize, "bytes")
            else:
                print(indent + "\t\t\tSaveFiles is False, so file will not be downloaded")
        else:
            print(indent + "\t\t\tFile exists, created:", time.ctime(os.path.getctime(filedirpath+filename)))

    for c in collist:
        if (not c == collkey) and (not c in exclude):
            traverse(s, tr, c, dirpath, indent + '\t', **kwargs)

def create_DCC_mirror(s, dcc_handle, dirpath, **kwargs):
    tr = tree.get_tree(s,dcc_handle)
    tree.print_tree(tr)
    docList = tree.get_flat_tree(tr)
    traverse(s, tr, tr['root']['collections'][0], dirpath, **kwargs)
    
            
def testTraverse():        
    # Login to DCC
    s = DCC.login(cf.dcc_url + cf.dcc_login)

    coll = 'Collection-286'    
    create_DCC_mirror(s, coll, '/Users/sroberts/Box Sync/TMT DCC Files/Test/', SaveFiles = True, MaxFileSize = 2000000)
    
if __name__ == '__main__':
    print("Running module test code for",__file__)
    
    testTraverse()