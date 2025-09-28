from datetime import datetime

from funcs import ATKScenario


def main():
    # 创建 ATK 场景管理实例
    atk = ATKScenario()

    # 1. 连接 ATK
    if not atk.connect_atk():
        print("无法连接 ATK，程序退出。")
        return

    # 2. 创建新场景（名称不能含空格）
    if not atk.create_new_scenario("AccessCalApp"):
        print("场景创建失败，程序退出。")
        return

    # 3. 设置场景时间范围（北京时间）
    start_time = datetime(2024, 6, 1, 8, 0, 0)   # 2024-06-01 08:00:00 (UTC+8)
    end_time = datetime(2024, 6, 2, 8, 0, 0)     # 2024-06-02 08:00:00 (UTC+8)
    atk.set_scenario_time_atk(start_time, end_time)

    # 4. 创建地面站
    atk.create_facility_atk("Beijing", 39.9042, 116.4074, 50.0)

    # 5. 创建传感器
    atk.create_sensor_atk(
        facility_name="Beijing",
        name="Sensor1",
        el_start=5.0,
        el_end=85.0,
        az_start=0.0,
        az_end=360.0,
        min_range=0.0,
        max_range=2000.0  # 单位：km
    )

    # 6. 添加卫星（示例 TLE）
    tle_example = [
        "STARLINK-1234",
        "1 48200U 21021BJ  24152.50000000  .00001234  00000-0  12345-4 0  9999",
        "2 48200  53.0000 120.0000 0001234  90.0000 270.0000 15.00000000123456"
    ]
    sat_id = atk.create_satellite_atk(tle_example)

    print(f"初始化完成，卫星 ID: {sat_id}")


if __name__ == "__main__":
    main()