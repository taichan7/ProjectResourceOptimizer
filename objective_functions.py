import numpy as np # NumPyをインポート

class ObjectiveFunctions: # 目的関数クラス
    def __init__(self, tasks, members, individual): # コンストラクタ
        self.tasks = tasks  # タスクリスト
        self.members = members # メンバーリスト
        self.individual = individual # 個体

    def f1(self): # 目的関数1 総コストを計算する
        total_cost = 0 # 総コスト
        for task_index, task in enumerate(self.tasks): # タスクを一つずつ取り出す
            task_duration = task.get_duration() # タスクの所要日数（労働日数）
            assigned_member_index = self.individual[task_index] # タスクに割り当てられたメンバーのインデックス
            assigned_member = self.members[assigned_member_index] # 割り当てられたメンバーを取得
            total_cost += assigned_member.cost * task_duration # 総コストを計算

        # print(f"TotalCost:", total_cost)  # 総コストを表示
        return total_cost # 総コストを返す

    def f2(self): # 目的関数2 メンバーごとの労働日数の標準偏差を計算する
        labor_days = [0] * len(self.members) # メンバーごとの労働日数
        for task_index, task in enumerate(self.tasks): # タスクを一つずつ取り出す
            task_duration = task.get_duration() # タスクの所要日数（労働日数）
            assigned_member_index = self.individual[task_index] # タスクに割り当てられたメンバーのインデックス
            labor_days[assigned_member_index] += task_duration # メンバーの労働日数を加算
        std_dev_labor_days = np.std(labor_days) # メンバーごとの労働日数の標準偏差
        
        # print(f"StdDevLaborDays:", std_dev_labor_days)  # 標準偏差を表示
        return std_dev_labor_days # 標準偏差を返す