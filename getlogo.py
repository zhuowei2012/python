#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import requests
import re
from bs4 import BeautifulSoup
import codecs
import csv
import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)


####比如爬取中间失败了，下一次启动的时候，跳过前面已经完成的，所以这里设计了一个开始序号
BEGIN_DOWNLOAD_INDEX = 14584
COMPLETE_DOWNLOAD_SUM = 0

DOWNLOAD_DIRECTORY_ROOT = "d:\\logo\\"
URL_ROOT = "https://pinpai.smzdm.com"
DEFAULT_BEGIN = "/diannaoshuma/"

EXPORT_EXCEL_NAME = "export.csv"

BRAND_GROUP1 = u"品牌分类"
BRAND_GROUP2 = u"品牌区域"

ALL_BRAND_INFO = []
TITLE = ['商标大类','商标类型','商标名称','关注度','商标区域','发源国家','创立时间','创始人中文名','创始人英文名','所属公司','总部地址',
         '主品牌','品牌口号','常用名','图片地址','是否下载成功','商标描述']
class BrandTypes:
    link = ""
    b_name = ""
    b_count = 0

class BrandInfo:
    #大类
    BrandBigGroup = ""
    #商标名称
    BrandName = ""
    #商标类型
    BrandType = ""
    #商标区域
    BrandArea = "未知"
    #商标发源国家
    SourceCountry = "未知"
    #创立时间
    CreateTime = "未知"
    #创始人中文名
    Founder_ch = "未知"
    #创始人英文名
    Founder_en = "未知"
    #所属公司
    Company = "未知"
    #总部地址
    HQAddress = "未知"
    #主品牌
    MainBrand = "未知"
    #品牌口号
    Kouhao = "未知"
    #常用名
    OtherName = "未知"
    # 商标描述
    BrandDesc = "未知"
    # 关注度
    FocusCount = 0
    #商标图片地址
    Logo_URL = "无图"
    #下载图片是否成功
    IsGetPic = "否"

    def __init__(self, group, brandname,brandtype,area="未知", focus=0, logoURL="无图", brandDesc="未知"):
        self.BrandBigGroup = group
        self.BrandName = brandname
        self.BrandType = brandtype
        self.BrandArea = area
        self.FocusCount = focus
        self.Logo_URL = logoURL
        self.BrandDesc = brandDesc

    def toDict(self):
        return [self.BrandBigGroup, self.BrandType, self.BrandName, str(self.FocusCount), self.BrandArea ,self.SourceCountry,
                self.CreateTime, self.Founder_ch, self.Founder_en,self.Company, self.HQAddress,self.MainBrand,self.Kouhao,
                self.OtherName,self.Logo_URL,self.IsGetPic, self.BrandDesc]

    def __str__(self):
        return self.BrandBigGroup + "&&" + self.BrandType + "&&" \
               + self.BrandName + "&&" + str(self.FocusCount) + "&&" + self.BrandArea + "&&" + \
               self.SourceCountry + "&&" + self.CreateTime + "&&" + \
               self.Founder_ch + "&&" + self.Founder_en + "&&" + self.Company + "&&" + self.HQAddress + "&&" + \
               self.MainBrand + "&&" + self.Kouhao + "&&" + self.OtherName + "&&" + self.Logo_URL + "&&" + self.IsGetPic + \
               "&&" + self.BrandDesc

    __repr__ = __str__

    #def __str1__(self):
    #    return "+++++++++++" + self.BrandBigGroup.encode("utf-8") + "," + self.BrandType.encode("utf-8") + "," \
    #           + self.BrandName.encode("utf-8") + "," + str(self.FocusCount) + ","+ self.BrandArea.encode("utf-8") + ","+ \
    #           self.SourceCountry.encode("utf-8") + ","+ self.CreateTime + ","+ \
    #           self.Founder_ch.encode("utf-8") + ","+ self.Founder_en + ","+ self.Company.encode("utf-8") + ","+ self.HQAddress.encode("utf-8") + ","+ \
    #           self.MainBrand.encode("utf-8") + ","+ self.Kouhao.encode("utf-8") + "," + self.OtherName.encode("utf-8") + ","+ self.Logo_URL.encode("utf-8") + ","+ self.BrandDesc.encode("utf-8")



def RequestHttp(url,headers):
    nRetry = 0
    while 1:
        try:
            result = requests.get(url, headers=headers)
            return result
        except:
            if nRetry > 5:
                break
        nRetry += 1




