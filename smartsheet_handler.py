import smartsheet # pip install smartsheet-python-sdk
from project import Project # project.pyからProjectクラスをインポート
from task import Task # task.pyからTaskクラスをインポート
from member import Member # member.pyからMemberクラスをインポート
from typing import List # List型を使うために必要
from datetime import datetime # datetime型を使うために必要
import re  # 正規表現を使用するために必要


class SmartsheetHandler: # SmartsheetHandlerクラス
    def __init__(self, api_key): # コンストラクタ
        self.smartsheet_client = smartsheet.Smartsheet(api_key) # Smartsheetクライアントを作成

    def read_projects_tasks_from_sheet(self, sheet_id) -> List[Project]: # Smartsheetからプロジェクトとタスクを読み込むメソッド
        sheet = self.smartsheet_client.Sheets.get_sheet(sheet_id)  # Smartsheetからシートを取得

        projects_dict = {}  # 空の辞書を作成
        tasks_dict = {}  # 空の辞書を作成

        for row in sheet.rows:
            # Create a dictionary to store cell values with column names as keys
            cell_values = {}  # 空の辞書を作成
            for cell in row.cells:  # セルを一つずつ取り出す
                column_title = next((col.title for col in sheet.columns if col.id == cell.column_id), None)  # カラムタイトルを取得
                cell_values[column_title] = cell.value  # セルの値を辞書に追加

            project_id = cell_values["Project ID"]  # プロジェクトIDを取得
            task_id = cell_values["Task ID"]  # タスクIDを取得

            # Create and store Project objects
            if project_id not in projects_dict:  # プロジェクトIDが辞書に存在しないか確認
                project = Project(project_id, cell_values["Project Name"], [])  # プロジェクトを作成
                projects_dict[project_id] = project  # プロジェクトを辞書に追加

            # Create and store Task objects
            if task_id not in tasks_dict:  # タスクIDが辞書に存在しないか確認
                required_skills = cell_values["Required Skills"].split(',')  # 必要スキルを取得
                prerequisite_tasks = list(map(int, cell_values["Prerequisite Tasks"].split(','))) if cell_values["Prerequisite Tasks"] else []  # 前提タスクを取得
                start_date = datetime.strptime(cell_values["Start Date"], "%Y-%m-%dT%H:%M:%S").date() # 開始日を取得
                end_date = datetime.strptime(cell_values["End Date"], "%Y-%m-%dT%H:%M:%S").date() # 終了日を取得
                task = Task(task_id, cell_values["Task Name"], start_date, end_date, cell_values["Budget"], required_skills, prerequisite_tasks)  # タスクを作成

                projects_dict[project_id].add_task(task)  # タスクをプロジェクトに追加
                tasks_dict[task_id] = task  # タスクを辞書に追加

        return list(projects_dict.values())  # プロジェクトのリストを返す

    def read_members_from_sheet(self, sheet_id) -> List[Member]: # Smartsheetからメンバーを読み込むメソッド
        sheet = self.smartsheet_client.Sheets.get_sheet(sheet_id)  # Smartsheetからシートを取得

        members_dict = {}  # 空の辞書を作成

        for row in sheet.rows:
            # Create a dictionary to store cell values with column names as keys
            cell_values = {}  # 空の辞書を作成
            for cell in row.cells:  # セルを一つずつ取り出す
                column_title = next((col.title for col in sheet.columns if col.id == cell.column_id), None)  # カラムタイトルを取得
                cell_values[column_title] = cell.value  # セルの値を辞書に追加

            member_id = cell_values["Member ID"]  # メンバーIDを取得

            if member_id not in members_dict:  # メンバーIDが辞書に存在しないか確認
                member_skills = cell_values["Member Skills"].split(',')  # メンバースキルを取得
                member = Member(member_id, cell_values["Member Name"], member_skills, cell_values["Member Cost"])  # メンバーを作成
                members_dict[member_id] = member  # メンバーを辞書に追加

        return list(members_dict.values())  # メンバーのリストを返す

    def write_data_to_sheet(self, sheet_id, task_assignments): # Smartsheetにデータを書き込むメソッド
        # Initialize the Smartsheet client
        sheet = self.smartsheet_client.Sheets.get_sheet(sheet_id) # Smartsheetからシートを取得

        # Delete all rows in the sheet
        row_ids = [row.id for row in sheet.rows] # シートのすべての行のIDを取得
        if row_ids: # 行のIDが存在するか確認
            self.smartsheet_client.Sheets.delete_rows(sheet_id, row_ids) # シートから行を削除

        # Set the column names
        column_map = {column.title: column.id for column in sheet.columns} # カラム名とカラムIDの辞書を作成

        # Create new rows
        new_rows = [] # 空のリストを作成
        for assignment in task_assignments: # タスク割り当てを一つずつ取り出す
            task = assignment.task # タスクを取得
            member = assignment.assigned_member # メンバーを取得
            actual_cost = assignment.get_actual_cost() # 実際のコストを取得
            ga_parameters_values = assignment.get_ga_parameters_values() # GAパラメータの値を取得

            new_row = smartsheet.models.Row() # Use smartsheet.models.Row() instead of sheet.models.Row()
            new_row = smartsheet.models.Row({"toBottom": True})  # 行を作成
            new_row.cells = [
                smartsheet.models.Cell({"columnId": column_map["Solution"], "value": assignment.solution}),
                smartsheet.models.Cell({"columnId": column_map["Population Size"], "value": ga_parameters_values[0] if len(ga_parameters_values) > 0 else ''}),
                smartsheet.models.Cell({"columnId": column_map["Num Generations"], "value": ga_parameters_values[1] if len(ga_parameters_values) > 1 else ''}),
                smartsheet.models.Cell({"columnId": column_map["Crossover Prob"], "value": ga_parameters_values[2] if len(ga_parameters_values) > 2 else ''}),
                smartsheet.models.Cell({"columnId": column_map["Crossover Type"], "value": ga_parameters_values[3] if len(ga_parameters_values) > 3 else ''}),
                smartsheet.models.Cell({"columnId": column_map["Mutation Prob"], "value": ga_parameters_values[4] if len(ga_parameters_values) > 4 else ''}),
                smartsheet.models.Cell({"columnId": column_map["Indpb"], "value": ga_parameters_values[5] if len(ga_parameters_values) > 5 else ''}),
                smartsheet.models.Cell({"columnId": column_map["Mutation Type"], "value": ga_parameters_values[6] if len(ga_parameters_values) > 6 else ''}),
                smartsheet.models.Cell({"columnId": column_map["Selection Type"], "value": ga_parameters_values[7] if len(ga_parameters_values) > 7 else ''}),
                smartsheet.models.Cell({"columnId": column_map["Objective Weights"], "value": ga_parameters_values[8] if len(ga_parameters_values) > 8 else ''}),
                smartsheet.models.Cell({"columnId": column_map["Constraint Weights"], "value": ga_parameters_values[9] if len(ga_parameters_values) > 9 else ''}),
                smartsheet.models.Cell({"columnId": column_map["Constraint Violations"], "value": ','.join(assignment.constraint_violations) if assignment.constraint_violations else ''}),
                smartsheet.models.Cell({"columnId": column_map["Project ID"], "value": assignment.project_id}),
                smartsheet.models.Cell({"columnId": column_map["Project Name"], "value": assignment.project_name}),
                smartsheet.models.Cell({"columnId": column_map["Task ID"], "value": task.id}),
                smartsheet.models.Cell({"columnId": column_map["Task Name"], "value": task.name}),
                smartsheet.models.Cell({"columnId": column_map["Start Date"], "value": task.start_date.strftime("%Y-%m-%d")}),
                smartsheet.models.Cell({"columnId": column_map["End Date"], "value": task.end_date.strftime("%Y-%m-%d")}),
                smartsheet.models.Cell({"columnId": column_map["Duration"], "value": task.get_duration()}),
                smartsheet.models.Cell({"columnId": column_map["Budget"], "value": task.budget}),
                smartsheet.models.Cell({"columnId": column_map["Required Skills"], "value": ",".join(task.skill_set)}),
                smartsheet.models.Cell({"columnId": column_map["Prerequisite Tasks"], "value": ",".join(map(str, task.prerequisite_tasks))}),
                smartsheet.models.Cell({"columnId": column_map["Member ID"], "value": member.id if member is not None else ''}),
                smartsheet.models.Cell({"columnId": column_map["Member Name"], "value": member.name if member is not None else ''}),
                smartsheet.models.Cell({"columnId": column_map["Member Skills"], "value": ",".join(member.skill_set) if member is not None else ''}),
                smartsheet.models.Cell({"columnId": column_map["Member Cost"], "value": member.cost if member is not None else ''}),
                smartsheet.models.Cell({"columnId": column_map["Actual Cost"], "value": actual_cost if actual_cost is not None else ''}),
            ] # セルを作成

            new_rows.append(new_row) # リストに追加

        # Add rows to the sheet
        self.smartsheet_client.Sheets.add_rows(sheet_id, new_rows)  # シートに行を追加

    def copy_and_rename_sheet(self, original_sheet_id, set_name, folder_id):
        # 元のシート情報を取得
        # original_sheet = self.smartsheet_client.Sheets.get_sheet(original_sheet_id)

        # 元のシート名を取得
        # original_sheet_name = original_sheet.name

        # シートの複製
        new_sheet_name = set_name[:50]  # set_nameの先頭50文字を取得
        response = self.smartsheet_client.Sheets.copy_sheet(
            original_sheet_id,
            smartsheet.models.ContainerDestination({
                'destination_type': 'folder',
                'destination_id': int(folder_id),  # フォルダIDを数値に変換して渡す
                'new_name': new_sheet_name  # 新しいシート名を指定
            })
        )
        
        # 応答から新しいシートの情報を取得
        new_sheet = response.result
            
        return new_sheet

