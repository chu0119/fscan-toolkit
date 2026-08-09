# Fscan Command Builder — Design Spec

**Date**: 2026-08-10
**Status**: Ready for implementation

## Overview

A single HTML file (`fscan-command-builder.html`) that serves as an interactive GUI for building command lines for fscan, fscan-web, and pscan. Zero dependencies, opens directly in any browser.

## Architecture

```
┌──────────────────────────────────────────────────────┐
│  #header                                            │
│  [fscan ▾] [加载预设 ▾] [保存预设] [历史记录 ▾]      │
│  工具选择器  预设管理              历史(最近20条)   │
├────────────┬─────────────────────────────────────────┤
│  #sidebar  │  #main                                  │
│  快速导航: │  ┌─ 目标设置 ──────────────────┐       │
│  ·目标     │  │ 目标IP/CIDR: [__________]    │       │
│  ·端口     │  │ 主机文件:    [__________] [浏]│       │
│  ·扫描控制 │  │ 排除主机:    [__________]     │       │
│  ·凭据     │  └──────────────────────────────┘       │
│  ·Web扫描  │  ┌─ 端口控制 ──────────────────┐       │
│  ·漏洞利用 │  │ 端口: [_______________]       │       │
│  ·后渗透   │  │ 端口文件: [__________] [浏]   │       │
│  ·代理     │  │ 排除端口: [__________]        │       │
│  ·输出     │  └──────────────────────────────┘       │
│            │  ┌─ ... ────────────────────────┐       │
│            │  ... (7 more collapsible panels) │       │
│            │  └──────────────────────────────┘       │
├────────────┴─────────────────────────────────────────┤
│  #footer                                             │
│  ┌──────────────────────────────────────────────────┐│
│  │ fscan.exe -h 192.168.1.0/24 -p 80,443 -nobr      ││
│  └──────────────────────────────────────────────────┘│
│  [📋 复制命令]  [▶ 运行]  [⚑ 保存配置]              │
└──────────────────────────────────────────────────────┘
```

## Core Modules

### 1. Parameter Definition Database (`paramDefs`)

A single JavaScript object defining every parameter with categories and metadata. Each parameter has:

```js
{
  id: 'target',            // Logical ID (same across tools)
  category: 'target',      // Which accordion panel
  label: '目标主机',        // Display label (Chinese)
  hint: 'IP、CIDR网段、域名', // Tooltip
  type: 'text',            // text | toggle | select | combo | file-picker | port-list | multitext
  fscan: '-h',             // Flag in fscan
  pscan: '-t',             // Flag in pscan
  web: false,              // Shown in fscan-web mode?
  default: '',             // Default value
  dependsOn: null,         // Show only when (e.g. {toggle: 'nobr', value: false})
  group: null,             // For grouping related fields
}
```

All ~75 parameters defined this way. The form auto-generates from this database.

### 2. Tool-Switching Engine

When the user switches tool (fscan ↔ pscan ↔ fscan-web):
- Re-read all form field values
- Regenerate the command string using the target tool's flag names
- Form labels and layout stay the same (logical IDs are stable)
- fscan-web mode collapses to just 2 fields (port + lang)

### 3. Conditional Show/Hide

- **Global toggles** (checkboxes) gate entire panels:
  - `-ao` (仅存活) → hides panels: port, cred, web, exploit, post-exploit, output format
  - `-nobr` (禁用爆破) → hides panels: cred
  - `-nopoc` → hides panels: web (POC-related fields only)
  - `-np` (跳过存活) → hides: nothing (but adds the flag)
- **Mode switching** (fscan only → selectable modes like `ssh`, `mysql`, etc.) shows relevant cred fields for that service.
- **Redis exploit** fields (rwp/rwc/rwf/rs) show only when Redis mode or Redis-related ports are targeted.

### 4. Command Generator

Reads all visible, non-empty form fields. Constructs command in the format:
```
.\fscan_2.2.0_windows_x64.exe -h <target> [flags in category order] [-o <output>]
```

Key rules:
- Booleans (toggles): only emit the flag if true
- Strings: omit if empty/default
- Ordered output: target → ports → mode → control → cred → toggles → web → exploit → local → proxy → output
- pscan: use obfuscated flag names from the mapping table
- fscan-web: `.\fscan-web_2.2.0_windows_x64.exe -port <n> -lang <zh/en>`

### 5. History System

- Store last 20 commands in `localStorage` (key: `fscan-cmd-history`)
- Each entry: `{tool, command, timestamp, label}`
- UI: dropdown with timestamps, click to restore
- Auto-save on every "copy" action

### 6. Preset System

- Save: serialize all form values + tool selection to JSON, prompt for name, store in `localStorage`
- Load: dropdown of saved presets, restore all form values and tool selection
- Delete: option in the dropdown

### 7. Copy & Run

- **Copy**: `navigator.clipboard.writeText(command)` + visual feedback ("已复制!")
- **Run** (bonus): Opens a modal showing how to run it, with the command pre-filled. Since browsers can't execute local exe files directly, show: "请在 PowerShell 中粘贴运行" with a one-click copy.

## Styling

- Dark theme (match security tool aesthetics)
- Color scheme: deep navy background, cyan accents, red for danger toggles
- Responsive: works on 1920px desktop, minimum width ~900px
- Accordion panels with smooth expand/collapse animation
- Monospace font for command preview
- CSS custom properties for easy theming

## File Structure

Single file: `D:\fscan\fscan-command-builder.html`

Sections (in order):
1. `<!DOCTYPE html>` → metadata
2. `<style>` → all CSS (embedded)
3. `<body>` → minimal HTML skeleton
4. `<script>` → all JS:
   - Parameter definitions
   - Rendering engine (generates DOM from defs)
   - Event handlers (tool switch, toggle, input change)
   - Command builder
   - History manager
   - Preset manager
   - Clipboard + copy logic

## Parameter Categories (Accordion Panels)

1. **目标设置** — target, hostFile, excludeHosts, excludeHostFile
2. **端口控制** — ports, portFile, excludePorts
3. **扫描控制** — mode, threads, timeout, webTimeout, globalTimeout, rate, maxPackets, icmpRate, pocConcurrency, retries
4. **功能开关** — skipPing, skipTCP, skipSubnet, noBrute, noPOC, noRedis, fullPOC, aliveOnly, silent, nocolor, nopg
5. **凭据与爆破** — username, password, extraUsers, extraPasswords, userFile, passFile, userPassFile, domain, hash, hashFile, sshKey
6. **Web 扫描** — url, urlFile, cookie, userAgent, pocName, pocPath, dns
7. **漏洞利用** — redisFile, redisShell, redisWritePath, redisWriteContent, redisWriteFile, shellcode, reverseShell, forwardShellPort
8. **后渗透** — localPlugin, persistenceFile, winPE, downloadUrl, downloadPath, keylogOutput, startSocks5
9. **代理与网络** — proxy, socks5, iface
10. **输出设置** — outputFile, outputFormat, noSave, lang, debug, perf, log

## Self-Review

- No TODOs or placeholders
- All 75 parameters covered via the fscan ↔ pscan mapping table
- Name collision gotchas handled (fscan -hf vs pscan -hf, etc.)
- fscan-web treated separately (2 fields only)
- localStorage for persistence, no server needed
