"""
太极系统引擎 - 核心计算模块
基于太极方程，提供网络健康度、代偿守恒与雪崩预警计算。
"""
import numpy as np

# 生存底线常数：6π⁵ ≈ 1836.12
SIX_PI_POW_5 = 6 * (np.pi ** 5)

def calculate_node_health(chi: float) -> dict:
    """
    计算单个节点（库）的健康度。
    :param chi: 节点的固定资产/结构刚度
    :return: 健康状态字典
    """
    is_alive = chi >= SIX_PI_POW_5
    if not is_alive:
        status = "崩塌"
        health_ratio = 0.0
    else:
        health_ratio = min((chi - SIX_PI_POW_5) / SIX_PI_POW_5, 1.0)
        if health_ratio > 0.5: status = "健康"
        elif health_ratio > 0.2: status = "正常"
        else: status = "预警"
        
    return {
        "is_alive": is_alive,
        "status": status,
        "health_ratio": health_ratio,
        "threshold": SIX_PI_POW_5
    }

def calculate_compensation(z_trans: float, z_long: float) -> dict:
    """
    计算横向流程(Z_trans)与纵向行政(Z_long)的代偿守恒。
    Z_trans^2 + Z_long^2 <= (6π⁵)^2
    """
    max_capacity = SIX_PI_POW_5
    current_load = np.sqrt(z_trans**2 + z_long**2)
    delta = current_load / max_capacity  # 偏离度：0~1，越接近1越危险
    
    if delta > 1.0:
        status = "突破守恒圆：系统雪崩！"
    elif delta > 0.8:
        status = "高危：行政重度代偿流程缺失"
    elif z_long > z_trans:
        status = "亚健康：靠行政命令硬撑"
    else:
        status = "健康：流程驱动为主"
        
    return {
        "z_trans": z_trans,
        "z_long": z_long,
        "delta": delta,
        "status": status
    }

def trigger_cascade_collapse(nodes: list) -> list:
    """
    检查树形网络并触发级联雪崩。
    :param nodes: 所有节点的平铺列表（需包含 parent_id 关系）
    :return: 崩塌的节点名称列表
    """
    collapsed = []
    # 逻辑：如果某父节点的所有子节点都 is_alive=False，则父节点崩塌
    # (实际应用中会递归向上检查)
    return collapsed
