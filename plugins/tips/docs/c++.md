每个内存的使用都需要申请


循环中的结构体等局部变量，内存会被清除，留给下一个使用


maps.begin maps.end it->first it->second


1012 临时变量、map中添加的value、数组中的元素，指针不同。


栈内存由OS动态开辟回收，我们malloc的内存时是在堆中，需要我们手动释放，否则就会内存泄露。


[2020-02-13 12:24:39] memset(*n,1|0,sizeof(type)*len)


[2020-02-13 03:52:07] 并查集：将有关系的结点组成一个集合


[2020-02-13 04:16:59] 在对问题进行建模的时候，我们应该尽量想清楚需要解决的问题是什么。


[2020-02-17 09:41:28] int n[m] 就是申请数组，如果需要指向一个数组，可以用指针int *n代替。


[2020-02-17 10:05:33] 0=false，-1||1=true


[2020-02-17 12:33:45] pop之后都要判断一下队列是否为空


[2020-02-18 11:24:51] string=char[]可以这样赋值


[2020-02-18 11:53:08] 指针取值*p，取变量指针&n


[2020-02-18 06:28:28] queue<btn*> q;


[2020-02-20 10:44:54] c


[2020-02-21 05:07:32] map中的元素（pair）放到序列容器（如vector）中，再用sort进行排序。


[2020-02-23 03:19:20] 大数字用python秒杀


[2020-02-24 01:16:51] string a="123""456";


[2020-02-25 10:16:54] 如果下标算起来太绕，直接多开一个，从1开始使用数组。写起来，思考起来都很方便，读起来也比较友好。


[2020-02-29 03:30:12] 大数据量(超过10000)都不要去用python


[2020-02-29 04:29:31] c++ vector push_back对象的时候存起来的是拷贝


[2020-02-29 04:40:23] %ld用于long类型，%lld用于long long类型。


[2020-02-29 05:14:47] sort函数，comp结果为true，是第一个参数排在前面


[2020-02-29 05:40:36] 结构体结尾处有个分号


[2020-02-29 07:50:57] 大量数据的输入，用scanf，而不是cin


[2020-03-01 03:39:08] 边的储存，因为题目限制65536kb,如果直接用数组int[10000][10000]至少用了800000000/1024 = 781 250kb


[2020-03-01 10:18:28] printf("%lu", vector.size());


[2020-03-01 10:39:07] 注意多重循环的break


[2020-03-03 09:15:07] 以数字型作为地址时，注意输出时的格式（一般前面都带0）


[2020-03-08 05:38:26] map的实现是一颗红黑树，因此，map的内部键的数据都是排好序的，查找和删除、插入的效率都是lgN。


[2020-03-09 04:31:02] 平方探测法：H(key)=( key + i ^ 2 ) % TSize，其中Tsize为表长，i取值为[1,Tsize/2]。若i超出范围，就说明表中找不到合适的位置。


[2020-03-09 05:30:13] index不能作为变量名


[2020-03-10 03:46:07] 有两种传递方法，一种是function(int a[]); 另一种是function(int *a)


[2020-03-10 03:46:15] 这两种两种方法在函数中对数组参数的修改都会影响到实参本身的值！


[2020-03-10 03:47:02] 这里也不能在test()函数内部用sizeof求数组的大小，必须在外面算好了再传进来。


[2020-03-11 11:29:53]  由于是升序，所以可用用一个数组count_time[24 * 60 * 60]模拟（挺好的思路）


[2020-03-12 12:07:48] 对他们排序，先按照车牌号排序，再按照来的时间先后排序。


[2020-03-12 04:19:13] int as={{}};int *a=as[0];这里只能用指针，不能赋值。


[2020-03-12 08:48:34] 一定要搞清楚index


[2020-03-19 09:11:17] 相乘和相加要考虑溢出


[2020-03-19 09:12:17] 如果时间较长的测试没通过，考虑数值溢出问题


[2020-03-20 05:40:54] 考虑连通数，优先使用并查集，效率很高


[2020-03-21 03:12:43] 双端队列：deque


[2020-03-22 06:17:36] 大型项目用什么编辑器或IDE根本无所谓，关键的是build tool。


[2020-03-23 12:01:17] string和char[]不能直接用等号判断是否相等


[2020-03-23 12:01:44] 结构体中的变量有默认初始值


[2020-03-24 11:44:43] C++ is not a tool for website development at all.


[2020-03-27 10:43:22] 红黑树也是二叉查找树


[2020-03-27 01:53:07] 但要保持红黑树的性质，结点不能乱挪，还得靠变色了。




