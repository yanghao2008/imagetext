from django.shortcuts import render
from books import models  # 导入models文件
from django.contrib.auth.decorators import login_required,permission_required 
from mybooks import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import re
import os
from PIL import Image
import re
import base64
from io import BytesIO

def highlight(matched):
    value = matched.group('value')
    return '<strong style="background:red">'+value+'</strong>'

def abstract(text):
    front=text.partition('<strong style="background:red">')
    rear=front[2].rpartition('</strong>')
    return front[0][-50:]+'<strong style="background:red">'+rear[0]+'</strong>'+rear[2][:50]

def getleginfo(BKname,page):
    return '<font color="purple">'+BKname.author+'：'+'《'+BKname.bookname+'》，'+BKname.pubaddress+'：'+BKname.publisher+'，'+BKname.year+'年，'+page+'</font>'

def search(request):
   if request.method == 'POST':
        query_str = request.POST.get('query_str').strip()
        query_str=re.sub(' +', ' ', query_str)
        bookname = request.POST.get('bookname')
        if query_str != '':
            if ' ' in query_str:
                queryregex = query_str.replace(' ', '.*')
                imagetext = models.BooksImageText.objects.filter(text__regex=queryregex, book_id__bookname__contains=bookname).order_by('id')
            else:
                imagetext = models.BooksImageText.objects.filter(text__regex=query_str, book_id__bookname__contains=bookname).order_by('id')
#分页
            paginator = Paginator(imagetext, 20) # 每页条数
            page = request.POST.get('page')
            try:
                pagesImagetext = paginator.page(page) 
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                pagesImagetext = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                pagesImagetext = paginator.page(paginator.num_pages)
#高亮、取摘要
            if ' ' in query_str:
                for it in pagesImagetext:
                    sub_query_strs=query_str.split(' ')
                    for sqs in sub_query_strs:
                        it.text=re.sub('(?P<value>'+sqs+')', highlight, it.text)
                    BKname=models.Info.objects.get(book_id=it.book_id)
                    copyright=getleginfo(BKname,it.page)
                    it.text=abstract(it.text)+'<br>'+copyright
            else:
                for it in pagesImagetext:
                    BKname=models.Info.objects.get(book_id=it.book_id)
                    copyright=getleginfo(BKname,it.page)
                    it.text=abstract(re.sub('(?P<value>'+query_str+')', highlight, it.text))+'<br>'+copyright

            return render(request, 'index.html', {'returninfo':'共在'+str(len(imagetext))+'个页面上找到检索信息。','imagetext': pagesImagetext,'query_str': query_str,'bookname': bookname})
        else:
            return render(request, 'index.html')
   else:
        return render(request, 'index.html')

def view(request):
    if request.method == 'POST':
        key_Id = request.POST.get('key_Id')
        imagetext = models.BooksImageText.objects.get(id=key_Id)
        with open(imagetext.txt,'r',encoding='UTF-8') as txtfile:
            textcontent=txtfile.read()
        img = Image.open(imagetext.image)
        output_buffer = BytesIO() 
        img.save(output_buffer, format='png') 
        byte_data = output_buffer.getvalue() 
        base64_data = base64.b64encode(byte_data)
        BKname=models.Info.objects.get(book_id=imagetext.book_id)
        copyright=getleginfo(BKname,imagetext.page)
    return render(request, 'books_view.html', {'copyright':copyright,'base64_data':str(base64_data,'utf-8'),'imagetext': imagetext,'textcontent':textcontent,'before':int(key_Id)-1,'next':int(key_Id)+1})

