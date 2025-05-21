from typing import List # List型を使うために必要
from datetime import datetime # datetime型を使うために必要

class Task: # タスククラス
    def __init__(self, id: int, name: str, start_date: str, end_date: str, budget: float, skill_set: List[str], prerequisite_tasks: List['Task']): # コンストラクタ
        self.id = id # タスクID
        self.name = name # タスク名
        self.start_date = start_date # 開始日
        self.end_date = end_date # 終了日
        self.budget = budget # 予算
        self.skill_set = skill_set # スキルセット
        self.prerequisite_tasks = prerequisite_tasks # 前提タスク

    def add_prerequisite_task(self, task: 'Task') -> None: # 前提タスクを追加するメソッド
        if task not in self.prerequisite_tasks: # 前提タスクが既に追加されていないか確認
            self.prerequisite_tasks.append(task) # 追加

    def remove_prerequisite_task(self, task: 'Task') -> None: # 前提タスクを削除するメソッド
        if task in self.prerequisite_tasks: # 前提タスクが既に追加されているか確認
            self.prerequisite_tasks.remove(task) # 削除

    def get_prerequisite_tasks(self) -> List['Task']: # 前提タスクを取得するメソッド
        return self.prerequisite_tasks # 前提タスクを返す

    def get_all_prerequisite_tasks(self) -> List['Task']: # 前提タスクと前提タスクの前提タスクを取得するメソッド
        all_prerequisite_tasks = [] # 空のリストを作成
        for task in self.prerequisite_tasks: # 前提タスクを一つずつ取り出す
            all_prerequisite_tasks.append(task) # 前提タスクを追加
            all_prerequisite_tasks.extend(task.get_all_prerequisite_tasks()) # 前提タスクの前提タスクを再帰的に追加
        return all_prerequisite_tasks # 前提タスクと前提タスクの前提タスクを返す
        
    def get_duration(self) -> int:  # タスクの期間を取得するメソッド
        if isinstance(self.start_date, str): # 開始日が文字列型の場合
            start_date_obj = datetime.strptime(self.start_date, "%Y-%m-%d")  # 開始日をdatetime型に変換
        else: # 開始日がdatetime型の場合
            start_date_obj = self.start_date # 開始日をそのまま使う

        if isinstance(self.end_date, str): # 終了日が文字列型の場合
            end_date_obj = datetime.strptime(self.end_date, "%Y-%m-%d")  # 終了日をdatetime型に変換
        else: # 終了日がdatetime型の場合
            end_date_obj = self.end_date # 終了日をそのまま使う

        duration = (end_date_obj - start_date_obj).days + 1  # 期間を計算
        return duration  # 期間を返す
