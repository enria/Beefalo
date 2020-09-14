# Beefalo

基于PyQt5的Windows启动器。  

因为很喜欢Wox的设计（还是Alfred？），就给Wox写了一些插件来实现一些功能。  
使用的过程中感觉Wox的bug还挺多的，用Python写插件给的接口又不够用，而且Wox项目也没什么人维护，所以就有了使用Python另起炉灶的想法。

## [安装](安装.md)

## 功能
Wox的功能，目前已经实现了我需要的部分，包括： 

+ [网页搜索](plugins/web_search)
+ [本地文件查找](plugins/everything)（基于Everything）
+ [查单词](plugins/translate)（使用有道云API）
+ [插件提示](plugins/plugin_hint)
+ [计算器](plugins/calculator)
+ [系统命令](plugins/system_cmd)


把我原来给Wox写的插件也做了转化，包括：  
+ [随手记](https://github.com/enria/Wox.Plugin.SSJ)  
+ [Formatter](https://github.com/enria/Wox.Plugin.Formatter)

另外，还实现了一些比较方便的功能：
+ [Workflow](plugins/workflow)
+ [API文档](plugins/api_doc)
+ [GitHub](plugins/github)
+ [TODO](plugins/todo)
+ [主题切换](plugins/theme)
![主题列表](images/readme_theme.gif)
+ [插件列表](plugins/plugin_hint)  
![插件列表](images/readme_plugin.gif)

## TODO
目前的功能都只是针对自已的需求实现的，为了其他用户使用，还有许多点需要做：
1. 打包，实现安装
2. 设置界面
