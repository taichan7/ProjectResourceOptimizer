from member import Member # member.pyからMemberクラスをインポート
from project import Project # project.pyからProjectクラスをインポート
from task import Task # task.pyからTaskクラスをインポート
import csv # csvモジュールをインポート

class TaskAssignment: # タスク割り当てクラス
    def __init__(self, project: Project, task: Task, member: Member, solution: int, constraint_violations: list, ga_parameters: list): # コンストラクタ
        self.project_id = project.id # プロジェクトID
        self.project_name = project.name # プロジェクト名
        self.task = task # タスク
        self.assigned_member = member  # 追加
        self.solution = solution  # 追加: ソリューション番号
        self.constraint_violations = constraint_violations  # 追加: 制約違反情報
        self.ga_parameters = ga_parameters  # 追加: GAパラメータ

    def assign_member(self, member: Member): # メンバーを割り当てるメソッド
        if self.assigned_member is None:  # 割り当てられたメンバーがいないか確認
            self.assigned_member = member  # 割り当てられたメンバーを設定
        else: # 割り当てられたメンバーがいる場合
            raise Exception("メンバーはすでに割り当てられています") # 例外を発生させる

    def unassign_member(self): # メンバーの割り当てを解除するメソッド
        self.assigned_member = None # 割り当てを解除

    def get_assigned_member(self): # 割り当てられたメンバーを取得するメソッド
        return self.assigned_member # 割り当てられたメンバーを返す
    
    def get_task(self): # タスクを取得するメソッド
        return self.task # タスクを返す
    
    def get_actual_cost(self): # 実際のコストを取得するメソッド
        if self.assigned_member is not None: # 割り当てられたメンバーがいるか確認
            return self.assigned_member.cost * self.task.get_duration() # 実際のコストを返す
        return None # 割り当てられたメンバーがいない場合はNoneを返す

    def get_ga_parameters_values(self): # GAパラメータの値を取得するメソッド
        return self.ga_parameters # GAパラメータの値を返す

    def to_csv(self, file_path: str, set_name: str):
        write_header = False  # ヘッダーを書き込むかどうかのフラグ
        # ファイルが存在しないか、空の場合にヘッダーを書き込む
        try:
            with open(file_path, 'r', newline="", encoding="utf-8") as f:
                write_header = f.readable() and f.readline().strip() == ""
        except FileNotFoundError:
            write_header = True

        with open(file_path, "a", newline="", encoding="utf-8") as f:  # ファイルを追記モードで開く
            csv_writer = csv.writer(f)
            headers = ["Set Name", "Solution", "Population Size", "Num Generations", "Crossover Prob", "Crossover Type", "Mutation Prob", "Indpb", "Mutation Type", "Selection Type", "Objective Weights", "Constraint Weights", "Scaling_Factor_F2", "Constraint Violations","Project ID", "Project Name", "Task ID", "Task Name", "Start Date", "End Date", "Budget",
                    "Required Skills", "Prerequisite Tasks", "Member ID", "Member Name", "Member Skills", "Member Cost", "Actual Cost"]
            if write_header:
                csv_writer.writerow(headers)  # ヘッダーを出力

            row_data = [set_name, self.solution] + self.ga_parameters + [','.join(self.constraint_violations),
                        self.project_id, self.project_name, self.task.id, self.task.name,
                        self.task.start_date, self.task.end_date, self.task.budget,
                        ','.join(self.task.skill_set), ','.join(map(str, self.task.prerequisite_tasks))]
            if self.assigned_member is not None:
                row_data += [self.assigned_member.id, self.assigned_member.name, ','.join(self.assigned_member.skill_set),
                            self.assigned_member.cost, self.get_actual_cost()]
            else:
                row_data += [None, None, None, None, None]

            csv_writer.writerow(row_data)  # データを出力
