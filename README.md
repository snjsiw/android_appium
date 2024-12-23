* 自动化流量采集技术原理与使用说明

  ## 一、技术原理

  ### 1、Appium自动化测试框架

  ![img](file:///C:/Users/lenovo/AppData/Local/Temp/msohtmlclip1/01/clip_image002.gif)

  ### 2、ADB（Android调试桥）

  当启动某个 adb 客户端时，客户端会先检查是否有 adb 服务器进程正在运行。如果没有，它将启动服务器进程。服务器在启动后会与本地TCP 端口 5037 绑定，并监听 adb 客户端发出的命令 – 所有 adb 客户端均通过端口 5037 与 adb 服务器通信。

  然后，服务器会与所有正在运行的设备建立连接。它通过扫描 5555 到 5585 之间（该范围供前 16模拟器使用）的奇数号端口查找模拟器。服务器一旦发现 adb 守护进程(adbd)，便会与相应的端口建立连接。请注意，每个模拟器都使用一对按顺序排列的端口 – 用于控制台连接的偶数号端口和用于 adb连接的奇数号端口。例如：模拟器 1，控制台：5554 模拟器 1，adb：5555 模拟器 2，控制台：5556 模拟器 2，adb：5557 依此类推如上所示，在端口 5555 处与 adb 连接的模拟器与控制台监听端口为 5554 的模拟器是同一个。服务器与所有设备均建立连接后，您便可以使用 adb 命令访问这些设备。由于服务器管理与设备的连接，并处理来自多个 adb客户端的命令，因此您可以从任意客户端（或从某个脚本）控制任意设备。

  ### 3、Monkey指令

  Android工具，运行在模拟器或实际设备中，被测应用发送伪随机事件流（如按键、触屏、手势等），过 monkey 用随机重复的方式来对应用程序进行一些稳定性、健壮性方面的测试，利用 socket 通讯（Android 客户端和服务器以 TCP/UDP 方式）使用的事件流数据流是随机的，不能自定义

  ## 二、使用说明（重点，遇到XXX情况咋处理）

  1. ### 云手机平台上安装指定软件方法

  #### 1）采编app

  输入app名称，设置资源权限（默认向子分组开放），提交一个apk文件，上传后会进行解析，解析成功后，app会被采编到后台。
   ![图形用户界面, 文本, 应用程序  描述已自动生成](file:///C:/Users/lenovo/AppData/Local/Temp/msohtmlclip1/01/clip_image004.jpg)

  #### 2）安装或更新

  可以根据云机数量和指定云集编号进行安装或更新，操作类型有推送并安装和仅推送两种。

  1. 推送和安装：将apk推送到云机上，并且执行安装任务;
  2. 仅推送：只是将apk推送到云机上，不执行安装任务。再次执行"推送和安装"，就可以直接安装，跳过推送过程。例如客户想批量更新某个app，但是白天直接更新会影响客户使用，那么可以在白天使用仅推送，先把app文件拷贝过去，到了晚上低峰期，再执行推送和安装，这时候由于没有了推送文件的过程，就可以迅速完成更新

  ![图形用户界面, 文本, 应用程序  描述已自动生成](file:///C:/Users/lenovo/AppData/Local/Temp/msohtmlclip1/01/clip_image006.jpg)
   **注意**：

  1. 填写数量必填，绑定云机编号非必填，云机编号范围一行一个；
  2. 如果填写数量小于可操作云机数，且绑定云机编号范围为空，在可操作云机中随机抽取填写数量的云机进行操作；
  3. 点击确认操作后，可以在系统管理-任务-子任务管理里查看实施的结果和对应的云机编号等信息；
  4. 应用安装量为五分钟一次定时刷新，如果需要实时更新安装量，请前往云机菜单对云机进行巡检。

  #### 3）上传脚本文件

  ![图形用户界面, 文本, 应用程序  描述已自动生成](file:///C:/Users/lenovo/AppData/Local/Temp/msohtmlclip1/01/clip_image008.gif)

  选择云机列表，更多操作，点击上传到云机

  ![图形用户界面, 文本, 应用程序  描述已自动生成](file:///C:/Users/lenovo/AppData/Local/Temp/msohtmlclip1/01/clip_image010.gif)

  保存在/sdcard中。

  2. ### 程序中设置目标软件，修改位置

  #### 1）查看上传应用包名

  ![img](file:///C:/Users/lenovo/AppData/Local/Temp/msohtmlclip1/01/clip_image011.gif)![图形用户界面, 应用程序  描述已自动生成](file:///C:/Users/lenovo/AppData/Local/Temp/msohtmlclip1/01/clip_image013.gif)

  #### 2）将上传应用包名存入package.yaml中

  ![图形用户界面, 文本, 应用程序  描述已自动生成](file:///C:/Users/lenovo/AppData/Local/Temp/msohtmlclip1/01/clip_image015.gif![image-20240320165112625](C:\Users\lenovo\AppData\Roaming\Typora\typora-user-images\image-20240320165112625.png)

  3. ### 设置文件存储位置

  #### 1）存储在本地

  打开PCAPdroid，选择转储模式

  ![img](file:///C:/Users/lenovo/AppData/Local/Temp/msohtmlclip1/01/clip_image016.gif)![文本  描述已自动生成](file:///C:/Users/lenovo/AppData/Local/Temp/msohtmlclip1/01/clip_image018.gif)

  #### 2）远程服务器接收

  ![img](file:///C:/Users/lenovo/AppData/Local/Temp/msohtmlclip1/01/clip_image019.gif)![文本  描述已自动生成](file:///C:/Users/lenovo/AppData/Local/Temp/msohtmlclip1/01/clip_image020.gif)

  设置服务器IP-端口

  ![img](file:///C:/Users/lenovo/AppData/Local/Temp/msohtmlclip1/01/clip_image021.gif)![图形用户界面, 文本, 应用程序, 电子邮件  描述已自动生成](file:///C:/Users/lenovo/AppData/Local/Temp/msohtmlclip1/01/clip_image023.gif)

  远程服务器启动udp_receiver.py python 脚本，PCAPdroid 将 PCAP 记录封装到 UDP 流中，并将流发送到远程 UDP 收集器。udp_receiver.py脚本将在指定端口上接收 UDP 数据包，对其进行解封装，并将原始 PCAP 记录打印到 stdout。通过将其输送到网络监控程序中，可以实时分析捕获的数据包。

  4. ### adb 命令，连接

  1）确认要映射的本地端口，以下以8011为例(如果有多台云机，可以指定本地的多个端口)

  2）确认本地8011端口没有在使用。(为了确保本地端口未在使用，可以先执行一次最后一步清理的命令，执行后，会确保本地端口处于可用状态)

  3）确定云机目前在线状态正常

  4）确定云机adb进程已启动(可以在云机上执行一次start adbd，确保adb进程以启动。注意云机重启后，需要重新执行一次。如果要确保云机重启后adb自启，可以联系PMO更新镜像)

  5）确认目前没有其他人在使用云机进行ADB连接，否则连接会失败，这一步只能人工确定，或者重启一次云机可以关闭之前的adb连接

  6）输入ssh连接命令以及对应连结秘钥开始建立连接，密码输入完成后，如果是windows系统，命令界面会卡住，需要重新打开一个命令行界面进行连接。如果是mac linux，可以直接进行下一步连接操作，此时，本地的8011端口，已经映射到云手机上的adb，输入adb连接命令：如：adb connect 127.0.0.1:8011

  5. ### 等待自动采集

  ### 1）运行程序等待自动采集

  6. ### 可在云手机平台页面看到采集过程

  常见问题：

  1. 设置了appium连接后长时间无法开始自动化采集：重新连接。

  2. Adb连接失败：

  netstat -ano | findstr “5037”查看5037端口占用情况

  ![img](file:///C:/Users/lenovo/AppData/Local/Temp/msohtmlclip1/01/clip_image025.gif)

  执行 taskkill -f -pid XXX 以杀死占据了5037端口的进程

  ![文本  描述已自动生成](file:///C:/Users/lenovo/AppData/Local/Temp/msohtmlclip1/01/clip_image027.gif)

  重新连接

  3. Appium报错：重启云手机和并执行步骤 4

  4. 采集过程中云手机页面在自动旋转：云手机平台问题，可不予处理。

  5. 采集过程中云手机卡住：云手机平台问题，可不予处理。
