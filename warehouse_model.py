"""
太极资源与仓库模型 - 通用业务模板
适用于企业ERP、智慧工地BIM、游戏地图、中医脏腑等场景。
"""
from taiji_engine import SIX_PI_POW_5, calculate_node_health

class Warehouse:
    """仓库（棋盘/背景）- 虚轴/阴/0"""
    def __init__(self, name: str, parent=None, chi: float = 2000.0, is_leaf: bool = False):
        self.name = name
        self.parent = parent
        self.chi = chi  # 固定资产/结构刚度
        self.is_leaf = is_leaf  # 是否为最小子库（承载点和增值点）
        self.children = []
        self.alive = True
        self.tax_collected = 0.0
        
        if parent:
            parent.children.append(self)

    def real_to_virtual(self, resource_value: float, install_ratio: float = 0.1) -> bool:
        """实转虚：资源买进来，安装成固定资产"""
        self.chi = resource_value * (1 - install_ratio)
        health = calculate_node_health(self.chi)
        self.alive = health["is_alive"]
        return self.alive

    def virtual_to_real(self, dismantle_loss: float = 0.15) -> float:
        """虚转实：拆解仓库，变卖回资源"""
        recovered = self.chi * (1 - dismantle_loss)
        self.alive = False
        self.chi = 0
        return recovered

    def collect_tax(self, tax_rate: float = 0.3):
        """副库向上抽税：只有叶子节点产生利润"""
        self.tax_collected = 0
        for child in self.children:
            if child.alive:
                if child.is_leaf:
                    profit = getattr(child, 'e_profit', 100)
                    tax = profit * tax_rate
                    child.cumulative_profit = getattr(child, 'cumulative_profit', 0) + (profit - tax)
                    self.tax_collected += tax
                else:
                    child.collect_tax(tax_rate)
                    self.tax_collected += child.tax_collected * tax_rate

class Resource:
    """资源（棋子/实体）- 实轴/阳/1"""
    def __init__(self, flow_id: str, value: float):
        self.flow_id = flow_id
        self.value = value
        self.current_node = None

    def inject_to(self, warehouse: Warehouse):
        """资源注入仓库"""
        self.current_node = warehouse
