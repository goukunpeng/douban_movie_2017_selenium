#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
import os
import time
import json
import functools
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class GetDoubanMovie2017(object):

    def __init__(self):
        self.browser = webdriver.Chrome()   # 声明浏览器对象
        try:
            self.browser.get('https://movie.douban.com/')
        except TimeoutException:
            print("Time Out!")
        self.wait = WebDriverWait(self.browser, 10)

    def close_browser(self):
        self.browser.close()

    def click_catalog(self):
        # 点击目录按钮，获得点击次数（目录标题总数）,获得目录标题的名称
        try:
            button_movie = self.browser.find_elements_by_xpath('//div[@class="nav-items"]/ul/li/a')
        except NoSuchElementException as no_element:
            print(no_element)
            self.browser.close()
        else:
            button_movie[6].click()  # 点击2017年度电影榜
        try:
            # 等待目录按钮可点击
            self.button_catalog = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'icon-doulist')))
        except TimeoutException as timeout:
            print(timeout, '\n', 'Time Out!')
        except NoSuchElementException as no_element:
            print(no_element, '\n', 'No Element')
        else:
            self.button_catalog.click()
        # 获得目录标题的总数，即浏览器的点击标题的次数
        click_times = len(self.browser.find_elements(By.XPATH, '//nav[@data-scroll="free"]/ul/li/a'))
        if click_times > 0:
            # 获得目录标题的名称
            catalog_title_names = [name.text for name in
                                   self.browser.find_elements(By.XPATH, '//nav[@data-scroll="free"]/ul/li/a')]
            self.button_catalog.click()  # 再次点击目录按钮，关闭目录的弹出框
            return click_times, catalog_title_names

    def click_title(self, right_title_name, catalog_title_names, i):
        # 按照标题名称，对标题进行分类再点击
        '''
        1.台词开头的标题
        2.榜单电影开头的标题
        3.演员、导演结尾的标题
        4.逝者结尾的标题
        5.[4:5]为逝世的标题
        6.开篇、结束页、留言板
        '''
        self.button_catalog.click()  # 点击目录
        # 找到目录标题的节点。每次点击目录后，获得标题的节点的值是不一样的。
        time.sleep(0.2)
        self.wait.until(EC.presence_of_all_elements_located)
        try:
            catalog_title_element = self.browser.find_elements(By.XPATH, '//nav[@data-scroll="free"]/ul/li/a')[i]
        except IndexError as error:
            print("第{}次点击,出现错误{}".format(i, error.args))
        else:
            catalog_title_element.click()
        info = {}
        if catalog_title_names[i][0:2] == "台词":
            movie_taici = self.browser.find_element(By.CLASS_NAME, '_3hnav').text
            # movie_taici = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, '_3hnav'))).text
            movie_link = self.browser.find_element(By.XPATH, '//div[@class="_2MPhS"]/a').get_attribute('href')
            movie_name = self.browser.find_element(By.XPATH, '//div[@class="_2MPhS"]/a').text
            movie_info = {'name': movie_name, 'link': movie_link, 'taici': movie_taici}
            info['{}'.format(right_title_name)] = movie_info
        if catalog_title_names[i][0:4] == "榜单电影":
            movie_title = self.browser.find_elements(By.XPATH, '//li[@class="_3M3-l"]/a/p[@class="hBH2S"]')
            movie_link = self.browser.find_elements(By.XPATH, '//li[@class="_3M3-l"]/a')
            movie_info = {}
            for n in range(len(movie_title)):
                try:
                    movie_info['{}'.format(n)] = {'name': movie_title[n].text,
                                                  'link': movie_link[n].get_attribute('href')}
                except IndexError as error:
                    movie_info['Error'] = {'IndexError': error.args}
            info['{}'.format(right_title_name)] = movie_info
        if catalog_title_names[i][-2:] == "演员" \
                or catalog_title_names[i][-2:] == "导演" \
                or catalog_title_names[i][-2:] == "艺人":    # 布尔或  x or y,若x非0，返回x，否则返回y
            self.wait.until(EC.presence_of_all_elements_located)
            current_title_elements = self.browser.find_elements(By.XPATH, '//div[@class="_2pL9Z"]/h1/div')
            current_title_names = [name.text for name in current_title_elements]
            if current_title_names != []:  # 标题名称列表不为空
                movie_info = {}
                for x in range(len(current_title_names)):
                    if current_title_names[x] == right_title_name:  # 当前页面的第x个节点是我们要获取信息的标题节点
                        # top1
                        movie_ranks = [rank.text for rank in
                                       self.browser.find_elements(By.XPATH, '//h2/span[@class="bli1r"]')]
                        movie_names = [name.text for name in
                                       self.browser.find_elements(By.XPATH, '//div[@class="_1sV3Y"]/h2/a')]
                        movie_links = [link.get_attribute('href') for link in
                                       self.browser.find_elements(By.XPATH, '//div[@class="_1sV3Y"]/h2/a')]
                        try:
                            movie_info['0'] = {'rank': movie_ranks[x],
                                               'name': movie_names[x],
                                               'link': movie_links[x]
                                               }
                        except IndexError as error:
                            movie_info['0'] = {'{}: Top1'.format(right_title_name): error.args}
                        # top2 ~ top10
                        other_ranks = [rank.text for rank in
                                       self.browser.find_elements(By.CLASS_NAME, '_1RW3z')]
                        other_names = [name.text for name in
                                       self.browser.find_elements(By.CLASS_NAME, '_1Sah4')]
                        other_links = [link.get_attribute('href') for link in
                                       self.browser.find_elements(By.XPATH, '//li[@class="_3-jWQ"]/a')]
                        try:
                            for index, i in enumerate(range(9 * x, 9 * x + 9)):
                                movie_info['{}'.format(index+1)] = {
                                                                    'rank': 'Top' + ' ' + str(other_ranks[i]),
                                                                    'name': other_names[i],
                                                                    'link': other_links[i]
                                                                    }
                        except IndexError as error:
                            movie_info['Error'] = {'{}: Top2 ~ Top10'.format(right_title_name): error.args}
                        info['{}'.format(right_title_name)] = movie_info
                        # print(info)
        if catalog_title_names[i][-2:] == "逝者" or catalog_title_names[i][4:6] == "逝世":
            names = [name.text for name in
                     self.browser.find_elements(By.XPATH, '//ul[@class="_2twXO"]/li/div[@class="_3lvtk"]/span[1]')]
            eng_names = [eng_name.text for eng_name in
                         self.browser.find_elements(By.XPATH, '//ul[@class="_2twXO"]/li/div[@class="_3lvtk"]/span[2]')]
            links = [link.get_attribute('href') for link in
                     self.browser.find_elements(By.XPATH, '//ul[@class="_2twXO"]/li/a')]
            staff_and_ages = [info.text for info in
                              self.browser.find_elements(By.CLASS_NAME, '_2rYHH')]
            movie_info_list = {}
            if len(names) == len(eng_names) == len(links) == len(staff_and_ages):
                for num in range(0, len(names)):
                    movie_info_list['{}'.format(num)] = {'name': names[num], 'eng_name': eng_names[num],
                                                         'link': links[num], 'staff_and_age': staff_and_ages[num]}
                info['{}'.format(right_title_name)] = movie_info_list
            else:
                info['{}'.format(right_title_name)] = {'names': len(names), 'eng_names': len(eng_names),
                                                       'links': len(links), 'staff_and_ages': len(staff_and_ages)}
        if catalog_title_names[i] == "开篇" or catalog_title_names[i] == "结束页":
            pass
        if catalog_title_names[i] == "留言板":
            pass
        if "台词" not in catalog_title_names[i]\
                and "榜单电影" not in catalog_title_names[i]\
                and "演员" not in catalog_title_names[i]\
                and "导演" not in catalog_title_names[i]\
                and "逝者" not in catalog_title_names[i]\
                and "逝世" not in catalog_title_names[i]\
                and "开篇" not in catalog_title_names[i]\
                and "结束页" not in catalog_title_names[i]\
                and "留言板" not in catalog_title_names[i]\
                and "艺人" not in catalog_title_names[i]:   # 布尔与，x and y，x为false，返回false，否则返回y
            self.wait.until(EC.presence_of_all_elements_located)
            current_title_elements = self.browser.find_elements(By.XPATH, '//div[@class="_2pL9Z"]/h1/div')
            # 当前网页页面的目录标题名称
            current_title_names = [name.text for name in current_title_elements]
            if current_title_names != []:  # 标题名称列表不为空
                movie_info = {}
                for x in range(len(current_title_names)):
                    if current_title_names[x] == right_title_name:  # 当前页面的第x个节点是我们要获取信息的标题节点
                        # 找不到节点，列表会为空
                        # Top 1
                        movie_ranks = [rank.text for rank in
                                       self.browser.find_elements(By.XPATH, '//h2/span[@class="bli1r"]')]
                        movie_names = [name.text for name in
                                       self.browser.find_elements(By.XPATH, '//div[@class="_1sV3Y"]/div/h2/a')]
                        movie_links = [l.get_attribute('href') for l in
                                       self.browser.find_elements(By.XPATH, '//div[@class="_1sV3Y"]/div/h2/a')]
                        movie_scores = [score.text for score in
                                        self.browser.find_elements(By.XPATH,
                                                                   '//div[@class="l9yjH"]/span[@class="_1tnY9"]')]
                        try:
                            movie_info['0'] = {'rank': movie_ranks[x],
                                               'name': movie_names[x],
                                               'score': movie_scores[x],
                                               'link': movie_links[x]
                                               }
                        except IndexError as error:
                            movie_info['0'] = {"{}: Top 1".format(right_title_name): error.args}
                        # top2 ~ top10
                        other_ranks = [rank.text for rank in
                                       self.browser.find_elements(By.CLASS_NAME, '_1RW3z')]
                        other_names = [name.get_attribute('title') for name in
                                       self.browser.find_elements(By.XPATH, '//li[@class="_3-jWQ"]/a')]
                        other_links = [link.get_attribute('href') for link in
                                       self.browser.find_elements(By.XPATH, '//li[@class="_3-jWQ"]/a')]
                        other_scores = [score.text for score in
                                        self.browser.find_elements(By.CLASS_NAME, '_3TUe2')]
                        try:
                            for index, i in enumerate(range(9 * x, 9 * x + 9)):
                                movie_info['{}'.format(index+1)] = {'rank': 'Top' + ' ' + other_ranks[i],
                                                                    'name': other_names[i],
                                                                    'link': other_links[i],
                                                                    'score': other_scores[i]
                                                                    }
                        except IndexError as error:
                            movie_info['Error'] = {'{}: Top2 ~ Top10'.format(right_title_name): error.args}
                        info['{}'.format(right_title_name)] = movie_info
        return info