def getAllBrands(str1, list):
    for brand in str1:
        brand_a = brand.find('a')
        if brand_a < 0:
            continue
        brand_tags = brand.find_all('a')
        if brand_tags < 0:
            continue

        for brand_href in brand_tags:
            a = BrandTypes()
            brand_name = brand_href.get_text().strip()
            d = brand_name.find(u'（')
            a.b_name = brand_name[:d].strip()
            #if a.b_name == u"电脑数码" or a.b_name == u"个护化妆" or a.b_name == u"家用电器" or a.b_name == u"运动户外"\
            #        or a.b_name == u"服饰鞋包"or a.b_name == u"母婴用品"or a.b_name == u"日用百货"or a.b_name == u"办公设备":
            #    continue
            a.link = brand_href.get('href')
            brand_count = brand_href.find('span').get_text()
            a.b_count = int(re.sub("[^0-9]", "", brand_count))
            list.append(a)

def ExportToFile(brand):
    log_dir = DOWNLOAD_DIRECTORY_ROOT + "/" + EXPORT_EXCEL_NAME
    bFirst = False
    if not os.path.exists(log_dir):
        bFirst = True
    with open(log_dir, "a") as ff:
        ff.write(codecs.BOM_UTF8)
        spamwriter = csv.writer(ff, dialect='excel',lineterminator='\n')
        spamwriter.writerow(TITLE) if bFirst else None
        #for brand in BrandInfos:
        print(brand)
        spamwriter.writerow(brand.toDict())
            #ff.write(str(brand).encode("utf-8") + "\r\n")

def CreateDirectory(directory):
    folder = os.path.exists(directory)
    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(directory)  # makedirs 创建文件时如果路径不存在会创建这个路径

def dealBrandGushi(brand_name, values, brandInfo):
    value = values.contents[-1].strip().replace("\n","")
    print(brand_name + ":" + value)
    if brand_name == u'发源国家':
        brandInfo.SourceCountry = value
    elif brand_name == u'创立时间':
        brandInfo.CreateTime = value
    elif brand_name == u'创始人中文名':
        brandInfo.Founder_ch = value
    elif brand_name == u'创始人英文名':
        brandInfo.Founder_en = value
    elif brand_name == u'所属公司':
        brandInfo.Company = value
    elif brand_name == u'总部地点':
        brandInfo.HQAddress = value

    elif brand_name == u'主品牌':
        brandInfo.MainBrand = value
    elif brand_name == u'品牌口号':
        brandInfo.Kouhao = value
    elif brand_name == u'常用名':
        brandInfo.OtherName = value

def getBrandInfo(brandlist, brandType, downloadDir):
    global COMPLETE_DOWNLOAD_SUM
    #遍历所有的
    for brand in brandlist:
        _current_brand_dir = downloadDir + "/" + brand.b_name+"_" + str(brand.b_count)
        CreateDirectory(_current_brand_dir)
        #print(brand.b_name + "," + brand.link + "," + str(brand.b_count))
        _total_count = brand.b_count
        _page_count = int(_total_count/100) + 1
        for _page in range(1,_page_count+1):
            if _page == 1:
                _brand_url = URL_ROOT + brand.link
            else:
                _brand_url = URL_ROOT + brand.link + "/p" + str(_page) + "/"

            r_current = RequestHttp(_brand_url, headers=headers)
            soup_currnt = BeautifulSoup(r_current.text, "html.parser")  # 解析text中的HTML

            dls = soup_currnt.find_all('ul', class_='brands clearfix')

            #处理每个logo
            for tag in dls[0].contents:
                #try:
                link_tag = tag.find('a')
                if link_tag < 0:
                    continue

                #logo的介绍页面地址、图片地址、logo名称
                link_url = link_tag.get('href')
                pic_url =  link_tag.find('img').get('src')
                #过滤掉这类无图片的
                if pic_url == "/resources/img/brand_default.jpg":
                    pic_url = ""
                else:
                    pic_url = "https:" + pic_url
                tag_name = link_tag.find('div', class_='brands-name').get_text()
                tag_name = tag_name.replace("/", "_")

                #print(link_url)
                #print(pic_url)
                #print(tag_name)

                #创建当前logo的路径
                brand_image_path = _current_brand_dir + "/" + tag_name + "." + pic_url.split('.')[-1]
                print(brand_image_path)

                #跳过已经下载成功的这部分
                if COMPLETE_DOWNLOAD_SUM < BEGIN_DOWNLOAD_INDEX or os.path.exists(brand_image_path):
                    COMPLETE_DOWNLOAD_SUM += 1
                    print(brandType + "|" + tag_name + "|已下载过了，跳过！！")
                    continue


                brand_link = URL_ROOT + link_url
                r_current_brand = RequestHttp(brand_link, headers=headers)
                soup_currnt = BeautifulSoup(r_current_brand.text, "html.parser")  # 解析text中的HTML

                #热度数据
                dls_brand = soup_currnt.find('span', class_='pp-follow-people').get_text()
                dls_brand = int(re.sub("[^0-9]", "", dls_brand))
                print(dls_brand)

                #品牌描述
                dls_brand_desc = soup_currnt.find('div',class_='pp-content-text').contents[0].strip()
                print(dls_brand_desc)

                oneBrand = BrandInfo(brandType, tag_name, brand.b_name, focus=dls_brand, logoURL=pic_url, brandDesc=dls_brand_desc)

                # 下载图片
                if pic_url:
                    try:
                        pic = RequestHttp(pic_url, headers=headers)
                        with open(brand_image_path, 'wb') as f:
                            f.write(pic.content)
                            oneBrand.IsGetPic = "是"
                            print("文件下载成功..." + brandType + "|" + tag_name + "|" + pic_url)
                    except:
                        print("文件下载失败！" + brandType + "|" + tag_name + "|" + pic_url)

                brand_gushi = brand_link + "/gushi/"
                r_current_gushi = RequestHttp(brand_gushi, headers=headers)
                soup_gushi = BeautifulSoup(r_current_gushi.text, "html.parser")  # 解析text中的HTML

                dls_gushi = soup_gushi.find_all('div', class_='item-group')
                for gushi in dls_gushi:
                    gushi_temp = gushi.find_all('div')
                    for temp in gushi_temp:
                        _desc = temp.find('span').get_text()
                        dealBrandGushi(_desc, temp, oneBrand)

                dls_gushi2 = soup_gushi.find_all('div', class_='item-group-simple')
                for gushi in dls_gushi2:
                    _desc = gushi.find('span').get_text()
                    dealBrandGushi(_desc, gushi, oneBrand)

                ALL_BRAND_INFO.append(oneBrand)
                COMPLETE_DOWNLOAD_SUM = COMPLETE_DOWNLOAD_SUM + 1
                ExportToFile(oneBrand)
                print(brandType + "|" + tag_name + ",采集成功！！")
                #break
                #except:
                #    print("有失败!!!!")

        #break



