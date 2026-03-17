# 汐语 OS (XiYu OS) - 融合 Minecraft 深度集成的 Web 模拟操作系统

![XiYu OS](https://img.shields.io/badge/XiYu_OS-v7.0.7-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

汐语 OS 是一款基于 Web 技术开发的模拟操作系统，拥有精美的 Windows 11 风格界面和深度的 Minecraft 游戏状态同步功能（含专用 Fabric Mod）。它不仅是一个美观的网页桌面，更是 Minecraft 玩家的管理中心。

## ✨ 核心特性

- **🖥️ 极致视觉体验**：采用 Windows 11 设计语言，支持玻璃拟态（Glassmorphism）、毛玻璃效果及平滑的微动画。
- **🎮 Minecraft 深度集成**：
    - **云端同步**：通过专用 Fabric Mod 实时同步飞行时长、计分板和游戏状态。
    - **互动中心**：内置联机中心，支持远程发送服务器指令及实时性能监控（TPS/内存）。
    - **玩家市场**：完整的玩家交易市场与商店系统。
- **📦 独立可执行程序**：支持通过 PyInstaller 打包为单体 EXE，无需 Python 环境即可运行。
- **💎 完善的会员体系**：集成云盘存储升级、每日奖励领取及 VIP 权益展示。
- **🛠️ OOBE 开箱体验**：内置安装引导程序，支持地区选择、管理员账号创建等流程。

## 🚀 技术栈

- **前端**：Vanilla HTML/CSS/JavaScript, Font Awesome, Google Fonts
- **后端**：Python / Flask
- **数据库**：SQLite3
- **游戏端**：Minecraft Fabric 1.21.1 (Java)
- **打包工具**：PyInstaller

## 🛠️ 快速开始

### 方式一：直接运行 EXE (推荐)
1. 前往 [Releases](https://github.com/zza52/xiyu-os/releases) 下载最新版的 `XiYuOS.exe`。
2. 双击运行，程序会自动在同级目录生成数据库及上传文件夹。
3. 浏览器访问 `http://127.0.0.1:5000` 即可。

### 方式二：开发者模式 (Python)
1. 克隆仓库：
   ```bash
   git clone https://github.com/zza52/xiyu-os.git
   cd xiyu-os
   ```
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行应用：
   ```bash
   python app.py
   ```

## 📂 项目结构

- `app.py`: Flask 后端逻辑
- `templates/`: 网页模板
- `static/`: 静态资源（CSS, JS, 图像）

---

## 🤝 贡献

欢迎提交 Issue 或 Pull Request！

## 📄 许可证

本项目基于 [MIT](LICENSE) 协议开源。

# XiYu OS - A Web-Based Simulated Operating System with Deep Minecraft Integration

![XiYu OS](https://img.shields.io/badge/XiYu_OS-v7.0.7-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

XiYu OS is a simulated operating system built with Web technologies. It features an exquisite Windows 11-style interface and deep Minecraft game state synchronization (including a dedicated Fabric Mod). It is not just an aesthetically pleasing web desktop, but also a comprehensive management center for Minecraft players.

## ✨ Core Features

- **🖥️ Ultimate Visual Experience**: Adopts the Windows 11 design language, supporting glassmorphism, frosted glass effects, and smooth micro-animations.
- **🎮 Deep Minecraft Integration**:
    - **Cloud Sync**: Real-time synchronization of elytra flight time, scoreboards, and game states via a dedicated Fabric Mod.
    - **Interactive Center**: Built-in multiplayer hub supporting remote server commands and real-time performance monitoring (TPS/Memory).
    - **Player Market**: A complete player trading market and store system.
- **📦 Standalone Executable**: Can be packaged into a single EXE file using PyInstaller, allowing it to run without a Python environment.
- **💎 Comprehensive Membership System**: Integrated cloud drive storage upgrades, daily reward claims, and VIP perk displays.
- **🛠️ OOBE (Out-of-Box Experience)**: Built-in setup wizard supporting region selection, administrator account creation, and more.

## 🚀 Tech Stack

- **Frontend**: Vanilla HTML/CSS/JavaScript, Font Awesome, Google Fonts
- **Backend**: Python / Flask
- **Database**: SQLite3
- **Game Client**: Minecraft Fabric 1.21.1 (Java)
- **Packaging Tool**: PyInstaller

## 🛠️ Quick Start

### Method 1: Run the EXE directly (Recommended)
1. Go to [Releases](https://github.com/zza52/xiyu-os/releases) to download the latest `XiYuOS.exe`.
2. Double-click to run. The program will automatically generate the database and upload folders in the same directory.
3. Access `http://127.0.0.1:5000` in your web browser.

### Method 2: Developer Mode (Python)
1. Clone the repository:
   ```bash
   git clone https://github.com/zza52/xiyu-os.git
   cd xiyu-os
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```

## 📂 Project Structure

- `app.py`: Flask backend logic
- `templates/`: HTML templates
- `static/`: Static resources (CSS, JS, Images)

---

## 🤝 Contributing

Issues and Pull Requests are always welcome!

## 📄 License

This project is open-sourced under the [MIT](LICENSE) License.
