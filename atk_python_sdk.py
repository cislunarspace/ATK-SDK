import time
from typing import List, Dict, Any, Tuple
import requests

# ============== 基础工具函数（统一 10ms 等待策略） ==============

def _post(base_url: str, path: str, payload: Dict[str, Any], timeout: float) -> requests.Response:
    """
    向指定 URL 发送 POST 请求（JSON 格式）

    内部工具函数，用于封装 HTTP 调用细节。自动拼接 base_url 与路径，发送 JSON 数据，
    并确保响应状态码为成功（2xx），否则抛出异常。

    :param base_url: ATK HTTP 服务的基础地址（如：http://localhost:8080）
    :param path: API 路径（如：/atk/open）
    :param payload: 要发送的 JSON 数据体
    :param timeout: 请求超时时间（秒）
    :return: 成功的 Response 对象
    :raises requests.HTTPError: 当响应状态码表示错误时
    """
    r = requests.post(f"{base_url.rstrip('/')}{path}", json=payload, timeout=timeout)
    r.raise_for_status()
    return r


def _detect_ok(events: List[str]) -> Tuple[bool, str]:
    """
    根据回调事件日志判断命令执行是否成功。

    Java 服务返回的 events 可能包含历史事件，因此按顺序取最后一个
    终态 ACK/NACK/code 作为本次判断依据。
    """
    last_status = None

    for line in events:
        for part in str(line).splitlines():
            if "onError" in part:
                last_status = ("NACK", "onError in callback")
                continue

            if "onReceivedEx" in part and "code=" in part:
                try:
                    num = int(part.split("code=", 1)[1].split(None, 1)[0].strip().rstrip(":,;"))
                    last_status = ("ACK", "") if num == 0 else ("NACK", f"onReceivedEx code={num}")
                except Exception:
                    pass
                continue

            if "NACK" in part:
                last_status = ("NACK", "NACK received")
                continue

            if "ACK" in part:
                last_status = ("ACK", "")

    if last_status is None:
        return True, ""

    return last_status[0] == "ACK", last_status[1]


# ============== 对外接口函数（简化参数，提升易用性） ==============

def atkOpen(base_url: str, host: str, port: int, timeout: float = 5.0) -> None:
    """
    建立与 ATK 服务的连接

    调用远程 /atk/open 接口，初始化与指定主机和端口的 TCP 连接。
    若连接失败或超时，将抛出异常。

    :param base_url: ATK 控制服务的基础 URL
    :param host: 目标 ATK 服务的 IP 或主机名
    :param port: 目标 ATK 服务的端口号
    :param timeout: HTTP 请求超时时间（秒），默认 5 秒
    :raises requests.RequestException: 若请求失败或响应状态异常
    """
    _post(base_url, "/atk/open", {"host": host, "port": port}, timeout)


def atkClose(base_url: str, timeout: float = 5.0) -> None:
    """
    关闭当前与 ATK 服务的连接

    调用远程 /atk/close 接口，释放已建立的连接资源。
    此操作是幂等的，即使未连接也可安全调用。

    :param base_url: ATK 控制服务的基础 URL
    :param timeout: HTTP 请求超时时间（秒），默认 5 秒
    :raises requests.RequestException: 若请求失败或响应状态异常
    """
    _post(base_url, "/atk/close", {}, timeout)


def atkConnect(
        base_url: str,
        command: str,
        cmdParam: str,
        wait_ms: int = 10,
        timeout_connect: float = 10.0,
) -> Dict[str, Any]:
    """
    向已连接的 ATK 服务发送一条控制命令并等待响应

    发送命令后等待设备响应，根据回调事件判断执行状态。
    返回结果仅包含 state（ACK/NACK）和预留的 result 字段。

    :param base_url: ATK 控制服务的基础 URL
    :param command: 要执行的命令类型（如 SET、GET 等）
    :param objPath: 命令作用的对象路径（如 /device/motor）
    :param cmdParam: 命令参数（可选）
    :param wait_ms: 等待设备响应的最大时间（毫秒），默认 10ms
    :param timeout_connect: 整个 HTTP 请求的超时时间（秒），默认 10 秒
    :param last_state: 上一条命令的执行结果，True 表示执行完毕，False 表示未执行完成
    :return: 字典，包含：
             - state: "ACK" 表示成功，"NACK" 表示失败
             - result: 空字符串，留待后续扩展（由 Java 侧决定内容）
    :raises requests.RequestException: 若网络请求失败（可选：也可捕获并转为 NACK）
    """
    payload = {
        "command": command or "",
        "cmdParam": cmdParam or "",
        "waitMs": int(wait_ms),
    }

    try:
        r = _post(base_url, "/atk/connect", payload, timeout_connect)
        data = r.json() if r.content else {}
        events = data.get("events", []) if isinstance(data, dict) else []
        success, reason = _detect_ok(events)  # 使用你的检测逻辑判断成功与否
        if success == False:
            print(reason)
            print(f"命令出现错误：{command} {cmdParam}")
    except Exception as e:
        events = [f"onError {e}"]

    return events
