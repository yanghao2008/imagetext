import os
import re
import sqlite3

def all_path(dirname):
    result = []
    for maindir, subdir, file_name_list in os.walk(dirname):
        for filename in file_name_list:
            apath = os.path.join(maindir, filename)
            result.append(apath)
    return result

def GetFileNameAndExt(filename):
     (filepath,tempfilename) = os.path.split(filename);
     (shotname,extension) = os.path.splitext(tempfilename);
     return filepath,shotname,extension

def GetFilenames(fileslist):
    filenames=[]
    for file in fileslist:
        fileinfo=GetFileNameAndExt(file)
        if fileinfo[2]=='.htm':
            filenames.append(fileinfo[1])
            #print(fileinfo[1])
    return filenames

#按照超星制定的页码标准排序
def Chaoxing_order(filenames):
    filenames_cov=[]
    filenames_bok=[]
    filenames_leg=[]
    filenames_fow=[]
    filenames_con=[]
    filenames_ins=[]
    filenames_att=[]
    filenames_bac=[]
    filenames_num=[]
    for fn in filenames:
        ifnum=re.findall(r'\d',fn[0:1])
        if len(ifnum):
            filenames_num.append(fn)
        else:
            if 'cov' in fn:
                filenames_cov.append(fn)
            if 'bok' in fn:
                filenames_bok.append(fn)
            if 'leg' in fn:
                filenames_leg.append(fn)
            if 'fow' in fn:
                filenames_fow.append(fn)
            if '!' in fn:
                filenames_con.append(fn)
            if 'ins' in fn:
                filenames_ins.append(fn)
            if 'att' in fn:
                filenames_att.append(fn)
            if 'bac' in fn:
                filenames_bac.append(fn)
    return filenames_cov+filenames_bok+filenames_leg+filenames_fow+filenames_con+filenames_num+filenames_ins+filenames_att+filenames_bac

def pageLessThreeNum(filename):
    for i in range(1,3,1):
        if filename[0:1]=='0':
            filename=filename[1:]
        else:
            return filename
    return filename

def pageName(filename):
    ifilenameum=re.findall(r'\d',filename[0:1])
    if len(ifilenameum):
        for i in range(1,6,1):
            if filename[0:1]=='0':
                filename=filename[1:]
            else:
                return '第'+filename+'页'
    else:
        if 'cov' in filename:
            return '封面第'+pageLessThreeNum(filename[3:])+'页'
        if 'bok' in filename:
            return '书名第'+pageLessThreeNum(filename[3:])+'页'
        if 'leg' in filename:
            return '版权第'+pageLessThreeNum(filename[3:])+'页'
        if 'fow' in filename:
            return '前言第'+pageLessThreeNum(filename[3:])+'页'
        if '!' in filename:
            return '目录第'+pageLessThreeNum(filename[3:])+'页'
        if 'ins' in filename:
            return '索引第'+pageLessThreeNum(filename[3:])+'页'
        if 'att' in filename:
            return '附录第'+pageLessThreeNum(filename[3:])+'页'
        if 'bac' in filename:
            return '封底第'+pageLessThreeNum(filename[3:])+'页'
    return '第'+filename+'页'

def pageNumber(filename):
    ifilenameum=re.findall(r'\d',filename[0:1])
    if len(ifilenameum):
        for i in range(1,6,1):
            if filename[0:1]=='0':
                filename=filename[1:]
            else:
                return filename
    return filename
            

def removeBom(file):
    '''移除UTF-8文件的BOM字节'''
    BOM = b'\xef\xbb\xbf'
    existBom = lambda s: True if s == BOM else False
 
    f = open(file, 'rb')
    if existBom(f.read(3)):
        fbody = f.read()
        # f.close()
        with open(file, 'wb') as f:
            f.write(fbody)

def readBkmk(bkmkfile):
    h1=''
    h2=''
    h3=''
    mulu=[]
    with open(bkmkfile,'r',encoding='utf-16') as fr:
        lines=fr.readlines()
        for line in lines:
            tabnum=line.count('\t')
            if tabnum==1:
                h1=line.strip().split('\t')[0]
                m=[]
                m.append(line.replace(',','，').strip().split('\t')[1])
                m.append(h1)
                mulu.append(m)
            if tabnum==2:
                h2=line.strip().split('\t')[0]
                m=[]
                m.append(line.replace(',','，').strip().split('\t')[1])
                m.append(h1+','+h2)
                mulu.append(m)
            if tabnum==3:
                h3=line.strip().split('\t')[0]
                m=[]
                m.append(line.replace(',','，').strip().split('\t')[1])
                m.append(h1+','+h2+','+h3)
                mulu.append(m)
    previous=1
    pre=''
    content={}
    for ml in mulu:
        current=int(ml[0])
        if current > 0:
            content[str(current)]=ml[1]
            if current > previous:
                for i in range(previous+1,current):
                    content[str(i)]=pre
            previous=current
            pre=ml[1]
    return(content)

global idkey
# 起始ID号，需要修改
idkey =336

def createDB(filepath,bookid):
    fileslist=Chaoxing_order(GetFilenames(all_path(filepath)))
    rows = []
    formertext=''
    if os.path.exists(filepath+'FreePic2Pdf_bkmk.txt'):
        bookmark=readBkmk(filepath+'FreePic2Pdf_bkmk.txt')
    for ls in fileslist:
        removeBom(filepath+ls+'.htm')
        with open(filepath+ls+'.htm','r',encoding = 'UTF-8') as fo:
            print(filepath+ls+'.htm')
            row=[]
            global idkey
            row.append(idkey)
            idkey=idkey+1
            row.append(bookid)
            print(pageNumber(ls))
            #处理书签页
            if os.path.exists(filepath+'FreePic2Pdf_bkmk.txt'):
                if pageNumber(ls) in bookmark.keys():
                    row.append(bookmark[pageNumber(ls)])
                else:
                    row.append('')
            else:
                row.append('')
            row.append(filepath.replace('/','\\').replace('Z:/VMwareShare_py/演示/','Z:\\VMwareShare_py\\')+ls+'.png')
            row.append(filepath.replace('/','\\').replace('Z:/VMwareShare_py/演示/','Z:\\VMwareShare_py\\')+ls+'.htm')
            text=fo.read()
            text=re.sub('<.+?>','',text)
            text=text.replace('\n','')
            row.append(formertext+text)
            if len(text) > 30:
                formertext=text[-30:]
            else:
                formertext=text
            row.append(pageName(ls))
            rows.append(row)
        fo.close()
    connection.executemany('INSERT INTO books_booksimagetext VALUES (?,?,?,?,?,?,?)', rows)


connection = sqlite3.connect('Z:/VMwareShare_py/test_books.db')
#connection.execute('CREATE TABLE books_booksimagetext (id int primarykey, book_id text, chapter text, image text,txt text, text text, page text)')

createDB('Z:/VMwareShare_py/演示/黄明信著《吐番佛教》中国藏学出版社_2010.01_P240_png/','b0002')
#

connection.commit()
connection.close()
