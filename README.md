# Beefalo
基于PyQt5的Windows启动器。  

因为很喜欢Wox的设计（还是Alfred？），就给Wox写了一些插件来实现一些功能。  
使用的过程中感觉Wox的bug还挺多的，用Python写插件给的接口又不够用，而且Wox项目也没什么人维护，所以就有了使用Python另起炉灶的想法。

Wox的功能，目前已经实现了我需要的部分，包括：
#### 网页搜索  
![网页搜索](https://pic.downk.cc/item/5e8bee29504f4bcb04c1742c.gif)
#### 本地文件查找（基于Everything）  
![本地文件查找](https://pic.downk.cc/item/5e8bee29504f4bcb04c1742e.gif)
#### 查单词（使用有道云API）  
![查单词](https://pic.downk.cc/item/5e8bee29504f4bcb04c17423.gif)
#### 插件提示

把我原来给Wox写的插件也做了转化，包括：
#### [随手记](https://github.com/enria/Wox.Plugin.SSJ)
#### [Formatter](https://github.com/enria/Wox.Plugin.Formatter)

另外，还实现了一些比较方便的功能：
#### 主题切换  
![主题列表](https://pic.downk.cc/item/5e8bf050504f4bcb04c2d078.gif)
#### 插件列表  
![插件列表](https://pic.downk.cc/item/5e8bee29504f4bcb04c17428.gif)


目前的功能都只是针对自已的需求实现的，为了其他用户使用，还有许多点需要做：
1. 打包，实现安装
2. 设置界面
