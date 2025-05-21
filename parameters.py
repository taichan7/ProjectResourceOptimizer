from deap import tools
from itertools import product
import datetime # datetimeモジュールをインポート
import os  # osモジュールをインポート
import os
from dotenv import load_dotenv

class Parameters:
    def __init__(self):
        # .envファイルから環境変数を読み込む
        load_dotenv()

        # 現在の日時を取得してタイムスタンプを作成
        now = datetime.datetime.now()
        self.timestamp_str = now.strftime("%Y%m%d_%H%M%S")

        # プロジェクト情報をまとめる
        self.projects_info = {
            'project1': {
                'projects_tasks_sheet_id': os.getenv("PROJECT1_PROJECTS_TASKS_SHEET_ID", ""),
                'members_sheet_id': os.getenv("PROJECT1_MEMBERS_SHEET_ID", ""),
                'resource_optimizer_sheet_id': os.getenv("PROJECT1_RESOURCE_OPTIMIZER_SHEET_ID", ""),
                'folder_id': os.getenv("PROJECT1_FOLDER_ID", "")  # フォルダID
            },
            'project2': {
                'projects_tasks_sheet_id': os.getenv("PROJECT2_PROJECTS_TASKS_SHEET_ID", ""),
                'members_sheet_id': os.getenv("PROJECT2_MEMBERS_SHEET_ID", ""),
                'resource_optimizer_sheet_id': os.getenv("PROJECT2_RESOURCE_OPTIMIZER_SHEET_ID", ""),
                'folder_id': os.getenv("PROJECT2_FOLDER_ID", "")  # フォルダID
            },
            'project3': {
                'projects_tasks_sheet_id': os.getenv("PROJECT3_PROJECTS_TASKS_SHEET_ID", ""),
                'members_sheet_id': os.getenv("PROJECT3_MEMBERS_SHEET_ID", ""),
                'resource_optimizer_sheet_id': os.getenv("PROJECT3_RESOURCE_OPTIMIZER_SHEET_ID", ""),
                'folder_id': os.getenv("PROJECT3_FOLDER_ID", "")  # フォルダID
            },
            'project4': {
                'projects_tasks_sheet_id': os.getenv("PROJECT4_PROJECTS_TASKS_SHEET_ID", ""),
                'members_sheet_id': os.getenv("PROJECT4_MEMBERS_SHEET_ID", ""),
                'resource_optimizer_sheet_id': os.getenv("PROJECT4_RESOURCE_OPTIMIZER_SHEET_ID", ""),
                'folder_id': os.getenv("PROJECT4_FOLDER_ID", "")  # フォルダID
            }
        }

        # 選択するプロジェクト
        selected_project = os.getenv("SELECTED_PROJECT", "project4")

        # APIキーとシートIDを設定
        self.api_key = os.getenv("SMARTSHEET_API_KEY", "")
        self.projects_tasks_sheet_id = self.projects_info[selected_project]['projects_tasks_sheet_id']
        self.members_sheet_id = self.projects_info[selected_project]['members_sheet_id']
        self.resource_optimizer_sheet_id = self.projects_info[selected_project]['resource_optimizer_sheet_id']
        self.folder_id = self.projects_info[selected_project]['folder_id']  # フォルダIDを設定

        # 固定のパラメータを設定
        self.mutation_type = 'mutShuffleIndexes' # 突然変異のパターン
        self.selection_type = 'selNSGA2' # 選択のパターン

        # 交叉、突然変異、選択のパターンを定義
        self.crossover_patterns = {
            'cxOnePoint': {'func': tools.cxOnePoint, 'params': {}},
            'cxTwoPoint': {'func': tools.cxTwoPoint, 'params': {}},
            'cxUniform': {'func': tools.cxUniform, 'params': {'indpb': None}},  # indpbを追加
        }

        self.mutation_patterns = {
            'mutShuffleIndexes': {'func': tools.mutShuffleIndexes, 'params': {'indpb': None}},
            # 他の突然変異のパターンもここに追加できます。
        }

        self.selection_patterns = {
            'selNSGA2': {'func': tools.selNSGA2, 'params': {}},
        }

        # パラメータ範囲の設定
        # indpb_values = [0.05, 0.1] # 突然変異の確率
        indpb_values = [0.1] # 突然変異の確率
        # population_sizes = [100, 200] # 集団のサイズ
        population_sizes = [100] # 集団のサイズ
        # crossover_probs = [0.6, 0.8, 1.0] # 交叉の確率
        crossover_probs = [1.0] # 交叉の確率
        # mutation_probs = [0.6, 0.8, 1.0] # 突然変異の確率
        mutation_probs = [1.0] # 突然変異の確率
        num_generations = [300] # 世代数
        # crossover_types = ['cxOnePoint', 'cxTwoPoint', 'cxUniform'] # 交叉のパターン
        crossover_types = ['cxUniform'] # 交叉のパターン
        objective_weights_values = [(-1.0, -1.0)]  # 目的関数の重み
        scaling_factor_f2_values = [3000, 4000, 5000]  # 目的関数2のスケーリング係数
        constraint_weights_values = [
            (1, 10, 100),
            (10, 100, 1000),
            (10, 200, 500),
            (10, 20, 30),
            (1, 100, 10),
            (10, 1000, 100),
            (10, 500, 200),
            (10, 30, 20),
            (10, 1, 100),
            (100, 10, 1000),
            (200, 10, 500),
            (20, 10, 30),
            (100, 1, 10),
            (1000, 10, 100),
            (500, 10, 200),
            (30, 10, 20),
            (10, 100, 1),
            (100, 1000, 10),
            (200, 500, 10),
            (20, 30, 10),
            (100, 10, 1),
            (1000, 100, 10),
            (500, 200, 10),
            (30, 20, 10)
        ]
        # パラメータセットの生成
        self.parameter_sets = {
            f"{self.timestamp_str}_exp{count:03d}_pop{pop_size}_cxp{cx_prob}_mup{mut_prob}_gen{n_gen}_{cx_type}_indpb{indpb}_objw{objw}_consw{consw}_scale{scale}": {
                "population_size": pop_size,
                "crossover_prob": cx_prob,
                "mutation_prob": mut_prob,
                "num_generations": n_gen,
                "crossover_type": cx_type,
                "mutation_type": self.mutation_type,
                "selection_type": self.selection_type,
                "mutation_params": {
                    "func": self.mutation_patterns[self.mutation_type]['func'],
                    "params": {
                        "indpb": indpb
                    }
                },
                "objective_weights": objw,
                "constraint_weights": consw,
                "scaling_factor_f2": scale  # スケーリング係数をパラメータセットに追加
            }
            for count, (pop_size, cx_prob, mut_prob, n_gen, cx_type, indpb, objw, consw, scale) in 
            enumerate(product(population_sizes, crossover_probs, mutation_probs, num_generations, crossover_types, indpb_values, objective_weights_values, constraint_weights_values, scaling_factor_f2_values), 1)
        }