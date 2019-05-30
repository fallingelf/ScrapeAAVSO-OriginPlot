# ScrapeAAVSO-OriginPlot


#依赖库：

numpy, pandas, bs4, requests, astropy, matplotlib, PyAstronomy, pypiwin32, OriginExt


#操作步骤

1.VSX上检索某一类型源，保存结果为csv文件；

2.修改ScrapeAAVSO.py中的变量值‘Catalog_AM’为csv文件名，然后运行此脚本获得AAVSO上的数据并得到png图；

3.在Plot2Origin.py中添加绘图模板参数（修改‘template’值），运行后得到origin文件。
