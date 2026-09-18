<!---
# Copyright (C) 2019 Syncplay
# This file is licensed under the MIT license - http://opensource.org/licenses/MIT

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
-->

# Syncplay
![GitHub Actions build status](https://github.com/lssb/syncplay/workflows/Build/badge.svg)

Solution to synchronize video playback across multiple instances of mpv, VLC, MPC-HC, MPC-BE and mplayer2 over the Internet.

## Official website
https://syncplay.pl

## Download
https://syncplay.pl/download/

## This fork (lssb-strm)

This is a personal build of Syncplay 1.7.7 for watching **`.strm` libraries** (Emby / Jellyfin / NAS pointers) together. It does not replace upstream Syncplay; the official project remains at https://github.com/Syncplay/syncplay.

Related report: [Syncplay/syncplay#807](https://github.com/Syncplay/syncplay/issues/807).

### What changed

- **Shared playlist identity.** mpv treats `.strm` as a playlist and reports the inner HTTP URL as the current file. This build keeps the `.strm` filename as the room identity for 25 seconds after open, so two people can each play their own NAS URL while staying on the same playlist item.
- **Sidecar subtitles.** Syncplay starts mpv with a bundled `strm-sidecars.lua` (`--scripts-append`). Matching `.srt` / `.ass` files next to the `.strm` are loaded automatically. You do not need to change the mpv install.
- **Server.** No server change. A 1.7.7 server is fine.
- **About dialog.** Window title is `Syncplay v1.7.7 lssb-strm`. Help → About names **lssb** and **白小九日**.

### 本次修改（中文）

mpv 会把 `.strm` 展开成里面的 URL，Syncplay 会把它当成另一个文件，同名字幕也找不到。本 fork 做了两件事：房间里继续用 `.strm` 文件名（打开后 25 秒内完成绑定），启动 mpv 时带上内置脚本，从 `.strm` 所在目录加载同名字幕。服务端不用改。

Windows 64 位便携包请到本仓库 [Actions](https://github.com/lssb/syncplay/actions) 下载 `Syncplay_1.7.7_x64_Portable`（工作流名：Build，分支 `strm-identity`）。

## What does it do

Syncplay synchronises the position and play state of multiple media players so that the viewers can watch the same thing at the same time.
This means that when one person pauses/unpauses playback or seeks (jumps position) within their media player then this will be replicated across all media players connected to the same server and in the same 'room' (viewing session).
When a new person joins they will also be synchronised. Syncplay also includes text-based chat so you can discuss a video as you watch it (or you could use third-party Voice over IP software to talk over a video).

## What it doesn't do

Syncplay is not a file sharing service.

## License

This project, the Syncplay released binaries, and all the files included in this repository unless stated otherwise in the header of the file, are licensed under the [Apache License, version 2.0](https://www.apache.org/licenses/LICENSE-2.0.html). A copy of this license is included in the LICENSE file of this repository. Licenses and attribution notices for third-party media are set out in [third-party-notices.txt](syncplay/resources/third-party-notices.txt).

## Authors
* *Initial concept and core internals developer* - Uriziel.
* *GUI design and current lead developer* - Et0h.
* *Original SyncPlay code* - Tomasz Kowalczyk (Fluxid), who developed SyncPlay at https://github.com/fluxid/syncplay
* *Other contributors* - See http://syncplay.pl/about/development/
