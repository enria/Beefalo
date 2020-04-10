## Everything插件

### 插件设置

```json
{
  "everything_query_max": 50,
  "system_icon": false,
  "link_root": "C:\\Users\\13972\\Links"
}
```
`everything_query_max`: 设置查询返回结果的最大值，设为0则不限制（不建议） 
 
`system_icon`: 设为`true`则使用系统文件的图标  

`link_root`: 快捷方式的文件夹  

我们来详细解释一下快捷方式的文件夹的作用。  
参考Alfred的实现方法，使用`find`关键字来进行全局的文件搜索，在没有关键字的情况下只搜索应用程序。  
为了方便使用，我们可以将常用软件、链接、文件的快捷方式放入到一个文件夹，并将这个文件夹设为`link_root`，这样不需要关键字就可以搜索这些文件。

实现效果：  

快捷方式文件夹  

![软件](images/readme_everything_lnk.gif)  

![软件](images/readme_everything_url.gif)  

![软件](images/readme_everything_folder.gif)

全局搜索  

![软件](images/readme_everything_global.gif)


