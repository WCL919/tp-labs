"""实验 2：面向对象基础。

    GameObject              ← 所有游戏对象的基类
    |-- Building            ← 建筑
    |   |-- Fort            ← 要塞，实现 Attacker（能打）
    |   `-- MobileHome      ← 房车，实现 Moveable（能跑）
    `-- Unit                ← 单位
        `-- Archer          ← 弓箭手，实现 Attacker 和 Moveable

运行方式：python main.py
"""

from abc import ABC, abstractmethod


# ABC = Abstract Base Class，Python 里用来做抽象类和接口的基类。
# 继承它以后，带 @abstractmethod 标记的方法子类必须实现，否则报错。


class GameObject(ABC):
    """所有游戏对象的基类。

    这里放「任何对象都有」的东西：编号、名字、坐标。
    子类不用重复写这几个字段和四个 get 方法，直接继承就有。
    """

    def __init__(self, object_id: int, name: str, x: int = 0, y: int = 0) -> None:
        # 前面加下划线 _ 是 Python 的习惯，表示「这是内部字段，别直接改，
        # 要通过 getId() / getName() 这些方法来读」。
        self._id = object_id
        self._name = name
        self._x = x
        self._y = y

    def getId(self) -> int:
        return self._id

    def getName(self) -> str:
        return self._name

    def getX(self) -> int:
        return self._x

    def getY(self) -> int:
        return self._y

    def __str__(self) -> str:
        # 打印对象时自动调用这个方法。比如 print(archer) 会输出
        # Archer#1 'Archer' (0, 0)
        return f"{type(self).__name__}#{self._id} '{self._name}' ({self._x}, {self._y})"


class Attacker(ABC):
    """接口：能攻击别人的东西。

    这里只写「必须有 attack 方法」，不写具体怎么打。
    注意它是接口不是类——攻击这个能力不能放进某一条继承线里，
    因为要塞（建筑）能打、弓箭手（单位）也能打，它们根本不在一条线上。
    """

    @abstractmethod
    def attack(self, unit: "Unit") -> None:
        """攻击指定的单位。参数名写成 "Unit" 加引号，因为下面才定义 Unit。"""


class Moveable(ABC):
    """接口：能在图上移动的东西。"""

    @abstractmethod
    def moveTo(self, x: int, y: int) -> None:
        """移动到坐标 (x, y)。"""


class Unit(GameObject, ABC):
    """单位——玩家能操控的东西。

    做成抽象类是因为：游戏里没有「一个纯单位」这种东西，
    永远是具体类型（弓箭手、剑士……），所以不允许直接创建 Unit。
    """

    def __init__(self, object_id: int, name: str, max_hp: float, x: int = 0, y: int = 0) -> None:
        # super().__init__(...) 是调用父类 GameObject 的初始化，
        # 先把 id / 名字 / 坐标存好，再处理血量。
        super().__init__(object_id, name, x, y)
        # float() 转成小数，因为伤害可能带小数，血量跟着用小数。
        self._hp = float(max_hp)

    def isAlive(self) -> bool:
        # 血量大于 0 就算活着
        return self._hp > 0

    def getHp(self) -> float:
        return self._hp

    def receiveDamage(self, damage: float) -> None:
        if damage < 0:
            raise ValueError("damage must not be negative")
        # max(0.0, ...) 是防止血量变成负数，最低就是 0。
        self._hp = max(0.0, self._hp - damage)


class Building(GameObject, ABC):
    """建筑。

    抽象类：要塞和房车的行为不一样，唯一的共同点是「建好了没有」。
    """

    def __init__(
        self,
        object_id: int,
        name: str,
        x: int = 0,
        y: int = 0,
        built: bool = True,
    ) -> None:
        super().__init__(object_id, name, x, y)
        self._built = built

    def isBuilt(self) -> bool:
        return self._built


class Archer(Unit, Attacker, Moveable):
    """弓箭手。

    一个类可以继承一个父类（Unit）同时实现多个接口（Attacker、Moveable），
    这就是「多继承」，但这里只有 Unit 有实际代码，另外两个都是接口。
    """

    def __init__(
        self,
        object_id: int,
        name: str,
        max_hp: float = 100.0,
        damage: float = 15.0,
        x: int = 0,
        y: int = 0,
    ) -> None:
        super().__init__(object_id, name, max_hp, x, y)
        self._damage = damage

    def attack(self, unit: Unit) -> None:
        # 攻击 = 让对方掉血。具体掉多少由自己的 _damage 决定。
        unit.receiveDamage(self._damage)

    def moveTo(self, x: int, y: int) -> None:
        # 改坐标就行，父类里 _x / _y 已经存在。
        self._x = x
        self._y = y


class Fort(Building, Attacker):
    """要塞：建筑，但能开炮打人。"""

    def __init__(
        self,
        object_id: int,
        name: str,
        damage: float = 40.0,
        x: int = 0,
        y: int = 0,
        built: bool = True,
    ) -> None:
        super().__init__(object_id, name, x, y, built)
        self._damage = damage

    def attack(self, unit: Unit) -> None:
        unit.receiveDamage(self._damage)


class MobileHome(Building, Moveable):
    """房车：建筑，但能移动。它不需要 attack 方法，因为它不实现 Attacker。"""

    def moveTo(self, x: int, y: int) -> None:
        self._x = x
        self._y = y


def show_state(label: str, unit: Unit) -> None:
    """打印一个单位当前的血量和生死状态。"""
    # :<10 表示左对齐占 10 个字符，:>5.1f 表示右对齐保留 1 位小数，
    # 目的只是让输出整齐，不影响逻辑。
    print(f"  {label:<10} hp={unit.getHp():>5.1f}  alive={unit.isAlive()}")

#demo
def main() -> None:
    # 造四个对象。参数里的 max_hp / damage / x / y 都是可选的。
    archer = Archer(1, "Archer", max_hp=80, damage=15, x=0, y=0)
    defender = Archer(2, "Defender", max_hp=80, damage=15, x=3, y=4)
    fort = Fort(3, "Fort", damage=40, x=10, y=10)
    home = MobileHome(4, "MobileHome", x=-5, y=2)

    print("=== All game objects ===")
    for obj in (archer, defender, fort, home):
        print(f"  {obj}")

    print("\n=== Movement ===")
    # 只有实现了 Moveable 的类才有 moveTo，所以这里只能对 archer 和 home 调用。
    archer.moveTo(2, 2)
    home.moveTo(4, 4)
    print(f"  archer     -> ({archer.getX()}, {archer.getY()})")
    print(f"  mobilehome -> ({home.getX()}, {home.getY()})")
    print(f"  fort stays -> ({fort.getX()}, {fort.getY()})")

    print("\n=== Combat ===")
    show_state("start", defender)
    archer.attack(defender)  # 弓箭手打，15 点
    show_state("after x15", defender)
    fort.attack(defender)  # 要塞开炮，40 点
    show_state("after x40", defender)
    fort.attack(defender)  # 再 40 点，血量被压到 0
    show_state("after x40", defender)

    print("\n=== States ===")
    print(f"  defender is alive: {defender.isAlive()}")
    print(f"  archer is alive:   {archer.isAlive()}")
    print(f"  fort is built:     {fort.isBuilt()}")
    print(f"  mobilehome is built: {home.isBuilt()}")


# 只有直接运行这个文件时才执行 main()；被别的文件 import 时不执行。
if __name__ == "__main__":
    main()
