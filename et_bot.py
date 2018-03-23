#-*- coding: utf-8 -*-
import time
import wget
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from seleniumrequests import PhantomJS
from bs4 import BeautifulSoup
import collections

BASEURL = 'http://everytime.kr/380952'
COMMENTURL = 'http://everytime.kr/ajax/moim/writecomment'
SURL = 'http://speller.cs.pusan.ac.kr/PnuWebSpeller/lib/check.asp'

class et_bot:
    def __init__(self, _userid, _password, _nick):
        self.userid = _userid
        self.password = _password
        self.driver = None
        self.postNum = 0
        self.sess = None
        self.text = None
        self.nick = _nick
        self.string = ""
        #self.check = False

    def login(self):
        self.driver = webdriver.PhantomJS('phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
        self.driver.implicitly_wait(3)
        self.driver.get('https://everytime.kr/login')
        self.driver.find_element_by_name('userid').send_keys(self.userid)
        self.driver.find_element_by_name('password').send_keys(self.password)
        self.driver.find_element_by_xpath('//*[@class="submit"]/input').click()
        
    def request(self):
        self.sess = requests.session()
        cookies = self.driver.get_cookies()
        for cookie in cookies:
            self.sess.cookies.set(cookie['name'], cookie['value'])

    def getPostNum(self):
        self.driver.get(BASEURL)
        WebDriverWait(self.driver, 5000).until(EC.visibility_of_element_located((By.CLASS_NAME, "status")))
        html = self.driver.page_source.encode("utf-8")
        soup = BeautifulSoup(html, 'html.parser')
        r = soup.find('a', class_ = "article")['href']
        
        """
       for link in soup.find('a', class_="article"):
            print(link.get('href'))
            r.append(link.get('href'))
        """
        self.postNum = r.split('/')[3]

    def getCommentPost(self):
        self.driver.get(BASEURL + '/v/' + str(self.postNum))
        WebDriverWait(self.driver, 50).until(EC.visibility_of_element_located((By.CLASS_NAME, "profile")))
          
        #title and content
        html = self.driver.page_source.encode("utf-8")
        soup = BeautifulSoup(html, 'html.parser')
        self.text = soup.find('p', class_ = "large").getText()

        """
        commentWriter = soup.findAll('h3', class_ = "medium")

        for i in commentWriter:
            if i.text == self.nick:
                print("overlap")
                self.check = True
        """

    def syntaxCleaner(self):
        self.string = ""
        syntax_dict = collections.OrderedDict()
        data = {'text1' : self.text}
        s = requests.post(SURL, data = data)
        html = s.content
        soup = BeautifulSoup(html, 'html.parser')
        tdError = soup.findAll('td', class_ = "tdErrWord")
        tdReplace = soup.findAll('td', class_ = "tdReplace")
        tdHelp = soup.findAll('td', id = "tdHelp_")
        n = len(tdReplace)

        for ctr in range(0, n):
            tdHelp = soup.find('td', id = "tdHelp_" + str(ctr))
            tdHelp = tdHelp.text
            tdHelp = tdHelp.split('.')[0]
	    #except
	    if tdHelp == u"우리말에서 온점(":
                tdHelp = u"우리말에서 온점은 앞에 오는 말에는 붙여 쓰지만, 뒤에 오는 말과는 띄어 써야 바릅니다."

            if len(tdHelp) > 50:
                tdHelp = ""
            e = [tdReplace[ctr].text, tdHelp]
            syntax_dict[tdError[ctr].text] = e

        for key, value in syntax_dict.iteritems():
	    if value[0] == u"맞춤법 로봇맞춤법 못":
		    value[0] = u"맞춤법 로봇"
	    elif value[0] == u"로봇못":
		    value[0] = u"로봇"
            st = "\"" + key + "\"" + "-> " + value[0] + "(" + value[1] + ")" +  '/ '   + '\n'
            self.string  = self.string + st

    def commentWrite(self):
        self.syntaxCleaner()
        if len(self.string) != 0:
            data = {'text' : self.string, 'is_anonym' : '1', 'id' : str(self.postNum)}
            self.sess.post(COMMENTURL, data = data)
            print(self.string)
        else:
            print("collect syntax")

    def runBot(self):

        prepostNum = [None] * 7
        idx = 0 

        while(1):
            time.sleep(3)
            try:
                bot.getPostNum()
            except:
                bot.getPostNum()

            if bot.postNum not in  prepostNum:
                print(bot.postNum)
                bot.getCommentPost()
                bot.commentWrite()
                prepostNum[idx] = bot.postNum
                idx += 1
            if idx == 7:
                idx = 0


if __name__ == "__main__":
    bot = et_bot('xxx', 'xxxx', 'id')
    bot.login()
    bot.request()
    bot.runBot()
