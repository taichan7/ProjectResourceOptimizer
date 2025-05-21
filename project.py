from task import Task # task.pyからTaskクラスをインポート
from typing import List # List型を使うために必要

class Project: # プロジェクトクラス
    def __init__(self, id: int, name: str, tasks: List[Task]): # コンストラクタ
        self.id = id # プロジェクトID
        self.name = name # プロジェクト名
        self.tasks = tasks # タスク

    def add_task(self, task: Task) -> None: # タスクを追加するメソッド
        self.tasks.append(task) # 追加

    def remove_task(self, task_id: int) -> None: # タスクを削除するメソッド
        for task in self.tasks: # タスクを一つずつ取り出す
            if task.id == task_id: # タスクIDが一致するか確認
                self.tasks.remove(task) # 削除

    def get_tasks(self) -> List[Task]: # タスクを取得するメソッド
        return self.tasks # タスクを返す

    def get_all_tasks(self) -> List[Task]: # タスクとタスクの前提タスクを取得するメソッド
        all_tasks = [] # 空のリストを作成
        for task in self.tasks: # タスクを一つずつ取り出す
            all_tasks.append(task) # タスクを追加
            all_tasks.extend(task.get_all_prerequisite_tasks()) # タスクの前提タスクを再帰的に追加
        return list(set(all_tasks)) # タスクとタスクの前提タスクを返す