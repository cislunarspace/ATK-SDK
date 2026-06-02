# 引言

在近期的一次卫星轨道机动仿真任务中，我需要为多颗卫星配置轨道机动参数。手动逐一设置过程繁琐且效率低下。为此，我将此前编写的二次开发代码进行了重构，整理出一个通用的 ATK 二次开发类。在开发过程中，我结合使用了自行编写的 Java 二次开发服务与 Python 二次开发包。

## 环境准备

### Windows

在运行本演示程序前，请完成以下准备工作：

1. **安装并注册 ATK**  
   请确保已正确安装并激活 ATK。具体操作可参考我制作的视频教程：  
   【ATK 安装及注册教程】 https://www.bilibili.com/video/BV1tKeazMENG/?share_source=copy_web&vd_source=bdc7e9e76a85f0e5e181fcb11ea574cb

2. **配置 Java 环境**  
   安装 Java 21 SDK，并根据你的系统环境修改 `java service` 文件夹下的 `start.bat` 文件。

3. **启动 Java 二次开发服务**  
   运行 `start.bat` 启动 Java 服务。启动成功后的界面如下所示：  
   ![alt text](figures/Java二次开发服务界面.png)

4. **安装 Python 环境**  
   请安装合适的 Python 版本（建议自行测试兼容性）。  
   我在开发时使用的是 Python 3.13.5。

5. **配置 ATK 路径**  
   在 `funcs.py` 文件中，设置你本地 `ATK.exe` 的完整路径：  
   ![alt text](figures/配置好ATK的启动地址.png)

6. **运行主程序**  
   执行 `Main.py`，程序运行后将自动调用 ATK。以下是 ATK 软件界面及控制台输出的截图：  
   ![alt text](figures/ATK运行截图.png)  
   ![alt text](figures/Console结果.png)

### Ubuntu

本仓库已在以下环境验证通过：

- Ubuntu 24.04.4 LTS
- OpenJDK 21
- Python 3.12
- ATK 4.0.0 Linux 版，安装目录为 `/opt/ATK/ATK-4.0.0`
- NVIDIA 驱动 595.71.05，OpenGL 4.6

Ubuntu 下不要直接用原始 `ATK.sh` 启动本 SDK 示例。仓库提供了 `launch_atk_ubuntu.sh`，用于补充 ATK Connect 端口参数并修复常见的 `libGL` / OpenGL 加载问题。

#### 1. 安装依赖

```bash
sudo apt update
sudo apt install openjdk-21-jdk python3 python3-requests \
  libgl1 libglx-mesa0 libgl1-mesa-dri mesa-utils libglu1-mesa \
  libegl1 libopengl0 libx11-6 libxcb1 libxcb-glx0 libxcb-dri2-0 \
  libxcb-dri3-0 libxcb-present0 libxcb-sync1 libxshmfence1 libdrm2
```

如果使用 NVIDIA 显卡，建议先确认驱动可用：

```bash
nvidia-smi
ldconfig -p | grep -E 'libGLX_nvidia|libnvidia-gl'
```

#### 2. 启动 ATK

```bash
cd /home/ouyangjiahong/codes/ATK-SDK
./launch_atk_ubuntu.sh
```

该脚本默认执行：

- 使用 `/opt/ATK/ATK-4.0.0` 作为 ATK 安装目录；
- 设置 ATK Connect 端口为 `6655`；
- 优先使用 Ubuntu / 显卡驱动提供的系统 OpenGL 库；
- 保留 ATK 自带 Qt 和运行库路径；
- 设置 Qt XCB / OpenGL 相关环境变量；
- 启动前切换工作目录到 ATK 安装目录，避免 `data dir not found`。

可通过环境变量覆盖默认值：

```bash
ATK_HOME=/opt/ATK/ATK-4.0.0 ATK_PORT=6655 ./launch_atk_ubuntu.sh
```

如果硬件 OpenGL 仍然不可用，可以尝试软件渲染：

```bash
ATK_SOFTWARE_GL=1 ./launch_atk_ubuntu.sh
```

如需诊断 Qt 插件或 OpenGL 加载问题：

