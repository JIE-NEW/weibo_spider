#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import re
import random
import requests
import sys
import traceback
import shutil
import pickle
from datetime import datetime
from datetime import timedelta
from lxml import etree
from time import sleep
from fake_useragent import UserAgent

ua = UserAgent()

reload(sys)
sys.setdefaultencoding('utf-8')


class Weibo:
    ua = UserAgent()
    my_headers = {"User-Agent": str(ua.random), "Accept-Encoding": "gzip, deflate, br", "Connection": "close"}

    # Weibo类初始化
    def __init__(self, user_id, filter=0):
        self.user_id = user_id  # 用户id，即需要我们输入的数字，如昵称为“Dear-迪丽热巴”的id为1669879400
        self.filter = filter  # 取值范围为0、1，程序默认值为0，代表要爬取用户的全部微博，1代表只爬取用户的原创微博
        self.username = ''  # 用户名，如“Dear-迪丽热巴”
        self.weibo_num = 0  # 用户全部微博数
        self.weibo_num2 = 0  # 爬取到的微博数
        self.following = 0  # 用户关注数
        self.followers = 0  # 用户粉丝数
        self.weibo_content = []  # 微博内容
        self.weibo_place = []  # 微博位置
        self.publish_time = []  # 微博发布时间
        self.up_num = []  # 微博对应的点赞数
        self.retweet_num = []  # 微博对应的转发数
        self.comment_num = []  # 微博对应的评论数
        self.publish_tool = []  # 微博发布工具
        self.move_flag = 1  # 当前用户爬取结束后是否移走

    '''# IP代理地址获取
    def get_random_ip(self):
        proxy_ip = random.choice(ip_list)
        proxies = {'http': proxy_ip}
        return proxies
    '''
    #随机获取cookie
    def get_cookie(self):
        oneCookie = random.choice(hand_cookie)
        cookies = {"Cookie": oneCookie}
        return cookies

    # 获取用户昵称
    def get_username(self):
        try:
            url = "https://weibo.cn/%d/info" % (self.user_id)
            html = requests.get(url, cookies=self.get_cookie(), headers=self.my_headers).content
            sleep(0.04)
            # html = unicode(html_gb, "gb2312").encode("utf8")
            selector = etree.HTML(html)
            username = selector.xpath("//title/text()")[0]  # /html/head/title
            self.username = username[:-3]
            #查看系统当前编码
            print sys.getdefaultencoding()
            
            print isinstance(self.username,unicode)
            print u"用户名: " + self.username
        except Exception, e:
            print "\n Error: ", e
            traceback.print_exc()

    # 获取用户微博数、关注数、粉丝数
    def get_user_info(self):
        try:
            url = "https://weibo.cn/u/%d?filter=%d&page=1" % (
                self.user_id, self.filter)
            html = requests.get(url, cookies=self.get_cookie(), headers=self.my_headers).content
            sleep(0.03)
            selector = etree.HTML(html)
            pattern = r"\d+\.?\d*"

            # 微博数
            str_wb = selector.xpath(
                "//div[@class='tip2']/span[@class='tc']/text()")[0]
            guid = re.findall(pattern, str_wb, re.S | re.M)
            for value in guid:
                num_wb = int(value)
                break
            self.weibo_num = num_wb
            print u"微博数: " + str(self.weibo_num)

            # 关注数
            str_gz = selector.xpath("//div[@class='tip2']/a/text()")[0]
            guid = re.findall(pattern, str_gz, re.M)
            self.following = int(guid[0])
            print u"关注数: " + str(self.following)

            # 粉丝数
            str_fs = selector.xpath("//div[@class='tip2']/a/text()")[1]
            guid = re.findall(pattern, str_fs, re.M)
            self.followers = int(guid[0])
            print u"粉丝数: " + str(self.followers)
            print "==========================================================================="

        except Exception, e:
            print "Error: ", e
            traceback.print_exc()

    # 获取"长微博"全部文字内容
    def get_long_weibo(self, weibo_link):
        try:
            html = requests.get(weibo_link, cookies=self.get_cookie(), headers=self.my_headers).content
            sleep(0.03)
            selector = etree.HTML(html)
            info = selector.xpath("//div[@class='c']")[1]
            wb_content = info.xpath("div/span[@class='ctt']")[0].xpath(
                "string(.)").encode(sys.stdout.encoding, "ignore").decode(
                sys.stdout.encoding)
            wb_content = wb_content[1:]
            return wb_content
        except Exception, e:
            print "Error: ", e
            traceback.print_exc()

    # 获取用户微博内容及对应的发布时间、点赞数、转发数、评论数
    def get_weibo_info(self):
        try:
            url = "https://weibo.cn/u/%d?filter=%d&page=1" % (
                self.user_id, self.filter)
            my_headers = {"User-Agent": str(ua.random), "Accept-Encoding": "gzip, deflate, br", "Connection": "close"}
            html = requests.get(url, cookies=self.get_cookie(), headers=my_headers).content
            selector = etree.HTML(html)
            if selector.xpath("//input[@name='mp']") == []:
                page_num = 1
            else:
                page_num = (int)(selector.xpath(
                    "//input[@name='mp']")[0].attrib["value"])
            pattern = r"\d+\.?\d*"
            for page in range(1, page_num + 1):

                sleep(random.uniform(0.02, 0.04))
                if ((page % 10) == 0):
                    print datetime.now().strftime('%Y-%m-%d %H:%M')
                    print u"当前页数" + str(page)
                    sleep(random.randint(5, 8))

                url2 = "https://weibo.cn/u/%d?filter=%d&page=%d" % (
                    self.user_id, self.filter, page)

                # 更换请求头
                my_headers = {"User-Agent": str(ua.random), "Accept-Encoding": "gzip, deflate, br",
                              "Connection": "close"}
                html2 = requests.get(url2, cookies=self.get_cookie(), headers=my_headers).content

                sleep(0.02)
                selector2 = etree.HTML(html2)
                info = selector2.xpath("//div[@class='c']")
                is_empty = info[0].xpath("div/span[@class='ctt']")
                if is_empty:
                    for i in range(0, len(info) - 2):


                        # 微博内容
                        str_t = info[i].xpath("div/span[@class='ctt']")
                        weibo_content = str_t[0].xpath("string(.)").encode(
                            sys.stdout.encoding, "ignore").decode(
                            sys.stdout.encoding)
                        weibo_content = weibo_content[:-1]
                        weibo_id = info[i].xpath("@id")[0][2:]
                        a_link = info[i].xpath(
                            "div/span[@class='ctt']/a/@href")
                        if a_link:
                            if (a_link[-1] == "/comment/" + weibo_id or
                                    "/comment/" + weibo_id + "?" in a_link[-1]):
                                weibo_link = "https://weibo.cn" + a_link[-1]
                                wb_content = self.get_long_weibo(weibo_link)
                                if wb_content:
                                    weibo_content = wb_content
                        #判断是否为转发微博，若是则添加
                                    
                        self.weibo_content.append(weibo_content)
                        # print u"微博内容: " + weibo_content

                        # 微博位置
                        div_first = info[i].xpath("div")[0]
                        a_list = div_first.xpath("a")
                        weibo_place = u"无"
                        '''
                        for a in a_list:
                            if ("http://place.weibo.com/imgmap/center" in a.xpath("@href")[0] and
                                    a.xpath("text()")[0] == u"显示地图"):
                                weibo_place = div_first.xpath(
                                    "span[@class='ctt']/a")[-1]
                                if u"的秒拍视频" in div_first.xpath("span[@class='ctt']/a/text()")[-1]:
                                    weibo_place = div_first.xpath(
                                        "span[@class='ctt']/a")[-2]
                                weibo_place = weibo_place.xpath("string(.)").encode(
                                    sys.stdout.encoding, "ignore").decode(sys.stdout.encoding)
                                break
                        '''
                        self.weibo_place.append(weibo_place)
                        # print u"微博位置: " + weibo_place

                        # 微博发布时间
                        str_time = info[i].xpath("div/span[@class='ct']")
                        str_time = str_time[0].xpath("string(.)").encode(
                            sys.stdout.encoding, "ignore").decode(
                            sys.stdout.encoding)
                        publish_time = str_time.split(u'来自')[0]
                        if u"刚刚" in publish_time:
                            publish_time = datetime.now().strftime(
                                '%Y-%m-%d %H:%M')
                        elif u"分钟" in publish_time:
                            minute = publish_time[:publish_time.find(u"分钟")]
                            minute = timedelta(minutes=int(minute))
                            publish_time = (
                                    datetime.now() - minute).strftime(
                                "%Y-%m-%d %H:%M")
                        elif u"今天" in publish_time:
                            today = datetime.now().strftime("%Y-%m-%d")
                            time = publish_time[3:]
                            publish_time = today + " " + time
                        elif u"月" in publish_time:
                            year = datetime.now().strftime("%Y")
                            month = publish_time[0:2]
                            day = publish_time[3:5]
                            time = publish_time[7:12]
                            publish_time = (
                                    year + "-" + month + "-" + day + " " + time)
                        else:
                            publish_time = publish_time[:16]
                        self.publish_time.append(publish_time)
                        # print u"微博发布时间: " + publish_time

                        # 微博发布工具
                        if len(str_time.split(u'来自')) > 1:
                            publish_tool = str_time.split(u'来自')[1]
                        else:
                            publish_tool = u"无"
                        self.publish_tool.append(publish_tool)
                        # print u"微博发布工具: " + publish_tool

                        str_footer = info[i].xpath("div")[-1]
                        str_footer = str_footer.xpath("string(.)").encode(
                            sys.stdout.encoding, "ignore").decode(sys.stdout.encoding)
                        str_footer = str_footer[str_footer.rfind(u'赞'):]
                        guid = re.findall(pattern, str_footer, re.M)

                        # 点赞数
                        up_num = int(guid[0])
                        self.up_num.append(up_num)
                        # print u"点赞数: " + str(up_num)

                        # 转发数
                        retweet_num = int(guid[1])
                        self.retweet_num.append(retweet_num)
                        # print u"转发数: " + str(retweet_num)

                        # 评论数
                        comment_num = int(guid[2])
                        self.comment_num.append(comment_num)
                        # print u"评论数: " + str(comment_num)
                        # print "==========================================================================="

                        self.weibo_num2 += 1

            # 在此处进行文件的写入

            if not self.filter:
                print u"共" + str(self.weibo_num2) + u"条微博"
            else:
                print (u"共" + str(self.weibo_num) + u"条微博，其中" +
                       str(self.weibo_num2) + u"条为原创微博"
                       )

        except Exception, e:

            # 修改移动标志，不移动文件
            self.move_flag = 0

            print "Error: ", e
            traceback.print_exc()

    # 将爬取的信息写入文件
    def write_txt(self):
        try:
            if self.filter:
                result_header = u"\n\n原创微博内容: \n"
            else:
                result_header = u"\n\n微博内容: \n"
            result = (u"用户信息\n用户昵称：" + self.username +
                      u"\n用户id: " + str(self.user_id) +
                      u"\n微博数: " + str(self.weibo_num) +
                      u"\n关注数: " + str(self.following) +
                      u"\n粉丝数: " + str(self.followers) +
                      result_header
                      )
            for i in range(1, self.weibo_num2 + 1):
                text = (self.publish_time[i - 1] + "&#&" + str(i) + ":" + self.weibo_content[i - 1] +
                        u"微博位置: " + self.weibo_place[i - 1] +
                        # u"发布时间: " + self.publish_time[i - 1] +
                        u"点赞数: " + str(self.up_num[i - 1]) +
                        u"	 转发数: " + str(self.retweet_num[i - 1]) +
                        u"	 评论数: " + str(self.comment_num[i - 1]) +
                        u"发布工具: " + self.publish_tool[i - 1] + "\n"
                        )
                result = result + text
            file_dir = os.path.split(os.path.realpath(__file__))[
                           0] + os.sep + "weibo"
            if not os.path.isdir(file_dir):
                os.mkdir(file_dir)
            file_path = file_dir + os.sep + "%d" % self.user_id + ".wbdata"
            f = open(file_path, "wb")
            f.write(result.encode('utf-8'))
            print u"共" + str(self.weibo_num2) + u"条微博"
            f.close()

            # 根据移动标志判断是否移动当前文件到success文件夹
            if self.move_flag == 1:
                move_dir = os.path.split(os.path.realpath(__file__))[
                               0] + os.sep + "successdata"  # 更改文件夹名称
                if not os.path.isdir(move_dir):
                    os.mkdir(move_dir)
                move_path = move_dir + os.sep + "%d" % self.user_id + ".wbdata"

                shutil.move(file_path, move_path)
                print u"微博已爬取完毕,并移走"
                print move_path
            else:
                print u"爬取故障，微博写入文件完毕，保存路径:"
                print file_path

        except Exception, e:
            print "Error: ", e
            traceback.print_exc()

    # 运行爬虫
    def start(self):
        try:
            self.get_username()
            self.get_user_info()
            self.get_weibo_info()
            self.write_txt()
            print str(self.user_id) + u"信息抓取完毕"
            print "==========================================================================="
        except Exception, e:
            print "Error: ", e


