import numpy as np

# 网络生存底线常数
SIX_PI_POW_5 = 6 * (np.pi ** 5)

def calculate_macro_energy(E_profit: float, alpha: float, d: float, chi: float, n: int) -> float:
    """
    网络传导方程求解器
    ΔE_macro(n, χ) = Σ (ΔE_profit^i - α * d / (1 + χ)) >= 6π^5
    
    参数:
        E_profit (float): 单个节点的横向应力利润 (ΔE_profit^i)
        alpha (float): 纵向抽税系数 (环境侵蚀强度)
        d (float): 相邻节点间的拓扑距离
        chi (float): 网络交联度
        n (int): 聚合度 (链条节点数)
        
    返回:
        float: 系统网络的总应力利润 ΔE_macro
    """
    tax_per_node = alpha * (d / (1.0 + chi))
    profit_per_node = E_profit - tax_per_node
    delta_E_macro = n * profit_per_node
    return delta_E_macro

def calculate_compensation_balance(z_trans: float, z_long: float) -> dict:
    """
    代偿势能监测仪: 计算 Z_trans 与 Z_long 占比及守恒状态
    Z_trans^2 + Z_long^2 <= (6π^5)^2
    
    参数:
        z_trans (float): 横向拔河应力
        z_long (float): 纵向代偿应力
        
    返回:
        dict: 包含总势能、占比、是否突破守恒律及溢出量
    """
    max_z_sq = SIX_PI_POW_5 ** 2
    total_z_sq = z_trans**2 + z_long**2
    total_z = np.sqrt(total_z_sq)
    
    z_trans_ratio = (z_trans**2 / total_z_sq) * 100.0 if total_z_sq > 0 else 0
    z_long_ratio = (z_long**2 / total_z_sq) * 100.0 if total_z_sq > 0 else 0
    
    is_balanced = total_z_sq <= max_z_sq
    overflow = max(0.0, total_z_sq - max_z_sq)
    
    return {
        "total_potential_energy": total_z,
        "z_trans_ratio": z_trans_ratio,
        "z_long_ratio": z_long_ratio,
        "is_balanced": is_balanced,
        "overflow": np.sqrt(overflow)  # 返回溢出的应力幅度
    }

def monitor_deviation_degree(delta: float) -> dict:
    """
    偏离度 Δ 预警模块
    根据系统偏离度评估系统状态并触发预警
    
    参数:
        delta (float): 系统偏离度 Δ ∈ (0, 1)
        
    返回:
        dict: 包含系统状态码、预警信息和全尺度周期拉伸率
    """
    if not (0 < delta < 1):
        raise ValueError("偏离度 Δ 必须在 (0, 1) 区间内")
        
    # T = T0 / (1 - Δ)，计算时间常数拉伸率
    time_dilation = 1.0 / (1.0 - delta)
    
    if delta >= 0.95:
        status = "CRITICAL_AVALANCHE"
        message = "系统逼近临界相变雪崩点，横向传导完全死锁，纵向代偿暴雷在即！"
    elif delta >= 0.8:
        status = "WARNING_STRESS"
        message = "系统网络死锁加剧，横向传导受阻，逼近64态饱和溢出！"
    elif delta >= 0.5:
        status = "SUB_HEALTH"
        message = "系统应力集中增加，建议疏通横向传导通道。"
    else:
        status = "NORMAL_STABLE"
        message = "系统高度有序，横向传导顺畅，处于稳态。"
        
    return {
        "status_code": status,
        "message": message,
        "time_dilation_factor": time_dilation
    }
