import re
import time
import csv
import os
import requests
import random
import pandas as pd
from selenium import webdriver
from pandas import DataFrame


class get_proxy(Proxy_flie_name = 'Proxy.csv'):
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' \
                          ' AppleWebKit/537.36 (KHTML, like Gecko) ' \
                          'Chrome/61.0.3163.100 Safari/537.36'
        self.header = {'User-Agent':self.user_agent}

        if os.path.isfile(self.Proxy_flie_name):
            self.gotten = 1
        else:
            self.gotten = 0

        if self.gotten == 0:
            print('尚未获取代理信息或者信息已丢失')
            print('请使用 get_content 方法重新获取')
            self.proxy = None
        else:
            self.proxy = self.present_proxy()

        #user_agent:展示使用的user-agent
        #header:展示使用的header
        #Proxy_file_name:展示文件保存的位置
        #proxy:展示全部数据

    def get_content(self, num = 3, name = 'Proxy.csv'):
        url = 'http://www.xicidaili.com/nn/'
        ori_proxy = []
        driver = webdriver.Chrome()
        for i in range(num):
            tar_url = url + str(i+1)
            driver.get(tar_url)
            proxy = driver.find_elements_by_tag_name('tr')
            for j in proxy[1:]:
                ori_proxy.append(j.text)
                print('已获取第',i+1,'页')
            time.sleep(1)
        print('获取完毕，开始保存！')
        driver.close()

        proxy = []
        for i in ori_proxy:
            ip_info = {}
            ori_info = re.split('[ ,\n]', i)
            ip_info['IP:PORT'] = ori_info[0] + ':' + ori_info[1]
            ip_info['IP'] = ori_info[0]
            ip_info['Port'] = ori_info[1]
            ip_info['Des'] = ori_info[2]
            ip_info['Protocol'] = ori_info[4]
            proxy.append(ip_info)
            print('第',i+1,'组数据整理完成')
        print('开始写入')
        proxy_frame = DataFrame(proxy)
        if name != 'Proxy.csv':
            self.Proxy_flie_name = name
        proxy_frame.to_csv(name, encoding='')

        print('保存完成,部分代理数据展示如下：')
        print(proxy_frame)
        self.gotten = 1
        self.proxy = proxy_frame

    #只含有IP和端口，用来调用
    def proxy_list(self):
        with open(self.Proxy_flie_name) as file:
            proxy_reader = csv.reader(file)
            pro_list = []
            for i in proxy_reader:
                pro_list.append([i[3], i[-1]])
            return pro_list

    def present_proxy(self):
        return pd.read_csv(self.Proxy_flie_name, encoding='gb2312')

    def find_dead(self):
        test_url = ['http://baidu.com', 'http://qq.com', 'http://zhihu.com']
        Dead_proxies = []
        if self.gotten == 0:
            print('没有找到获取代理信息，即将开始获取')
            self.get_content(num=3)
        proxy_tobe_refresh = self.proxy_list()

        for i in proxy_tobe_refresh:
            proxy = {}
            proxy[i[-1].lower()] = ('http://' + i[0])
            url = test_url[random.randint(0,2)]
            print(proxy, '正在测试中')
            try:
                r = requests.get(url, headers=self.header, proxies=proxy)
                if r.status_code == 200:
                    print('通过测试！')
                else:
                    Dead_proxies.append(i[0])
                    print('未通过测试！')
            except:
                Dead_proxies.append(i[0])
                print('未通过测试')
                continue
            time.sleep(1)
        return Dead_proxies

    def fresh_proxy(self):
        proxies_tobe_removed = self.find_dead()
        new_proxy = []
        print('开始更新')
        with open(self.Proxy_flie_name, 'r') as file:
            reader = csv.reader(file)
            print('开始进行校核操作')
            for i in reader:
                for j in proxies_tobe_removed:
                    if j in i:
                        print('已删除',j)
                        continue
                    else:
                        new_proxy.append(i)

        with open(self.Proxy_flie_name, 'w', newline='') as file:
            print('开始重新写入.....')
            writer = csv.writer(file)
            for i in new_proxy:
                writer.writerow(i)
            print('更新完毕')




