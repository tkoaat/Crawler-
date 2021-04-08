
import requests
import re
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select
import numpy as np
import os
import matplotlib.pyplot as plt
from tqdm import tqdm

class mine_down():
    def __init__(self,savedir,savetxt):
        self.kv = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
        }
        self.savedir=savedir
        self.savetxt=savetxt#标签
        self.count=0

        self.prdir=""
        self.radir=""

        self.creatdir()
    def creatdir(self):
        try:
            self.prdir = self.savedir+'/processed'
            self.radir = self.savedir + '/raw'
            os.makedirs(self.prdir)
            os.makedirs(self.radir)
        except Exception as e:
            print(e)
    def txt2array(self,text):
        dd =text.split('\n')
        ddd=dd[9:-5]#删掉空行和文字
        nd=[]
        for d in ddd:
            a=np.array(d.split(','),dtype=np.float32)
            nd.append(a)
        return nd
    def download(self,textp,textr):
        urlp=textp['href']
        urlr=textr['href']
        try:
            p = requests.get(urlp, headers=self.kv)
            r= requests.get(urlr, headers=self.kv)
            p.encoding = 'utf-8'
            r.encoding = 'utf-8'
            pt=p.text
            rt=r.text
            pt=self.txt2array(pt)
            rt=self.txt2array(rt)
            print("over")
            try:
                pathp=self.prdir+'/lamanp_{}.npy'.format(self.count)
                np.save(pathp,pt)
                pathr=self.radir+'/lamanr_{}.npy'.format(self.count)
                np.save(pathr,rt)
                with open(self.savetxt, 'a') as f:
                    f.writelines(urlp+'\n')
                    f.writelines(urlr+'\n')
                    f.close()
                self.count = self.count + 1
            except:
                return 0
        except:
            return 0

    def minesecond(self,url=''):
        #选择框先看选择框
        r = requests.get(url, headers=self.kv)
        r.raise_for_status()
        r.encoding = 'utf-8'
        text = r.text
        soup = BeautifulSoup(text, 'html.parser')
        try:
            #先捞数字
            idlist=soup.find_all('select')
            idr=idlist[0]
            idf=idlist[1]
            idfname=idf['name']
            if idfname=='sample_child_record_raman_id':#有框
                seurl='https://rruff.info/index.php/r=sample_detail/download_type=sample_child_record_raman/module=download_box/NODISPLAY=1'
                try:
                    #构造网址
                    fa=idf.parent()[0]
                    sample_child_id = fa['value']
                    ffa=idr.parent()[0]
                    sample_id = ffa['value']
                    opt=idf.findAll('option')
                    opt=opt[:-1]
                    for op in opt:
                        sample_child_record_raman_id =op['value']
                        surl=seurl+'/sample_id='+sample_id+'/sample_child_id='+sample_child_id+'/sample_child_record_raman_id='+sample_child_record_raman_id
                        redata=requests.get(surl,verify=False)
                        rr=BeautifulSoup(redata.text, 'html.parser')
                        atag=rr.find_all('a')
                        self.download(atag[0],atag[3])
                except:
                    return 0
            else:
                print("数据缺失")
        except:
            return 0
    def mine(self,url=""):
        urls=url.split('info')
        urlb=urls[1]
        try:
            r = requests.get(url,headers=self.kv)
            r.raise_for_status()
            r.encoding = 'utf-8'
            text=r.text
            soup = BeautifulSoup(text, 'html.parser')
            target=soup.find_all('a',class_='page_link_2')
            for t in tqdm(target):
                try:
                    value=t.get('href')
                    l=re.match('.*'+(urlb)+'.*',value)
                    if l!=None:
                        ll=urls[0]+'info'+value
                        self.minesecond(ll)
                except:
                    return "没这个标签"
        except:
            return "错误"
    def plotsee(self,url="F:\dataset\laman\ceshi\processed/lamanp_0.npy"):
        zz = np.load(url)
        x = zz[:, 0]
        y = zz[:, 1]
        plt.plot(x, y)
        plt.show()


if __name__=="__main__":
    saveurl="F:\dataset\laman\ceshi"
    savetxt="F:\dataset\laman\ceshi/tag.txt"
    #url="https://rruff.info/chem=P/display=default/R080147"
    url="https://rruff.info/phosphate/display=default/"
    down=mine_down(saveurl,savetxt)
    down.mine(url)

    up="https://rruff.info/repository/sample_child_record_raman/by_minerals/Allanpringite__R080147__Raman__780__0__unoriented__Raman_Data_Processed__31610.txt"

