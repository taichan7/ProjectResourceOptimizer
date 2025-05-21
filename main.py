from optimizer import Optimizer # optimizer.pyからOptimizerクラスをインポート
from test_data_generator import TestDataGenerator # test_data_generator.pyからTestDataGeneratorクラスをインポート
from task_assignment import TaskAssignment # task_assignment.pyからTaskAssignmentクラスをインポート
from smartsheet_handler import SmartsheetHandler # smartsheet_handler.pyからSmartsheetHandlerクラスをインポート
from pareto_plotter import ParetoPlotter # pareto_plotter.pyからParetoPlotterクラスをインポート
from violation_writer import ViolationWriter # violation_writer.pyからViolationWriterクラスをインポート
from parameters import Parameters # parameters.pyからParametersクラスをインポート
from deap import tools # deapモジュールからtoolsをインポート
import os # osモジュールをインポート
import csv # csvモジュールをインポート
import numpy as np # NumPyをインポート

def main(): # メイン関数

    # # テストデータのパラメータ設定
    # num_projects = 5 # プロジェクト数
    # num_tasks = 100 # タスク数
    # num_members = 10 # メンバー数
    # # テストデータを生成
    # test_data_generator = TestDataGenerator()  # テストデータ生成クラスのインスタンスを作成
    # projects = test_data_generator.generate_projects(num_projects, num_tasks)  # プロジェクトを生成
    # members = test_data_generator.generate_members(num_members)  # メンバーを生成

    # # CSVファイルからデータを読み込む
    # projects_csv_file = os.path.join("..", "csv/projects_and_tasks.csv") # プロジェクトとタスクのCSVファイル
    # members_csv_file = os.path.join("..", "csv/members.csv") # メンバーのCSVファイル
    # projects = TestDataGenerator.read_projects_and_tasks_from_csv(projects_csv_file)  # プロジェクトを生成
    # members = TestDataGenerator.read_members_from_csv(members_csv_file)  # メンバーを生成

    params = Parameters() # パラメータクラスのインスタンスを作成
    # 実験のベースディレクトリを作成
    base_dir = os.path.join("..", "results", params.timestamp_str) # タイムスタンプのサブディレクトリを作成
    os.makedirs(base_dir, exist_ok=True) # ディレクトリを作成
    # 各実験のデータおよびサマリーCSVを格納するディレクトリ
    summary_csv_dir = base_dir  # サマリーCSVを格納するディレクトリ
    os.makedirs(summary_csv_dir, exist_ok=True)  # ディレクトリを作成

    api_key = params.api_key  # APIキー
    projects_tasks_sheet_id = params.projects_tasks_sheet_id  # プロジェクトとタスクのシートID
    members_sheet_id = params.members_sheet_id  # メンバーのシートID
    resource_optimizer_sheet_id = params.resource_optimizer_sheet_id  # リソース最適化のシートID
    folder_id = params.folder_id  # フォルダID

    # SmartsheetHandlerクラスのインスタンスを作成します。
    smartsheet_handler = SmartsheetHandler(api_key) # SmartsheetHandlerクラスのインスタンスを作成
    # read_data_from_sheetメソッドでプロジェクトとメンバーを読み込みます。
    projects = smartsheet_handler.read_projects_tasks_from_sheet(projects_tasks_sheet_id) # プロジェクトとタスクを読み込み
    members = smartsheet_handler.read_members_from_sheet(members_sheet_id) # メンバーを読み込み

    for set_name, param_set in params.parameter_sets.items(): # パラメータセット数分繰り返す

        # print(f"Running experiment with parameter set: {set_name}")
        mutation_params = param_set['mutation_params']  # 修正
        selection_params = params.selection_patterns[param_set['selection_type']]

        population_size = param_set['population_size']
        crossover_prob = param_set['crossover_prob']
        mutation_prob = param_set['mutation_prob']
        num_generations = param_set['num_generations']
        indpb = mutation_params['params']['indpb']
        crossover_params = params.crossover_patterns[param_set['crossover_type']]
        if 'indpb' in crossover_params['params']:
            crossover_params['params']['indpb'] = indpb  # indpbを設定
        objective_weights = param_set['objective_weights']
        constraint_weights = param_set['constraint_weights']
        crossover_type = param_set['crossover_type']
        mutation_type = param_set['mutation_type']
        selection_type = param_set['selection_type']
        scaling_factor_f2 = param_set['scaling_factor_f2']  # スケーリング係数を取得
        
        optimizer = Optimizer()  # 最適化クラスのインスタンスを作成
        
        for project in projects: # プロジェクト数分繰り返す
            optimizer.add_project(project) # 最適化クラスにプロジェクトを追加

        for member in members: # メンバー数分繰り返す
            optimizer.add_member(member) # 最適化クラスにメンバーを追加

        # パラメータをセット
        optimizer.set_optimization_parameters(
            population_size,
            crossover_prob,
            mutation_prob,
            num_generations,
            indpb,
            crossover_params,
            mutation_params,
            selection_params,
            objective_weights,
            constraint_weights,
            scaling_factor_f2
        )  # 最適化のパラメータを設定

        all_individuals_by_generation = optimizer.optimize()  # 最適化を実行
        
        # GAのパラメータを格納するリストにスケーリング係数を追加
        ga_parameters = [
            population_size, 
            num_generations, 
            crossover_prob, 
            crossover_type, 
            mutation_prob, 
            indpb, 
            mutation_type, 
            selection_type, 
            ','.join(map(str, objective_weights)), 
            ','.join(map(str, constraint_weights)),
            scaling_factor_f2  # スケーリング係数を追加
        ]

        # 最終世代のパレート最適解を取得
        last_generation_individuals = all_individuals_by_generation[-1]  # 最終世代の個体群を取得

        # 制約違反がない個体と、ある個体を分ける
        feasible_individuals = [ind for ind in last_generation_individuals if not any(ind.constraint_violations)]
        infeasible_individuals = [ind for ind in last_generation_individuals if any(ind.constraint_violations)]

        # トップを抽出する個体数を設定
        num_top_individuals = 5  # 例：トップ5を抽出したい場合

        # 制約違反がない個体を優先してトップを抽出
        top_individuals = sorted(feasible_individuals, key=lambda x: (x.fitness.values[0], x.fitness.values[1]))[:num_top_individuals]

        # 個体数に満たない場合は、制約違反がある個体から追加
        if len(top_individuals) < num_top_individuals:
            # 制約違反回数が少ないものを優先して追加
            sorted_infeasible_individuals = sorted(infeasible_individuals, key=lambda x: sum(len(violation) for violation in x.constraint_violations))
            top_individuals += sorted_infeasible_individuals[:(num_top_individuals - len(top_individuals))]

        best_solutions = []  # 最適解リスト
        for sol_idx, ind in enumerate(top_individuals):  # パレート最適解数分繰り返す
            solution = []  # タスク割り当てを格納するリスト
            task_idx = 0  # タスクのインデックス
            for project in optimizer.projects:  # プロジェクト数分繰り返す
                for task in project.tasks:  # タスク数分繰り返す
                    assigned_member = optimizer.members[ind[task_idx]]  # タスクに割り当てられたメンバーを取得
                    constraint_violations = ind.constraint_violations[task_idx]  # 制約違反情報を取得
                    task_assignment = TaskAssignment(project, task, assigned_member, sol_idx + 1, constraint_violations, ga_parameters) # タスク割り当てを作成
                    solution.append(task_assignment)  # タスク割り当てをリストに追加
                    task_idx += 1  # タスクのインデックスを更新
            best_solutions.append(solution)  # ベストな解をリストに追加

        all_best_solutions = [] # 全てのベストな解を格納するリスト
        for best_solution in best_solutions: # ベストな解数分繰り返す
            all_best_solutions.extend(best_solution) # ベストな解をリストに追加

        # best_solution に格納されているタスク割り当てを表示
        for idx, best_solution in enumerate(best_solutions): # ベストな解数分繰り返す
            print(f"Solution {idx + 1}:") # 解番号を表示
            for task_assignment in best_solution:  # タスク割り当て数分繰り返す
                task = task_assignment.task  # タスクを取得
                assigned_member = task_assignment.get_assigned_member()  # 割り当てられたメンバーを取得
                constraint_violations = task_assignment.constraint_violations  # 制約違反情報を取得
                project_id = task_assignment.project_id  # プロジェクトIDを取得
                project_name = task_assignment.project_name  # プロジェクト名を取得
                if assigned_member is not None:  # 割り当てられたメンバーが存在するか確認
                    print(f"Project: {project_name} (ID: {project_id}) -> Task: {task.name} (ID: {task.id}) -> Member: {assigned_member.name} (ID: {assigned_member.id}) -> Constraint Violations: {','.join(constraint_violations)}")  # 割り当てられたメンバーと制約違反情報を表示
                else:  # 割り当てられたメンバーが存在しない場合
                    print(f"Project: {project_name} (ID: {project_id}) -> Task: {task.name} (ID: {task.id}) -> Member: None -> Constraint Violations: {','.join(constraint_violations)}")  # 割り当てられたメンバーと制約違反情報を表示
            print("\n") # 改行

        # 実験ごとのディレクトリを作成
        experiment_dir = os.path.join(base_dir, set_name)
        os.makedirs(experiment_dir, exist_ok=True)
        csv_dir = os.path.join(experiment_dir, "csv") # CSV出力のファイル名を指定
        os.makedirs(csv_dir, exist_ok=True) # ディレクトリを作成
        images_dir = os.path.join(experiment_dir, "pareto_front_images") # 出力する画像を格納するフォルダを指定します。
        os.makedirs(images_dir, exist_ok=True) # ディレクトリを作成

        # CSV出力のファイル名を指定
        output_csv_file = os.path.join(csv_dir, "task_assignments.csv") # CSV出力のファイル名を指定
        summary_csv_file = os.path.join(summary_csv_dir, "summary_task_assignments.csv") # サマリーCSVのファイル名を指定

        # タスク割り当てをCSVファイルに出力
        for best_solution in best_solutions:  # ベストな解数分繰り返す
            for task_assignment in best_solution:  # タスク割り当て数分繰り返す
                task_assignment.to_csv(output_csv_file, set_name)  # タスク割り当てをCSVファイルに出力
                task_assignment.to_csv(summary_csv_file, set_name)  # タスク割り当てをサマリーCSVファイルに出力

        # 以下、violation_statistics.csv と violation_details.csv に対する同様の処理を行います。
        stat_csv_file = os.path.join(csv_dir, "violation_statistics.csv") # CSV出力のファイル名を指定
        details_csv_file = os.path.join(csv_dir, "violation_details.csv") # CSV出力のファイル名を指定
        summary_stat_csv_file = os.path.join(summary_csv_dir, "summary_violation_statistics.csv") # サマリーCSVのファイル名を指定
        summary_details_csv_file = os.path.join(summary_csv_dir, "summary_violation_details.csv") # サマリーCSVのファイル名を指定

        # 出力する世代の間隔を指定します。
        gen_interval = 10 # 画像を出力する世代の間隔を指定します。
        # ViolationWriterクラスのインスタンスを作成
        writer = ViolationWriter(all_individuals_by_generation, ga_parameters, params.timestamp_str)
        # 世代ごとの制約違反数をCSVファイルに出力
        writer.write_generation_stats(stat_csv_file, set_name)
        writer.write_generation_stats(summary_stat_csv_file, set_name)
        # 世代ごとの制約違反詳細をCSVファイルに出力
        writer.write_violation_details(details_csv_file, gen_interval, set_name)
        writer.write_violation_details(summary_details_csv_file, gen_interval, set_name)

        # オリジナルのシートをコピーして新しい名前を付ける
        new_sheet = smartsheet_handler.copy_and_rename_sheet(resource_optimizer_sheet_id, set_name, folder_id)
        # 新しいシートIDを取得
        new_sheet_id = new_sheet.id
        # 新しいシートにデータを書き込む
        smartsheet_handler.write_data_to_sheet(new_sheet_id, all_best_solutions)  # タスク割り当てをシートに書き込み

        output_dir = images_dir # 出力する画像を格納するフォルダを指定します。
        gen_interval = 10 # 画像を出力する世代の間隔を指定します。
        max_individuals = 100 # 画像に出力する最大個体数を指定します。
        plotter = ParetoPlotter(gen_interval, max_individuals) # ParetoPlotterクラスのインスタンスを作成します。
        plotter.plot_pareto_front_and_violations(output_dir, all_individuals_by_generation, set_name) # パレート解のプロット
        # plotter.plot_all_generations_pareto_front(output_dir, all_individuals_by_generation, gen_interval, set_name)  # パレート解のプロット
        plotter.plot_all_generations_pareto_front(output_dir, all_individuals_by_generation, gen_interval, set_name, summary_csv_dir)


if __name__ == "__main__": # メイン関数を実行
    main() # メイン関数を実行