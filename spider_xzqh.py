import requests
from lxml import etree
import time

# 爬取的uri
url1 = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2019/'

# 模拟请求头
headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
        'Cookie': 'AD_RS_COOKIE=20080919; wzws_cid=fafdc6741ab8efcd5795778727299fbb6da385e91171cd22afd180dedd39bf0c93b239a7e8628295bc1a364a42f742008b5bcbb37f9a0909290688d49a5fc83e453ae04b9aed325f0db387e2914b580f',
}


def getjwh(url):
    """居委会级别的数据爬取"""
    """@url 街道镇级别的url"""

    # 如果爬取url失败将重试
    bl = True
    while bl:
        try:
            r = requests.get(url.strip(), headers=headers)
            if r.status_code == 200:
                bl = False
            else:
                # 爬取失败暂停10秒后继续爬取
                time.sleep(10)
                bl = True

            r.raise_for_status()
        except:
            # 爬取失败暂停10秒后继续爬取
            time.sleep(10)
            bl = True

    # 网页的字符编码改为GBK由于测试utf8编码有问题
    r.encoding = 'GBK'

    # 使用xpath提取html中的数据
    html = etree.HTML(r.text)

    # 获取居委会列表
    shis = html.xpath('//tr[@class="villagetr"]')
    data = []

    for s in shis:
        try:
            # 获取居委会的行政区划编号
            id = s.xpath('./td[1]/text()')

            # 获取居委会的行政区划名
            name = s.xpath('./td[3]/text()')
            data.append([name[0], id[0]])
        except:
            continue
    return data



def getinfo(url, classdtr):
    """获取市，区/县，街道/镇级别的数据"""
    """@url 为省级的url地址"""
    """@classdtr 为市，区/县，街道/镇 级别的html标签class属性"""

    # 如果爬取url失败将重试
    bl = True
    while bl:
        try:
            r = requests.get(url.strip(), headers=headers)
            if r.status_code == 200:
                print(url, r.status_code)
                bl = False
            else:
                time.sleep(10)
                bl = True
            r.raise_for_status()
        except:
            print(url, type(r.status_code), r.status_code)
            time.sleep(10)
            bl = True

    print(url, r.status_code)
    r.encoding = 'GBK'
    html = etree.HTML(r.text)
    data = []
    shis = html.xpath('//tr[@class="%s"]' % classdtr)
    for s in shis:
        try:
            name = s.xpath('./td[2]/a/text()')
            href = s.xpath('./td[2]/a/@href')
            if len(name) > 0 and len(href) > 0:
                data.append([name[0].strip(), '/'.join(url.split('/')[:-1]) +'/'+ href[0]])
        except:
            continue
    return data




def getshengs():
    """获取全部省信息"""

    bl = True
    while bl:
        try:
            r = requests.get(url1, headers=headers)
            if r.status_code == 200:
                bl = False
            else:
                time.sleep(10)
                bl = True
            r.raise_for_status()
        except:
            time.sleep(10)
            bl = True
    r.encoding = 'GBK'
    # print(r.text)
    html = etree.HTML(r.text)
    rows = html.xpath('//tr[@class="provincetr"]')
    for row in rows:
        for td in row.xpath('./td'):
            href = td.xpath('./a/@href')
            text = td.xpath('./a/text()')
            if len(href) > 0 and len(text) > 0:
                with open('xz3/sheng.txt', 'a', encoding='utf-8') as f:
                    f.write("%s\t%s\n" % (text[0].strip(), (url1 + href[0]).strip()))



if __name__ == "__main__":
    # 获取全部省市
    getshengs()

    # 通过省数据内的URL爬取市级数据
    for s in open('xz3/sheng.txt', encoding='utf-8'):
        sline = s.split('\t')
        print(sline[0], sline[1])
        shis = getinfo(sline[1], 'citytr')
        for shi in shis:
            print(sline[0], shi[0])
            with open('xz3/shi.txt', 'a', encoding='utf-8') as f:
                f.write("%s\t%s\t%s\n" % (sline[0], shi[0], shi[1]))

    # 通过市级数据内的URL爬取区级数据
    for s in open('xz3/shi.txt', encoding='utf-8'):
        sline = s.split('\t')
        print(sline)
        qus = getinfo(sline[2], 'countytr')
        if len(qus) < 1:
            with open('xz3/qu.txt', 'a', encoding='utf-8') as f:
                f.write("%s\t%s\t%s\t%s\n" % (sline[0], sline[1], sline[1], sline[2]))

        for qu in qus:
            with open('xz3/qu.txt', 'a', encoding='utf-8') as f:
                f.write("%s\t%s\t%s\t%s\n" % (sline[0], sline[1], qu[0], qu[1]))

    # 通过区级数据内的URL爬取街道/镇级数据
    for s in open('xz3/qu.txt', encoding='utf-8'):
        sline = s.split('\t')
        print(sline)
        if len(sline) == 1 and sline[0] == '\n':
            continue
        zhens = getinfo(sline[3], 'towntr')
        for zhen in zhens:
            with open('xz3/zhen.txt', 'a', encoding='utf-8') as f:
                f.write("%s\t%s\t%s\t%s\t%s\n" % (sline[0], sline[1], sline[2], zhen[0], zhen[1]))

    # 通过街道/镇级数据内的URL爬取居委会数据
    for s in open('xz3/zhen.txt', encoding='utf-8'):
        sline = s.split('\t')
        print(sline)
        if len(sline) == 1 and sline[0] == '\n':
            continue
        jwhs = getjwh(sline[4])
        print(jwhs)
        for j in jwhs:
            with open('xz3/data.txt', 'a', encoding='utf-8') as f:
                f.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (sline[0], sline[1], sline[2], sline[3], j[0], j[1]))