base_url = URL_ROOT + DEFAULT_BEGIN
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3018.3 Safari/537.36'}
r = RequestHttp(base_url,headers = headers)

soup = BeautifulSoup(r.text,"html.parser")#解析text中的HTML
#<a href="/jiayongdianqi/" >家用电器&nbsp;<span>（2534）</span>

brand_class = soup.find_all('div', class_='brand-classify')



brand_type1 = brand_class[0].contents
brand_list1 = []
getAllBrands(brand_type1, brand_list1)
download1 = DOWNLOAD_DIRECTORY_ROOT + BRAND_GROUP1
getBrandInfo(brand_list1, BRAND_GROUP1, download1)

#brand_type2 = brand_class[1].contents
#brand_list2 = []
#getAllBrands(brand_type2, brand_list2)
#download2 = DOWNLOAD_DIRECTORY_ROOT + BRAND_GROUP2
#getBrandInfo(brand_list2, BRAND_GROUP2, download2)

#ExportToFile(ALL_BRAND_INFO)

#得到总
#sum_count_str = soup.find_all('h2', class_='brand-type-title')
#sum_count = (sum_count_str[0].find('span').get_text())
#sum_count = int(re.sub("[^0-9]", "", sum_count))
#print(sum_count)
#for tag in sum_count_str:
#   # print tag
#    m_name = tag.find('span', class_='title').get_text()
#    m_rating_score = float(tag.find('span',class_='rating_num').get_text())
#    m_people = tag.find('div',class_="star")
#    m_span = m_people.findAll('span')
#    m_peoplecount = m_span[3].contents[0]
#    m_url=tag.find('a').get('href')
#    print( m_name+"        "  +  str(m_rating_score)   + "           " + m_peoplecount + "    " + m_url )

#dls = soup.find_all('ul', class_='brands clearfix')
#for tag in dls[0].contents:
#    link_tag = tag.find('a')
#    if link_tag < 0:
#        continue
#    link_url = link_tag.get('href')
#    pic_url = link_tag.find('img').get('src')
#    tag_name = link_tag.find('div', class_ = 'brands-name').get_text()
#    print(link_url)
#    print(pic_url)
#    print(tag_name)
#marks = soup.find_all('span',class_='rating_nums')


pat1 = '\d{4}\-\d{2}\-\d{2}'
pat2 = '[\/0-9a-z\.]{41}'
imglist1 = re.compile(pat1).findall(r.text)
imglist2 = re.compile(pat2).findall(r.text)
for i,j in zip(imglist1,imglist2):
    thisimgurl = 'https://files.vivo.com.cn/activity/attachments/geniesse/' + i + j
    # print(thisimgurl)
    root = "D://picss//"
    path = root + thisimgurl.split('/')[-1]
    try:
        if not os.path.exists(root):
            os.mkdir(root)
        if not os.path.exists(path):
            pic = requests.get(thisimgurl,headers = headers)
            with open(path,'wb') as f:
                f.write(pic.content)
                print("文件保存成功...")
        else:
            print("文件已存在...")
    except:
        print("爬取失败！")