def main():
    global location, ip_list, ip_proxies, ua,hand_cookie
    baseloc = os.path.split(os.path.realpath(__file__))[0]
    try:

        # 代理服务器
        # proxyHost = "112.29.170.230"
        
        proxyHost = "123.249.34.10"
        proxyPort = "888"
        # 代理隧道验证信息
        proxyUser = "te915w"
        proxyPass = "te915w"
        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxyHost,
            "port": proxyPort,
            "user": proxyUser,
            "pass": proxyPass,
        }

        '''代理IP地址
        114.237.220.160:3456
        180.112.66.106:3456
        111.176.249.201:3456
        '''
        ip_proxies = {'http': proxyMeta, "https": proxyMeta}

        #cookie
        '''
        hand_cookie = [
            'SCF=AoX08_bUGyw9JeuQN9en5JCICXjCuxM3R18fi67vZb2TzI9zZ83zI9ZtlUaF4-s59ATu9bNA8rjld_SjB-UiTt8.; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhjDW6Izh5Q998y9H2pElyC5JpX5K-hUgL.FoqfS0-ES0n7Shn2dJLoIEXLxK-LBo5L12qLxKML1hnLBo2LxKBLBonL12BLxKBLBonL122LxKnLB-qLB.-t; _T_WM=e815451ab6706b4c94860f316e1248e8; SUB=_2A25278wjDeRhGeBI7VQY8SvFyjiIHXVSE9RrrDV6PUJbkdBeLUGlkW1NRm7IjJ-HsfEYDZMXbmVW881C41NyZqJj; SUHB=0ebtwpii0T2xjK; SSOLoginState=1542175859',
            ]
        '''
        #hand_cookie = pickle.load(open("cookielistfile2", "rb"))

        cookiefile = open(baseloc + os.sep +'cookiestr.txt','r')
        cookiestr = cookiefile.read()
        hand_cookie = cookiestr.split('#')


        # 使用实例,输入一个用户id，所有信息都会存储在wb实例中
        # user_id = 3820000665  # 可以改成任意合法的用户id（爬虫的微博id除外）
        filter = 0  # 值为0表示爬取全部微博（原创微博+转发微博），值为1表示只爬取原创微博
        

        user = open(baseloc + os.sep +'01.txt', 'r')
        user_list = user.readlines()
        for line in user_list:
            sleep(random.randint(3, 8))
            #print(line)
            user_id = int(line.replace('\n', ''))
            try:
                wb = Weibo(user_id, filter)  # 调用Weibo类，创建微博实例wb
                wb.start()  # 爬取微博信息
                # 删除爬取成功的uid

            except:
                pass
            continue

        '''
        print u"用户名: " + wb.username
        print u"全部微博数: " + str(wb.weibo_num)
        print u"关注数: " + str(wb.following)
        print u"粉丝数: " + str(wb.followers)
        if wb.weibo_content:
            print u"最新/置顶 微博为: " + wb.weibo_content[0]
            print u"最新/置顶 微博位置: " + wb.weibo_place[0]
            print u"最新/置顶 微博发布时间: " + wb.publish_time[0]
            print u"最新/置顶 微博获得赞数: " + str(wb.up_num[0])
            print u"最新/置顶 微博获得转发数: " + str(wb.retweet_num[0])
            print u"最新/置顶 微博获得评论数: " + str(wb.comment_num[0])
            print u"最新/置顶 微博发布工具: " + wb.publish_tool[0]
        '''
    except Exception, e:
        print "Error: ", e
        traceback.print_exc()


if __name__ == "__main__":
    main()
