# ATK Connect 二次开发案例

本目录复现 `~/codes/atk-doc/02-案例教程/8-二次开发案例` 中的 Connect 模式案例。

Ubuntu 下推荐使用仓库根目录的 `run_atk_example_ubuntu.sh` 统一运行案例。该脚本会自动检查 ATK 端口、启动缺失的 ATK 进程，并在每次运行前重启 Java 二次开发服务以清理旧连接状态，用户无需手动处理 Java 服务与 ATK 之间的 socket 状态。

## 列出案例

```bash
cd /home/ouyangjiahong/codes/ATK-SDK
./run_atk_example_ubuntu.sh --list
```

## 运行案例

轻量案例：

```bash
./run_atk_example_ubuntu.sh simple --no-save
./run_atk_example_ubuntu.sh access --no-save
./run_atk_example_ubuntu.sh coverage --no-save
./run_atk_example_ubuntu.sh huge_constellation --no-save
```

轨道转移 / Astrogator 案例：

```bash
./run_atk_example_ubuntu.sh hohmann_transfer --no-save
./run_atk_example_ubuntu.sh leo_to_geo_transfer --no-save
./run_atk_example_ubuntu.sh inclination_targeting --no-save
./run_atk_example_ubuntu.sh free_return_lunar_transfer --no-save
```

轨道转移案例命令较多，运行时间长于轻量案例，并依赖 ATK Astrogator 相关功能模块授权。调试长案例时，可使用 `--max-commands N` 只运行前 N 条命令来定位首个失败点，例如：

```bash
./run_atk_example_ubuntu.sh hohmann_transfer --no-save --max-commands 40
```

案例执行完成后 ATK 会保持打开，便于继续查看场景或复现下一个案例。

参数说明：

- `--no-save`：跳过文档中的 `Save` 命令。
- `--close`：案例运行后关闭 Java 服务与 ATK 的 Connect 连接。
- `--max-commands N`：只运行前 N 条命令，便于调试 Astrogator 等长案例。
- `--keep-going`：遇到 NACK / onError 后继续执行后续命令，并在控制台报告失败。

Astrogator、RPO 和接近分析案例命令较多，可能依赖 ATK 对应功能模块授权；如果出现 NACK，请根据控制台输出的失败命令对照源文档排查。

## 底层入口

如需调试，可以直接调用底层 Python 入口：

```bash
python3 examples/run_example.py --list
python3 examples/run_example.py simple --no-save
```
