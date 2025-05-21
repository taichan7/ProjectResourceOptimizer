import random # random をインポート
from typing import List # List型を使うために必要
from datetime import date, timedelta # date型とtimedelta型を使うために必要
from member import Member # メンバークラスをインポート
from project import Project # プロジェクトクラスをインポート
from task import Task # タスククラスをインポート
import csv # csvをインポート
from datetime import datetime # datetime型を使うために必要

class TestDataGenerator: # テストデータ生成クラス
    @staticmethod # クラスメソッド
    def generate_projects(num_projects: int, num_tasks: int) -> List[Project]: # プロジェクトを生成するメソッド
        projects = [Project(i, f"Project {i}", []) for i in range(num_projects)] # プロジェクトを生成
        tasks = TestDataGenerator.generate_tasks(num_tasks) # タスクを生成

        for task in tasks: # タスクを一つずつ取り出す
            project = random.choice(projects) # プロジェクトをランダムに選択
            while task in project.tasks:  # タスクが既にプロジェクトに関連付けられている場合、別のプロジェクトを選択
                project = random.choice(projects) # プロジェクトをランダムに選択
            project.add_task(task) # タスクをプロジェクトに関連付ける

        return projects # プロジェクトを返す

    @staticmethod # クラスメソッド
    def generate_tasks(num_tasks: int) -> List[Task]:
        tasks = []
        for i in range(num_tasks):
            start_date = date(2023, 1, 1) + timedelta(days=random.randint(0, 364))
            end_date = start_date + timedelta(days=random.randint(1, 30))
            budget = random.uniform(1000, 10000)
            skill_set = [f"Skill {i}" for i in range(random.randint(1, 5))]
            prerequisite_tasks_ids = []

            candidate_tasks = [task for task in tasks if task.start_date < start_date]

            if candidate_tasks:
                num_prerequisite_tasks = random.randint(0, len(candidate_tasks))
                prerequisite_tasks = random.sample(candidate_tasks, num_prerequisite_tasks)
                prerequisite_tasks_ids = [prereq_task.id for prereq_task in prerequisite_tasks]

            task = Task(i, f"Task {i}", start_date, end_date, budget, skill_set, prerequisite_tasks_ids)
            tasks.append(task)
        return tasks

    @staticmethod # クラスメソッド
    def generate_members(num_members: int) -> List[Member]: # メンバーを生成するメソッド
        members = [] # 空のリストを作成
        skill_pool = [f"Skill {i}" for i in range(20)] # スキルプールを生成
        for i in range(num_members): # メンバーを生成
            skill_set = random.sample(skill_pool, random.randint(1, 5)) # スキルセットを生成
            cost = random.uniform(10, 100) # コストを生成
            member = Member(i, f"Member {i}", skill_set, cost) # メンバーを生成
            members.append(member) # メンバーを追加
        return members # メンバーを返す
    
    @staticmethod # クラスメソッド
    def read_projects_and_tasks_from_csv(file_path: str) -> List[Project]: # CSVファイルからプロジェクトとタスクを読み込むメソッド
        projects_dict = {} # 空の辞書を作成
        with open(file_path, "r") as f: # CSVファイルを開く
            csv_reader = csv.reader(f) # CSVファイルを読み込む
            next(csv_reader) # 1行目を読み飛ばす
            for row in csv_reader: # CSVファイルの行を一つずつ取り出す
                project_id = int(row[0]) # プロジェクトIDを取得
                project_name = row[1] # プロジェクト名を取得
                task_id = int(row[2]) # タスクIDを取得
                task_name = row[3] # タスク名を取得
                start_date = datetime.strptime(row[4], "%Y-%m-%d") # 開始日を取得
                end_date = datetime.strptime(row[5], "%Y-%m-%d") # 終了日を取得
                budget = float(row[6]) # 予算を取得
                skill_set = row[7].split(",") # スキルセットを取得
                prerequisite_tasks = [int(pt_id.strip()) for pt_id in row[8].split(",") if pt_id.strip()] # 前提タスクを取得
                task = Task(task_id, task_name, start_date, end_date, budget, skill_set, prerequisite_tasks) # タスクを生成

                if project_id not in projects_dict: # プロジェクトが辞書に存在しない場合
                    project = Project(project_id, project_name, [task]) # プロジェクトを生成
                    projects_dict[project_id] = project # プロジェクトを辞書に追加
                else: # プロジェクトが辞書に存在する場合
                    projects_dict[project_id].add_task(task) # タスクをプロジェクトに追加

        return list(projects_dict.values()) # プロジェクトを返す

    @staticmethod # クラスメソッド
    def read_members_from_csv(file_path: str) -> List[Member]: # CSVファイルからメンバーを読み込むメソッド
        members = [] # 空のリストを作成
        with open(file_path, "r") as f: # CSVファイルを開く
            csv_reader = csv.reader(f) # CSVファイルを読み込む
            next(csv_reader)  # 1行目を読み飛ばす
            for row in csv_reader: # CSVファイルの行を一つずつ取り出す
                member_id = int(row[0]) # メンバーIDを取得
                member_name = row[1] # メンバー名を取得
                skill_set = row[2].split(",") # スキルセットを取得
                cost = float(row[3]) # コストを取得
                member = Member(member_id, member_name, skill_set, cost) # メンバーを生成
                members.append(member) # メンバーを追加
        return members # メンバーを返す