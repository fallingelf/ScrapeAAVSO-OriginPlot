# -*- coding: utf-8 -*-
"""
Created on Mon May 20 10:04:10 2019
通过目标源文件列表检索AAVSO并下载观测数据
@author: falli
"""

import os,requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from astropy import units as u
from matplotlib import pyplot as plt
from astropy.coordinates import SkyCoord
from PyAstronomy.pyasl.asl.astroTimeLegacy import helio_jd

def mkdir(folder):
    '''
    '''
    if not os.path.exists(folder):
        os.mkdir(folder)

def lb2radec(l,b):
    '''
    将银道坐标转换(l,b)为赤道坐标(ra,dec);
    '''
    radec=SkyCoord(l=l,b=b,frame='galactic',unit='deg').icrs
    return str(radec.ra.value)+' '+str(radec.dec.value)

def GetHtml(url):
    '''
    用Get方法访问url;
    '''
    try:
        r=requests.get(url)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        return r.text
    except:
        print('出现异常-GetHtml')

def PostHtml(url,data):
    '''
    用Post方法访问url;
    '''
    try:
        r=requests.post(url,data=data)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        return r.text
    except:
        print('出现异常-PostHtml')

def AimAMStar(bsobj,iterms_save_file=os.path.join(os.getcwd(),'Results4RaDec.txt')):
    '''
    对于坐标检索VSX得到的多个源进行有条件的筛选，得到第一个符合条件的目标并保存在文件Results4RaDec.txt中;
    返回值为此目标的url;
        -此函数筛选变星类型中含有'AM'或者是'NA'的目标。
    '''
    Object=[];VariabilityType=[];AMStar='';AMStarType=''
    for iterm in bsobj.findAll('span',{'class':'desig'}):
        Object.append(iterm.string)
        VariabilityType.append(iterm.parent.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.string)
        if ('AM' in VariabilityType[-1]) or ('NA' in VariabilityType[-1]):
            AMStar=Object[-1];AMStarType=VariabilityType[-1]
            AMStar_url=iterm.a.attrs['href']
    with open(iterms_save_file,'a') as f:
        f.write(str(Object)+'    '+str(VariabilityType)+'    '+'['+AMStar+',    '+AMStarType+']'+'\n')
    print('['+AMStar+',    '+AMStarType+']')
    return AMStar_url

def GetVSX(star_name='',radec=''):   
    '''
    通过关键字(star_name或者radec)得到目标的相关信息;
    star_name:
        目标名检索返回有两种结果(1)没有目标信息;(2)直接进入目标信息页;
    radec:
        坐标检索返回两种结果(1)没有目标信息;(2)列出靠近坐标的所有变星目录;
        对于情况(2)利用AimAMStar()获得满足条件的目标url
    '''
    data={'ql':'1','getCoordinates':'0','plotType':'Search','special':'index.php?view=results.special&sid=2',\
          'ident':star_name,'constid':'0','targetcenter':radec,'format':'s','fieldsize':'10','fieldunit':'2',\
          'geometry':'r','filter[]':{'0':'0','1':'1','2':'2','3':'3'},'order':'1'}
    url='https://www.aavso.org/vsx/index.php?view=results.submit1'
    try:
        if radec!='':
            data['ident']=''
            htmlstr=PostHtml(url,data)
            if 'There were no records that matched the search criteria.' in htmlstr:
                return None,None,None,None
            bsobj=BeautifulSoup(htmlstr,'html5lib')
            htmlstr=GetHtml('https://www.aavso.org/vsx/'+AimAMStar(bsobj))
        else:
            htmlstr=PostHtml(url,data)
            if 'There were no records that matched the search criteria.' in htmlstr:
                return None,None,None,None
        #with open(os.path.join(os.getcwd(),'ss.html'),'w') as f:
        #    f.write(htmlstr)
        bsobj=BeautifulSoup(htmlstr,'html5lib')
        name=bsobj.find('td',string='Name').next_sibling.next_sibling.span.string.replace('\n','').replace('\xa0',' ').replace(')','').replace('(',';')
        uid=bsobj.find('td',string='AAVSO UID').next_sibling.next_sibling.td.string.replace('\n','').replace('\xa0',' ').replace(')','').replace('(','#')
        radec=bsobj.find('td',string='J2000.0').next_sibling.next_sibling.td.string.replace('\n','').replace('\xa0',' ').replace(')','').replace('(',';').split(';')[0]
        epoch=bsobj.find('td',string='Epoch').next_sibling.next_sibling.td.string.replace('\n','').replace('\xa0',' ').replace(')','').replace('(',';').split('HJD')[-1]
        period=bsobj.find('td',string='Period').next_sibling.next_sibling.string.replace('\n','').replace('\xa0',' ').replace(')','').replace('(',';').split('d')[0]   
        if epoch == '--':
            epoch=0
        return name,uid,radec,float(epoch),period
    except:
        print('出现异常-GetVSX')

