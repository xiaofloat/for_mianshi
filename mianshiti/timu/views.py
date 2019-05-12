import json
import os
import uuid

import pythoncom
import win32com.client
import fitz
from django.http import HttpResponse
from django.shortcuts import render
import sys
sys.coinit_flags = 0

# Create your views here.

# 转换 Word文件档到pdf
from mianshiti.settings import BASE_DIR


def ConvertDocToPdf(src, dst):
    pythoncom.CoInitialize()
    if not os.path.exists(src):
        print(src + "不存在，无法继续！")
        return False
    os.system('taskkill /im wps.exe')
    # 如果文件存在就删除
    if os.path.exists(dst):
        os.remove(dst)
    o = win32com.client.Dispatch("Kwps.Application")
    o.Visible = False
    doc = o.Documents.Open(src)
    doc.ExportAsFixedFormat(dst, 17)
    o.Quit()
    if os.path.exists(dst):
        return True
    else:
        return False


# pdf文件转换成图片
def pdf_to_png(pdf_file_path):
    #  打开PDF文件，生成一个对象
    doc = fitz.open(pdf_file_path)
    img_path = os.path.splitext(pdf_file_path)[0]
    res_l = []
    for pg in range(doc.pageCount):
        page = doc[pg]
        rotate = int(0)
        # 每个尺寸的缩放系数为2，这将为我们生成分辨率提高四倍的图像。
        zoom_x = 2.0
        zoom_y = 2.0
        trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
        pm = page.getPixmap(matrix=trans, alpha=False)
        pm.writePNG(img_path + '%s.png' % pg)
        res_l.append('/static/' + (img_path + '%s.png' % pg).split(r'/')[-1])
    return res_l


def shangchuanzhanshi(request):
    file_obj = request.FILES.get('doc')
    file_name = file_obj.name
    img_l = []
    if file_obj:
        upload_file = "%s/%s" % ('./static', file_name)
        with open(upload_file, 'wb') as new_file:
            for chunk in file_obj.chunks():
                new_file.write(chunk)

        word_file_path = BASE_DIR + '/static/' + file_name
        pdf_file_path = os.path.splitext(word_file_path)[0] + '.pdf'
        # print(pdf_file_path)
        ConvertDocToPdf(word_file_path, pdf_file_path)
        img_l = pdf_to_png(pdf_file_path)
        # print(img_l)

    res_dict = {
        'code': 200,
        'img': img_l
    }
    res_s = json.dumps(res_dict)
    return HttpResponse(res_s)


# 旅行的题目- =！
def init_main(request):
    data = json.load(open(BASE_DIR + '/static/lvxing.json', 'r', encoding='utf-8'))
    res_s = json.dumps(data)
    return HttpResponse(res_s)

