import re
import time
import csv
import os
import requests
import random
import pandas as pd
from selenium import webdriver
from pandas import DataFrame


class get_proxy:
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' \
                          ' AppleWebKit/537.36 (KHTML, like Gecko) ' \
                          'Chrome/61.0.3163.100 Safari/537.36'
        self.header = {"User-Agent": self.user_agent}
        self.proxy_file_name = 'Proxy.csv'
        self.time = 3
        if os.path.isfile(self.proxy_file_name):
            self.gotten = 1
        else:
            self.gotten = 0
        self.freshen = 0

        # user_agent:展示使用的user-agent
        # header:展示使用的header
        # proxy_file_name:展示文件保存的位置

    # 代理死的太多，默认爬取3页（3*100条数据）
    def get_content(self, num=3, name='Proxy.csv'):
        if self.gotten == 1:
            print('已获取代理信息')
        else:
            pass
        url = 'http://www.xicidaili.com/nn/'
        ori_proxy = []
        driver = webdriver.Chrome()
        for i in range(num):
            tar_url = url + str(i + 1)
            driver.get(tar_url)
            proxy = driver.find_elements_by_tag_name('tr')
            for j in proxy[1:]:
                ori_proxy.append(j.text)
            print('已获取第', i + 1, '页')
            time.sleep(1)
        print('获取完毕，开始保存！')
        driver.close()

        proxy = []
        count = 0
        for i in ori_proxy:
            ip_info = {}
            ori_info = re.split('[ ,\n]', i)
            ip_info['IP:PORT'] = ori_info[0] + ':' + ori_info[1]
            ip_info['IP'] = ori_info[0]
            ip_info['Port'] = ori_info[1]
            ip_info['Des'] = ori_info[2]
            ip_info['Protocol'] = ori_info[4]
            proxy.append(ip_info)
            count += 1
            print('第', count, '组数据整理完成')
        print('开始写入')
        proxy_frame = DataFrame(proxy)
        if name != 'Proxy.csv':
            self.proxy_file_name = name
        proxy_frame.to_csv(name, encoding='')

        print('保存完成,部分代理数据展示如下：')
        print(proxy_frame)
        self.gotten = 1

    # 只含有IP和端口，用来调用
    def proxy_list(self):
        with open(self.proxy_file_name) as file:
            proxy_reader = csv.reader(file)
            next(proxy_reader)
            pro_list = []
            for i in proxy_reader:
                pro_list.append([i[3], i[-1]])
            return pro_list

    def present_proxy(self):
        return pd.read_csv(self.proxy_file_name, encoding='gb2312')

    def find_dead(self):
        test_url = ['http://baidu.com', 'http://qq.com', 'http://zhihu.com']
        Dead_proxies = []
        count_url = 0
        count_dead = 0
        if self.gotten == 0:
            print('没有找到获取代理信息，即将开始获取')
            self.get_content(num=3)
        proxy_tobe_refresh = self.proxy_list()
        task_num = len(proxy_tobe_refresh)
        for i in proxy_tobe_refresh:
            proxy = {}
            proxy[i[-1].lower()] = ('http://' + i[0])
            url = test_url[random.randint(0, 2)]
            count_url += 1
            print(proxy, '正在测试中(第',count_url,'个，共', task_num,'个)')
            try:
                r = requests.get(url, headers= self.header, proxies=proxy, timeout = self.time)
                if r.status_code == 200:
                    print('通过测试！')
                else:
                    Dead_proxies.append(i[0])
                    print('未通过测试！')
                    count_dead += 1
            except:
                Dead_proxies.append(i[0])
                print('未通过测试')
                count_dead += 1
            time.sleep(1)
        print("共测试", count_url,"个链接")
        print("未通过共计",count_dead,"个， 通过共计", count_url - count_dead, "个")

        return Dead_proxies

    def fresh_proxy(self):
        proxies_tobe_removed = self.find_dead()
        print("确认是否更新列表？[Y/N]")
        wanna_fresh = input()
        if wanna_fresh == 'Y' or wanna_fresh ==  'y':
            new_proxy = []
            print('开始更新')

            with open(self.proxy_file_name, 'r') as file:
                reader = csv.reader(file)
                for i in reader:
                    if i[3] in proxies_tobe_removed:
                        print("已移除", i[3])
                    else:
                        new_proxy.append(i[1:])

            proxy_frame = DataFrame(new_proxy)
            proxy_frame.to_csv(self.proxy_file_name, encoding='')

            self.freshen = 1
        else:
            print("放弃更新")


if __name__ == '__main__':
    proxy = get_proxy()
    if proxy.gotten == 1:
        print('Proxy List is saved in:', proxy.proxy_file_name)
        print("是否重新获取？ [Y/N]")
        exc = input()
        if exc == 'Y' or exc == 'y':
            proxy.get_content()
    else:
        print('Can\'t find Proxy List, Get the List now? [Y/N]')
        exc = input()
        if exc == 'Y' or exc ==  'y':
            proxy.get_content()
    if proxy.freshen == 0:
        print("Fresh Proxy List? [y/n]")
        exc = input()
        if exc == 'Y' or exc ==  'y':
            proxy.fresh_proxy()
    else:
        print("Finished")

