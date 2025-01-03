面向多终端控制系统的安全，团队开发了分布式客户端病毒检测系统，对客户端的文件进行病毒检测，客户端的检测与安全防护由服务端控制，包括：病毒库升级、病毒库删除、配置修改、主动查杀、定时查杀，实现多样化查杀。

分布式病毒查杀，相对于单设备病毒防御软件能够从服务器更直观监控客户端的数据安全，同时保证客户端到服务端的数据传输安全。系统总体低耦合，ClamAV引擎查杀被封装成函数，能够使用其他查杀方式。