def PostAAVSO(star_name):
    '''
    两步检索AAVSO，第一次检索获得关键字'form_build_id'，并作为表单值进行第二次检索;
    '''
    url='https://www.aavso.org/data-download'
    data={'auid':star_name,'start':'All','stop':'All','firstname':'','lastname':'','email':'','country':'',\
      'affiliation':'','whoami':'Student','purpose':'Data Analysis','discrepant':'no','mtypeinput':'no',\
      'zformat':'csv','comments':'','submit.x':'45','submit.y':'22','form_build_id':'','form_id':'dd_form'}
    try:
        form_key=BeautifulSoup(GetHtml(url),'html5lib').find('input',{'name':'form_build_id'}).attrs['value']
        data['form_build_id']=form_key
        return PostHtml(url,data)
    except:
        print('出现异常-PostAAVSO')

def Get_data_url(bsobj):
    '''
    获取AAVSO数据url;
    '''
    return 'https://www.aavso.org'+bsobj.find('a',string='Click here to access your data file').attrs['href']

def Good_Name(string):
    '''
    windows下\/:*?"<>|不能出现在文件名中，需要去掉;
    '''
    return string.replace('\\','').replace('/','').replace(':','').replace('*','').replace('?','').replace('"','').replace('<','').replace('>','').replace('|','').replace(' ','')

def WashData(data):
    '''
    将星等含有‘<’的数据去掉;
    '''
    for i in range(len(data)):
        if '<' in str(data['Magnitude'][i]):
            data=data.drop(i,axis=0)
    return data

def PhaseData(data_in_file,data_out_file,radec,epoch,period):
    '''
    添加HJD与相位;
    '''
    pho_data=WashData(pd.read_csv(data_in_file,header=0,na_filter=False))  #row 0 is titles
    pho_data['HJD']=np.array([helio_jd(jd-2400000,radec.ra.value,radec.dec.value)+2400000 for jd in pho_data['JD']])
    if period!='--':
        period=float(period)
        pho_data['Phase']=round(((pho_data['HJD']-epoch)/period) % 1 , 4)
    pho_data.to_csv(data_out_file,index=False,header=True,sep=",")  
    return pho_data

def PlotNeatData(starname,neatdata,figout):
    '''
    将不同波段的数据分别绘成不同的符号
    '''
    if len(neatdata)==0:
        return None
    markers={'N/A':'yo','NA':'yo','Vis.':'ko','B':'b*','V':'gs','R':'rD','I':'mh','CR':'rp','CV':'cp','TG':'cp','Green-Vis.':'gp','SG':'gP'}
    for band in set(neatdata['Band']):
        if band not in markers.keys():
            markers[band]='rx'
        plt.plot(neatdata['HJD'][neatdata['Band']==band].astype(float)-2400000,neatdata['Magnitude'][neatdata['Band']==band].astype(float),markers[band],label=band,markersize=10)
    plt.gcf().set_size_inches(30,15)
    plt.gca().invert_yaxis();plt.legend(loc='best',fontsize=20)
    plt.title('AAVSO Data for '+starname,fontsize=20);
    plt.xlabel('HJD (+2400000)',fontsize=20);plt.ylabel('Magnitude',fontsize=20)
    plt.tick_params(labelsize=20);
    plt.grid()
    plt.savefig(figout,dpi=100)
    plt.show() 
    
#目标源文件
Catalog_AM=pd.read_csv(os.path.join(os.getcwd(),'VSX_AM_All.csv'),header=0,na_filter=False) 

for i in range(len(Catalog_AM)):
    #l=float(Catalog_AM.loc[i]['l']);b=float(Catalog_AM.loc[i]['b']);radec=lb2radec(l,b)
    print('----------------------------------------------------------------------------------------\n')
    print(i,'. ',Catalog_AM['Name'][i],'\n')
    #通过关键词访问VSX获取目标相关信息;
    star_name,uid,radec,epoch,period=GetVSX(star_name=Catalog_AM['Name'][i],radec='')
    star_inf={'StarName':star_name,'Epoch':epoch,'Period':period,'RaDec':SkyCoord(radec, unit=(u.hourangle, u.deg))}
    #保存得到的目标信息;
    with open(os.path.join(os.getcwd(),'Inf1VSX.dat'),'a+') as f:
        f.write(star_name+','+str(uid)+','+str(radec)+','+str(epoch)+','+str(period)+'\n')
    
    if ('No observations' in uid) or (uid == '--'):
        print('No observations in AAVSO')
    else:
        #爬取数据并保存为文件;
        folder_out=os.path.join(os.getcwd(),Good_Name(star_name));mkdir(folder_out)
        datafile=os.path.join(folder_out,Good_Name(star_name)+'.txt')
        bsobj=BeautifulSoup(PostAAVSO(star_name),'html5lib')
        with open(datafile,'w+') as f:
            f.write(GetHtml(Get_data_url(bsobj)))
        #整理数据并画图
        neatfile=os.path.join(folder_out,'neat_'+Good_Name(star_name)+'.txt')
        neatdata=PhaseData(datafile,neatfile,star_inf['RaDec'],star_inf['Epoch'],star_inf['Period'])
        figout=datafile.replace('.txt','.png')
        PlotNeatData(star_name,neatdata,figout)














