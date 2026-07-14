# -*- coding: utf-8 -*-
# Taiji-Systems 动力学交互演示脚本
# 展示调节 chi 和 delta 时，系统的三种相态：稳态恢复、涌现跃迁、雪崩归零

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# 将上一级目录加入系统路径，以便导入 taiji_systems 模块
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))

from taiji_systems.core_engine import (
    SIX_PI_POW_5,
    calculate_macro_energy,
    calculate_compensation_balance,
    monitor_deviation_degree
)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 基础网络参数
N_NODES = 100         # 节点数
E_PROFIT = 200.0      # 单节点基础利润
ALPHA = 0.5           # 环境抽税系数
D = 10.0              # 基础拓扑距离

def simulate_system_response(delta_target: float, chi: float, steps: int = 100):
    """模拟系统在特定参数下的动力学响应"""
    # 初始状态
    delta = 0.1
    z_trans = 1800.0
    z_long = 500.0
    
    delta_history = []
    macro_energy_history = []
    z_long_history = []
    
    for t in range(steps):
        # 1. 计算当前网络总利润
        macro_E = calculate_macro_energy(E_PROFIT, ALPHA, D, chi, N_NODES)
        
        # 2. 根据利润与底线的关系，更新偏离度 Delta
        if macro_E > SIX_PI_POW_5:
            # 利润充裕，系统有自愈能力，Delta 向目标值缓慢收敛
            delta += (delta_target - delta) * 0.05
        else:
            # 利润跌破底线，横向传导失效，Delta 加速恶化趋向 1 (雪崩)
            delta += (1.0 - delta) * 0.2
            
        delta = np.clip(delta, 0, 0.999)
        
        # 3. 更新代偿势能 (横向堵死，纵向暴增)
        if delta > 0.8:
            # 横向传导开始死锁，Z_trans 下降，Z_long 被迫暴增
            z_trans *= 0.95
            z_long = np.sqrt(max(0, SIX_PI_POW_5**2 - z_trans**2)) + (delta - 0.8) * 5000
        else:
            # 正常波动
            z_trans = 1800.0 + np.random.randn() * 50
            z_long = 500.0 + np.random.randn() * 20
            
        delta_history.append(delta)
        macro_energy_history.append(macro_E)
        z_long_history.append(z_long)
        
    return delta_history, macro_energy_history, z_long_history

# ================= 模拟三种相态 =================
steps = 150

# 相态1：稳态恢复 (高交联度，目标Delta低)
delta1, macro_E1, z_long1 = simulate_system_response(delta_target=0.2, chi=2.5, steps=steps)

# 相态2：涌现跃迁 (中等交联度，目标Delta逼近临界值)
delta2, macro_E2, z_long2 = simulate_system_response(delta_target=0.85, chi=0.8, steps=steps)

# 相态3：雪崩归零 (极低交联度，横向传导堵死)
delta3, macro_E3, z_long3 = simulate_system_response(delta_target=0.5, chi=0.1, steps=steps)

# ================= 绘制对比图 =================
fig, axs = plt.subplots(3, 1, figsize=(12, 15))

time_axis = np.arange(steps)

# 绘制相态1：稳态恢复
axs[0].plot(time_axis, delta1, label='偏离度 Δ', color='blue')
axs[0].axhline(y=0.8, color='r', linestyle='--', label='预警线 (Δ=0.8)')
axs[0].set_title('相态1：稳态恢复 (高交联度 χ=2.5) -> 横向传导顺畅，系统自愈', fontsize=14)
axs[0].set_ylabel('偏离度 Δ')
axs[0].set_ylim(0, 1.1)
axs[0].legend()
axs[0].grid(True)

# 绘制相态2：涌现跃迁
axs[1].plot(time_axis, delta2, label='偏离度 Δ', color='orange')
axs[1].plot(time_axis, [zl/10000 for zl in z_long2], label='纵向代偿 Z_long (缩放)', color='red')
axs[1].axhline(y=0.95, color='black', linestyle='--', label='雪崩临界线 (Δ=0.95)')
axs[1].set_title('相态2：涌现跃迁 (中交联度 χ=0.8) -> 逼近64态饱和，纵向代偿开始激增', fontsize=14)
axs[1].set_ylabel('数值')
axs[1].set_ylim(0, 1.5)
axs[1].legend()
axs[1].grid(True)

# 绘制相态3：雪崩归零
axs[2].plot(time_axis, delta3, label='偏离度 Δ', color='red')
axs[2].fill_between(time_axis, 0, delta3, color='red', alpha=0.2)
axs[2].axhline(y=0.95, color='black', linestyle='--', label='雪崩临界线 (Δ=0.95)')
axs[2].set_title('相态3：雪崩归零 (低交联度 χ=0.1) -> 横向利润跌破6π^5，Δ冲刺至1，网络解体', fontsize=14)
axs[2].set_ylabel('偏离度 Δ')
axs[2].set_xlabel('时间步')
axs[2].set_ylim(0, 1.1)
axs[2].legend()
axs[2].grid(True)

plt.tight_layout()
plt.show()

# ================= 打印引擎状态报告 =================
print("\n" + "="*50)
print("🔥 太极系统拓扑代偿监测仪 - 状态报告 🔥")
print("="*50)

print("\n【相态1：稳态恢复 末态对账】")
status1 = monitor_deviation_degree(delta1[-1])
print(f"偏离度 Δ: {delta1[-1]:.4f}")
print(f"网络总利润 ΔE_macro: {macro_E1[-1]:.2f} (底线 {SIX_PI_POW_5:.2f})")
print(f"系统状态: {status1['status_code']} - {status1['message']}")

print("\n【相态2：涌现跃迁 末态对账】")
status2 = monitor_deviation_degree(delta2[-1])
comp2 = calculate_compensation_balance(1500, z_long2[-1])
print(f"偏离度 Δ: {delta2[-1]:.4f}")
print(f"纵向代偿 Z_long 激增至: {z_long2[-1]:.2f}")
print(f"代偿守恒状态: {'突破底线暴雷!' if not comp2['is_balanced'] else '仍在守恒圈内'}")
print(f"系统状态: {status2['status_code']} - {status2['message']}")

print("\n【相态3：雪崩归零 末态对账】")
status3 = monitor_deviation_degree(delta3[-1])
print(f"偏离度 Δ: {delta3[-1]:.4f}")
print(f"网络总利润 ΔE_macro: {macro_E3[-1]:.2f} (低于底线，网络解体)")
print(f"系统状态: {status3['status_code']} - {status3['message']}")
print("="*50)
