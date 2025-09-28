import os
import subprocess
import time  # 用于 time.sleep()
from datetime import timedelta, datetime
from typing import Dict, Any, List, Optional, Set

from atk_python_sdk import atkOpen, atkConnect


class ATKScenario:
    """ATK 场景管理类，用于创建和配置卫星、地面站、传感器，并计算可见性。"""

    # 常量定义
    BASE_URL = "http://localhost:8080"
    UTC_OFFSET_HOURS = 8  # 中国标准时间 UTC+8
    ATK_EXE_PATH = r"D:\Program Files (x86)\ATK\ATK-0826\ATK.exe"

    def __init__(self) -> None:
        """
        初始化 ATKScenario 实例。
        """
        # 场景时间
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

        # 设施与传感器
        self.facilities: Dict[str, Dict[str, Any]] = {}  # 地面站信息
        self.sensors: Dict[str, Dict[str, Any]] = {}     # 传感器信息

        # 卫星与访问数据
        self.caldata: Dict[int, Dict[str, Any]] = {}     # 卫星计算数据

        # 自动配色计数器
        self.color_num: int = 0

    def connect_atk(self, base=None, host="127.0.0.1", port=6655):
        """
        连接 ATK 服务，若未运行则尝试启动本地进程。
        """
        if base is None:
            base = self.BASE_URL

        try:
            atkOpen(base, host, port, 1)
            print("ATK 连接成功！")
            return True
        except Exception as e1:
            print(f"未检测到 ATK 进程：{e1}")
            print("正在启动 ATK 进程...")

            try:
                if not os.path.exists(self.ATK_EXE_PATH):
                    raise FileNotFoundError(f"ATK.exe 未找到: {self.ATK_EXE_PATH}")

                subprocess.Popen([self.ATK_EXE_PATH], cwd=os.path.dirname(self.ATK_EXE_PATH))
                print("ATK 进程已启动，等待 8 秒初始化...")
                time.sleep(8)

                atkOpen(base, host, port, 1)
                print("ATK 连接成功！")
                return True
            except Exception as e2:
                print(f"启动或连接 ATK 失败: {e2}")
                return False

    def create_new_scenario(self, scenario_name="DefaultScenario", base=None):
        """
        在已连接的 ATK 中创建新场景。
        """
        if ' ' in scenario_name:
            print(f"场景名称不合法，名称中不能包含“空格”！")
            return False

        if base is None:
            base = self.BASE_URL

        try:
            atkConnect(base, 'New', f'/ Scenario {scenario_name}')
            print(f"新场景 '{scenario_name}' 创建成功")
            return True
        except Exception as e:
            print(f"创建场景失败: {e}")
            return False

    def set_scenario_time_atk(self, start: datetime, end: datetime) -> None:
        """
        设置 ATK 场景的分析时间范围（自动转换为 UTC）。

        Parameters
        ----------
        start : datetime
            场景开始时间（本地时间，如北京时间）
        end : datetime
            场景结束时间（本地时间）
        """
        # 转换为 UTC（ATK 使用 UTC）
        start_utc = start - timedelta(hours=self.UTC_OFFSET_HOURS)
        end_utc = end - timedelta(hours=self.UTC_OFFSET_HOURS)

        # 移除微秒，格式化为 ATK 要求的字符串
        start_utc = start_utc.replace(microsecond=0)
        end_utc = end_utc.replace(microsecond=0)

        # 英文月份缩写（避免 locale 影响）
        MONTHS = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        s_str = f'{start_utc.day} {MONTHS[start_utc.month]} {start_utc.year} {start_utc.strftime("%H:%M:%S")}.000'
        e_str = f'{end_utc.day} {MONTHS[end_utc.month]} {end_utc.year} {end_utc.strftime("%H:%M:%S")}.000'

        arg = f'* "{s_str}" "{e_str}"'
        atkConnect(self.BASE_URL, "SetAnalysisTimePeriod", arg)
        atkConnect(self.BASE_URL, "Animate", "* Reset")

    def create_facility_atk(self, name: str, lat: float, lon: float, height: float = 0.0) -> None:
        """
        在 ATK 中创建地面站设施。

        Parameters
        ----------
        name : str
            地面站名称
        lat : float
            纬度（度）
        lon : float
            经度（度）
        height : float, optional
            高度（米），默认为 0.0
        """
        base = self.BASE_URL
        atkConnect(base, "New", f"/ Facility {name}")
        atkConnect(base, "SetPosition", f"*/Facility/{name} Geodetic {lat} {lon} {height}")
        atkConnect(base, "Graphics", f"*/Facility/{name} SetColor {self.color_num}")
        self.color_num += 1
        atkConnect(base, "Animate", "* Reset")

        self.facilities[name] = {
            "path": f"*/Facility/{name}",
            "params": {"name": name, "lat": lat, "lon": lon, "height": height}
        }

    def create_sensor_atk(self, facility_name: str, **params) -> None:
        """
        在指定地面站上创建传感器。

        Parameters
        ----------
        facility_name : str
            所属地面站名称
        **params : dict
            必须包含：name, el_start, el_end, az_start, az_end, min_range, max_range
        """
        sensor_name = params["name"]
        base = self.BASE_URL
        sensor_path = f"*/Facility/{facility_name}/Sensor/{sensor_name}"

        atkConnect(base, "New", f"/ {sensor_path}")
        atkConnect(base, "Point", f"{sensor_path} Fixed Euler 121 180 0 0")
        atkConnect(
            base, "Define",
            f"{sensor_path} Conical {90.0 - params['el_end']} {90.0 - params['el_start']} "
            f"{params['az_start']} {params['az_end']}"
        )
        atkConnect(
            base, "SetConstraint",
            f"{sensor_path} Range Min {params['min_range']} Max {params['max_range'] * 1000}"
        )
        atkConnect(base, "Graphics", f"{sensor_path} SetColor {self.color_num}")
        self.color_num += 1
        atkConnect(base, "Animate", "* Reset")

        self.sensors[sensor_name] = {
            "path": sensor_path,
            "access": set(),
            "params": params
        }

    def create_satellite_atk(self, tle: List[str]) -> int:
        """
        通过 TLE 创建卫星。

        Parameters
        ----------
        tle : List[str]
            标准三行 TLE 数据（[名称, 行1, 行2]）

        Returns
        -------
        int
            卫星 NORAD ID
        """
        sat_id = int(tle[1][2:7])
        base = self.BASE_URL
        sat_path = f"*/Satellite/{sat_id}"

        atkConnect(base, "New", f"/ {sat_path}")
        atkConnect(base, "SetState", f'{sat_path} TLE "{tle[1]}" "{tle[2]}"')
        atkConnect(base, "Graphics", f"{sat_path} SetColor {self.color_num}")
        self.color_num += 1
        atkConnect(base, "Animate", "* Reset")

        # 初始化 caldata 条目
        if sat_id not in self.caldata:
            self.caldata[sat_id] = {}
        self.caldata[sat_id].update({
            "path": sat_path,
            "access": {}
        })

        return sat_id

    def set_sensor_atk(self, sensor_name: str, **params) -> None:
        """
        更新已有传感器的参数。

        Parameters
        ----------
        sensor_name : str
            传感器名称
        **params : dict
            需包含 el_start, el_end, az_start, az_end, min_range, max_range
        """
        base = self.BASE_URL
        sensor_path = self.sensors[sensor_name]["path"]

        atkConnect(
            base, "Define",
            f"{sensor_path} Conical {90.0 - params['el_end']} {90.0 - params['el_start']} "
            f"{params['az_start']} {params['az_end']}"
        )
        atkConnect(
            base, "SetConstraint",
            f"{sensor_path} Range Min {params.get('min_range', 0) * 1000} "
            f"Max {params['max_range'] * 1000}"
        )

        # 更新内存中的参数
        self.sensors[sensor_name]["params"].update(params)