def run_time(func):
    @functools.wraps(func)
    def wrapper():
        start_time = datetime.now()
        print('start time:', start_time)
        func()
        end_time = datetime.now()
        print('end time:', end_time)
        used_time = datetime.timestamp(end_time) - datetime.timestamp(start_time)
        print('used time:', used_time)
    return wrapper


def main():
    movie = GetDoubanMovie2017()
    click_times, catalog_title_names = movie.click_catalog()
    for i in range(click_times):
        right_title_name = catalog_title_names[i]
        info = movie.click_title(right_title_name, catalog_title_names, i)
        content = {'{}'.format(i): info}
        try:
            json_data = json.dumps(content, indent=2, ensure_ascii=False)
        except TypeError:  # TypeError: Object of type 'type' is not JSON serializable
            print('{}'.format(right_title_name), '索引:', i, TypeError)
            continue
        yield json_data
    movie.close_browser()


@run_time
def write_to_json():
    filename = 'movie-2017.json'
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, 'a+', encoding='utf-8') as ff:
        for content in main():
            ff.write(str(content) + '\n')


if __name__ == '__main__':
    write_to_json()


'''
需解决的问题:
1. try..except..
try:
    pass
except IndexError:
    print(IndexError.args) 这样写获取不到IndexError的args，输出为<attribute 'args' of 'BaseException' objects>
若写成:
except IndexError as error:
    print(error.args)  输出为list index out of range

2. 要了解异常有哪些类型

3. TypeError: Object of type 'type' is not JSON serializable
第238行出现上述错误，是因为在上面的代码红，我将捕获的异常IndexError直接存入了字典里，而IndexError的类型为type
更多关于 TypeError: Object of type 'bytes' is not JSON serializable 问题参考链接:
https://blog.csdn.net/bear_sun/article/details/79397155
'''