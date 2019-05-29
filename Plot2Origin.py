# -*- coding: utf-8 -*-
"""
Created on Mon May 27 01:25:37 2019
将文件夹下所有的数据文件导入到Origin表格并在其中绘图
@author: falli
"""

import os
import pandas as pd
import OriginExt as O

def ImportData2Plot(data,wksname,grfname,template,opjfile):
    if len(data)==0:
        return None
    origin = O.Application(); origin.Visible = origin.MAINWND_SHOW
    origin.NewProject; origin.Execute("sec -poc 5")
    #instanse-page-layer
    workbook = origin.CreatePage(2,wksname,"origin") # 2 for WorksheetPage
    wb = origin.WorksheetPages(workbook)              # get workbook instance from name 
    graph = origin.CreatePage(3,grfname,template) # Make a graph (3 for GraphPage) with the template
    graph_page = origin.GraphPages(graph) # Get graph page
    graph_layer = graph_page.Layers(0)    # Get graph layer
    
    bands=list(set(data['Band']))
    for i in range(len(bands)):
        band=bands[i]
        if i>0 : wb.Layers.Add()  # add more worksheets with wb.Layers.Add()
        ws=wb.Layers(i)           # get worksheet instance, index starts at 0.
        ws.Name=wksname+'_'+band  # Set worksheet name
    
        # Put the data into the worksheet
        for j in range(data.shape[1]):
            origin.PutWorksheet('['+wb.Name+']'+ws.Name,data[data.columns[j]][data['Band']==band].values, 0, j) # row 0, col 0
            ws.Columns[j].SetLongName(data.columns[j])
        ws.Columns[2].SetType(2)             # column type 2 for yErr
        ws.Columns[1].SetComments(band)      # set comments
        #if i>0 : graph_page.Layers.Add()    # this script will double the axies;
        #graph_layer = graph_page.Layers(0)   # Get graph layer
        dr = origin.NewDataRange()           # Make a new datarange
        # Add data to data range
        # Column type, worksheet, start row, start col, end row (-1=last), end col
        dr.Add('X', ws, 0 , 0, -1, 0)
        dr.Add('Y', ws, 0 , 1, -1, 1)
        # Add data plot to graph layer
        symbols={'N/A':'20','NA':'20','Vis.':'2','B':'8','V':'1','R':'5','I':'17','CR':'5','CV':'1','TG':'17','Green-Vis.':'8','SG':'19'}
        colors={'N/A':'#FFFF00','NA':'#FFFF00','Vis.':'#000000','B':'#0000FF','V':'#008000','R':'#FF0000','I':'#FF00FF','CR':'#A52A2A','CV':'#00FFFF','TG':'#800080','Green-Vis.':'#ADFF2F','SG':'#06857B'}
        if band not in symbols.keys(): symbols[band]='7';colors[band]='#8B0000'
        graph_layer.AddPlot(dr,201) # 201--symbol
        graph_layer.Execute(
                'range rr = !' + str(i+1)      + '; ' +
                'set rr -k '   + symbols[band] + ';'  + # symbol type
                'set rr -kf 0;'+       # symbol interior 0 = solid
                'set rr -z '   + str(6) + ';' + # symbol size
                'set rr -c  color('+colors[band]+');'+ # edge color
                'set rr -cf color('+colors[band]+');'+ # face color
                'set rr -kh 10*'+str(1)+';') # edge width
    # Get axes ranges
    x_range=data['HJD'][len(data['HJD'])-1]-data['HJD'][0];
    y_range=data['Magnitude'].max()-data['Magnitude'].min()
    x_axis_range = (data['HJD'][0]-x_range/10,data['HJD'][0]+x_range*11/10)
    y_axis_range = (data['Magnitude'].max()+y_range/10,data['Magnitude'].min()-y_range/10)
    graph_layer.Execute('layer.x.from = ' + str(x_axis_range[0]) + '; ' + 
                        'layer.x.to   = ' + str(x_axis_range[1]) + ';')
    graph_layer.Execute('layer.y.from = ' + str(y_axis_range[0]) + '; ' + 
                        'layer.y.to   = ' + str(y_axis_range[1]) + ';')
    # save the origin project and exit
    origin.Save(opjfile)
    origin.Exit()

def data1txt(datafile):
    aavsodata=pd.read_csv(datafile,header=0,na_filter=False,dtype={'HJD':float,'Magnitude':float})  #将NA,N/A等识别为字符
    if len(aavsodata)==0:
        return aavsodata,'x'
    starname=aavsodata['Star Name'][0]
    data=pd.DataFrame({'HJD':aavsodata['HJD']-2450000,'Magnitude':aavsodata['Magnitude'],\
                       'Uncertainty':aavsodata['Uncertainty'],'Band':aavsodata['Band'],\
                       'Observer':aavsodata['Observer Code']})
    return data,starname

def Good_Name(string):
    '''
    windows下\/:*?"<>|不能出现在文件名中，需要去掉;
    '''
    return string.replace('\\','').replace('/','').replace(':','').replace('*','').replace('?','').replace('"','').replace('<','').replace('>','').replace('|','').replace(' ','')

template='C:\\Users\\falli\\Documents\\OriginLab\\User Files\\AAVSO_SCATTER.otpu'

for file in os.listdir(os.getcwd()):
    if os.path.isdir(file):
        try:
            print(file+'\n')
            datafile=[os.path.join(os.getcwd(),file,txt) for txt in os.listdir(file) if 'neat_' in txt][0]
        except:
            continue
        data,starname=data1txt(datafile);
        opjfile=os.path.join(os.getcwd(),file,Good_Name(starname)+'.opj')  
        ImportData2Plot(data,starname,starname,template,opjfile)
        
        
        
        
        
        