```bash
ATK_DEBUG_GL=1 ./launch_atk_ubuntu.sh
```

确认 ATK Connect 端口已监听：

```bash
ss -ltnp | grep ':6655\b'
```

#### 3. 启动 Java 二次开发服务

另开一个终端：

```bash
cd /home/ouyangjiahong/codes/ATK-SDK
bash "java service/start.sh"
```

确认 HTTP 服务端口已监听：

```bash
ss -ltnp | grep ':8080\b'
```

如果提示 `地址已在使用`，说明已有 Java 服务占用 `8080`，可先停止旧进程：

```bash
pkill -f atk_python_sdk_service.jar
```

#### 4. 运行 Python 示例

另开一个终端：

```bash
cd /home/ouyangjiahong/codes/ATK-SDK
python3 Main.py
```

成功时可看到类似输出：

```text
ATK 连接成功！
新场景 'AccessCalApp' 创建成功
初始化完成，卫星 ID: 48200
```

## 复现 atk-doc 二次开发案例

本仓库的 `examples/` 目录复现了 `~/codes/atk-doc/02-案例教程/8-二次开发案例` 中的 Connect 模式案例。Ubuntu 下推荐使用 `run_atk_example_ubuntu.sh` 统一运行案例：它会自动检查 ATK 端口、启动缺失的 ATK 进程，并在每次运行前重启 Java 二次开发服务以清理旧连接状态，用户无需手动处理 Java 服务与 ATK 之间的 socket 状态。

列出可运行案例：

```bash
cd /home/ouyangjiahong/codes/ATK-SDK
./run_atk_example_ubuntu.sh --list
```

运行轻量案例：

```bash
./run_atk_example_ubuntu.sh simple --no-save
./run_atk_example_ubuntu.sh access --no-save
./run_atk_example_ubuntu.sh coverage --no-save
./run_atk_example_ubuntu.sh huge_constellation --no-save
```

案例执行完成后 ATK 会保持打开，便于继续查看场景或复现下一个案例。

如需直接调用底层 Python 入口，也可以使用：

```bash
python3 examples/run_example.py --list
python3 examples/run_example.py simple --no-save
```

常用参数：

- `--no-save`：跳过文档脚本中的 `Save` 命令；
- `--close`：案例运行后关闭 Java 服务与 ATK 的 Connect 连接；
- `--keep-going`：遇到 `NACK` / `onError` 后继续执行后续命令，并在控制台报告失败。

Astrogator、RPO、接近分析等长案例命令较多，运行时间更长，且可能依赖 ATK 对应功能模块授权。如出现 `NACK`，请根据控制台输出的失败命令对照源文档排查。

## Ubuntu 故障排查

### `libGL` / OpenGL 错误

如果直接运行 ATK 原始脚本时出现：

```text
libGL error: image driver extension not found
libGL error: failed to load driver: nouveau
libGL error: failed to load driver: swrast
Unrecognized OpenGL version
```

请使用本仓库的：

```bash
./launch_atk_ubuntu.sh
```

该脚本会优先使用系统 OpenGL / GLVND 库，避免 ATK 自带旧 `libGL.so.1` 与当前系统驱动不匹配。

### 端口冲突

Java 服务默认使用 `8080`，ATK Connect 默认使用 `6655`。如果端口被占用，可检查：

```bash
ss -ltnp | grep -E ':(6655|8080)\b'
```

停止相关进程：

```bash
pkill -f atk_python_sdk_service.jar
pkill -f '/opt/ATK/ATK-4.0.0/ATK'
```

### ATK 安装目录不同

如果 ATK 不在 `/opt/ATK/ATK-4.0.0`，运行前设置：

```bash
export ATK_HOME=/path/to/ATK-4.0.0
export ATK_EXECUTABLE=/home/ouyangjiahong/codes/ATK-SDK/launch_atk_ubuntu.sh
```

`funcs.py` 默认会通过 `ATK_EXECUTABLE` 查找启动器；未设置时使用仓库内的 `launch_atk_ubuntu.sh`。

# 注意事项

如有任何疑问，欢迎通过邮箱联系我：ouyangjiahong22@nudt.edu.cn
