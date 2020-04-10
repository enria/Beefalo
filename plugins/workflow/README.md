## Workflow插件
![MD5](images/readme_workflow_md5.gif)
### 插件设置

```json
{
  "flows": [
    {
      "name": "MD5",
      "script": "C:/Users/13972/Documents/Beefalo/scripts/md5.py",
      "input": "arg",
      "output": "dialog"
    }
  ]
}
```
`name`: 脚本名称 
`script`: 脚本文件   
`input`: 输入方式，可选`"arg"`、`"clipboard"`  
`output`: 输出方式，可选`"clipboard"`、`"dialog"`  






