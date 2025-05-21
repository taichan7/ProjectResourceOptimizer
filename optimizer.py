from deap import base, creator, tools # DEAPをインポート
import numpy as np # NumPyをインポート
import random # randomをインポート
import copy # copyをインポート
from objective_functions import ObjectiveFunctions # 目的関数クラスをインポート
from constraint_functions import ConstraintFunctions # 制約条件クラスをインポート
# deapモジュールからhypervolumeをインポート
from deap.tools._hypervolume import hv # hypervolumeをインポート

class Optimizer: # 最適化クラス
    def __init__(self): # コンストラクタ
        self.projects = [] # プロジェクトリスト
        self.members = [] # メンバーリスト
        self.tasks = []  # タスクリストを追加
        self.objective_weights = [] # 目的関数の重み
        self.constraint_weights = [] # 制約条件の重み
        self.population_size = None # 集団の大きさ
        self.crossover_prob = None # 交叉の確率
        self.mutation_prob = None # 突然変異の確率
        self.num_generations = None # 世代数
        self.indpb = None # 突然変異の確率
        self.crossover_params = None # 交叉関数のパラメータ
        self.mutation_params = None  # 突然変異関数のパラメータ
        self.selection_params = None  # 選択関数のパラメータ

    def add_project(self, project): # プロジェクトを追加するメソッド
        self.projects.append(project) # 追加
        for task in project.tasks: # タスクを一つずつ取り出す
            self.tasks.append(task)  # 各プロジェクトのタスクを追加

    def remove_project(self, project):  # プロジェクトを削除するメソッド
        for task in project.tasks: # タスクを一つずつ取り出す
            self.tasks.remove(task)  # 関連するタスクを削除
        self.projects.remove(project)  # プロジェクトを削除

    def get_projects(self): # プロジェクトを取得するメソッド
        return self.projects # プロジェクトを返す

    def add_member(self, member): # メンバーを追加するメソッド
        self.members.append(member) # 追加

    def remove_member(self, member): # メンバーを削除するメソッド
        self.members.remove(member) # 削除

    def get_members(self): # メンバーを取得するメソッド
        return self.members # メンバーを返す

    def set_optimization_parameters(self, population_size, crossover_prob, mutation_prob, num_generations, indpb, crossover_params, mutation_params, selection_params, objective_weights, constraint_weights, scaling_factor_f2):  # 最適化のためのパラメータを設定するメソッド
        self.population_size = population_size # 集団の大きさ
        self.crossover_prob = crossover_prob # 交叉の確率
        self.mutation_prob = mutation_prob # 突然変異の確率
        self.num_generations = num_generations # 世代数
        self.indpb = indpb # 突然変異の確率
        self.crossover_params = crossover_params # 交叉関数のパラメータ
        self.mutation_params = mutation_params  # 突然変異関数のパラメータ
        self.selection_params = selection_params  # 選択関数のパラメータ
        self.objective_weights = objective_weights # 目的関数の重み
        self.constraint_weights = constraint_weights # 制約条件の重み
        self.scaling_factor_f2 = scaling_factor_f2  # 目的関数2のスケーリング係数

    def evaluate_fitness(self, individual):  # 目的関数を評価するメソッド
        # print(f"Individual: ", individual)
        objective_functions = ObjectiveFunctions(self.tasks, self.members, individual) # 目的関数を作成
        f1 = objective_functions.f1() # 目的関数1を計算
        f2 = objective_functions.f2() # 目的関数2を計算

        # individualに目的関数のペナルティ加算前の値を保存
        individual.original_objective_values = (f1, f2)

        constraint_functions = ConstraintFunctions(self.tasks, self.members, self.constraint_weights, individual) # 制約条件を作成
        penalty = constraint_functions.apply_constraints()  # 制約条件を適用

        return (f1 + penalty, f2 * self.scaling_factor_f2 + penalty) # 目的関数の値を返す


    def optimize(self):  # 最適化を実行するメソッド
        creator.create("FitnessMulti", base.Fitness, weights=self.objective_weights) # 目的関数の重みを設定
        creator.create("Individual", list, fitness=creator.FitnessMulti, constraint_violations=None) # 個体を作成

        toolbox = base.Toolbox() # ツールボックスを作成
        toolbox.register("attr_int", random.randint, 0, len(self.members) - 1) # 0からメンバー数-1までの整数をランダムに返す関数を登録
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_int, len(self.tasks)) # 個体を作成
        # toolbox.register("individual", self.create_individual_constrained)  # 制約を満たす個体を生成する関数を登録
        toolbox.register("population", tools.initRepeat, list, toolbox.individual) # 集団を作成
        toolbox.register("mate", self.crossover_params['func'], **self.crossover_params['params']) # 交叉を実行する関数を登録
        toolbox.register("mutate", self.mutation_params['func'], **self.mutation_params['params'])  # 突然変異を実行する関数を登録
        # toolbox.register("mutate", self.mutate_constrained)  # 突然変異を実行する関数を登録
        toolbox.register("select", self.selection_params['func'], **self.selection_params['params'])  # 選択を実行する関数を登録
        toolbox.register("evaluate", self.evaluate_fitness) # 目的関数を評価する関数を登録

        history = tools.History() # 履歴を保存するオブジェクトを作成
        toolbox.decorate("mate", history.decorator) # 交叉を実行する関数に履歴を保存するデコレーターを追加
        toolbox.decorate("mutate", history.decorator) # 突然変異を実行する関数に履歴を保存するデコレーターを追加
        toolbox.decorate("select", history.decorator) # 選択を実行する関数に履歴を保存するデコレーターを追加

        # 統計情報を収集するためのオブジェクトを作成
        stats = tools.Statistics(lambda ind: ind.fitness.values) # 集団の各個体の目的関数を取得
        stats.register("min", np.min, axis=0) # 集団の各目的関数の最小値を取得
        stats.register("max", np.max, axis=0) # 集団の各目的関数の最大値を取得
        stats.register("avg", np.mean, axis=0) # 集団の各目的関数の平均値を取得

        population = toolbox.population(n=self.population_size)  # 集団を作成
        history.update(population)  # 初期集団の情報を記録  

        # 適応度の評価
        fitnesses = list(map(toolbox.evaluate, population)) # 各個体の適応度を評価
        for ind, fit in zip(population, fitnesses): # 各個体の適応度を設定
            ind.fitness.values = fit # 各個体の適応度を設定

        logbook = tools.Logbook() # ログブックを作成
        logbook.header = ['gen', 'evals'] + stats.fields # ログブックのヘッダーを設定

        all_individuals_by_generation = []  # 各世代の個体のリストを格納するリスト
        for gen in range(self.num_generations): # 世代数分繰り返す
            tools.emo.assignCrowdingDist(population) # 集団の個体にクラウディング距離を設定
            offspring = tools.selTournamentDCD(population, len(population))  # 子個体の生成での選択を実行
            # offspring = toolbox.select(population, len(population)) # 選択を実行
            offspring = [toolbox.clone(ind) for ind in offspring]  # 親個体から子個体を生成

            for child1, child2 in zip(offspring[::2], offspring[1::2]): # 2個体ずつ取り出す
                if random.random() < self.crossover_prob: # 交叉を実行
                    toolbox.mate(child1, child2) # 交叉を実行
                    del child1.fitness.values # 適応度を削除
                    del child2.fitness.values # 適応度を削除

            for mutant in offspring: # 突然変異を実行
                if random.random() < self.mutation_prob: # 突然変異を実行
                    toolbox.mutate(mutant)  # 突然変異を実行
                    del mutant.fitness.values # 適応度を削除

            invalid_ind = [ind for ind in offspring if not ind.fitness.valid] # 適応度が未設定の個体を取得
            fitnesses = map(toolbox.evaluate, invalid_ind) # 適応度を評価
            for ind, fit in zip(invalid_ind, fitnesses): # 各個体の適応度を設定
                ind.fitness.values = fit # 各個体の適応度を設定

            # tools.emo.assignCrowdingDist(population + offspring) # 集団と子個体のクラウディング距離を設定
            # population = tools.selTournamentDCD(population + offspring, len(population)) # 子個体の生成での選択を実行
            population = toolbox.select(population + offspring, len(population))  # 次世代の作成での選択を実行
            history.update(population)  # 更新された集団の情報を記録

            # 統計情報の更新
            record = stats.compile(population) # 統計情報を計算
            logbook.record(gen=gen, **record) # 記録
            print(f"Logbook: {logbook.stream}") # ログブックを表示

            # ハイパーボリュームの計算（追加部分）
            pareto_front = tools.sortNondominated(population, len(population), first_front_only=True)[0] # パレート最適解を取得
            if pareto_front: # パレート最適解が存在する場合
                max_objectives = [max(ind.fitness.values[i] for ind in pareto_front) for i in range(len(self.objective_weights))] # パレート最適解の各目的関数の最大値を取得
                reference_point = [1.1 * max_val for max_val in max_objectives] # 参照点を設定
                front_matrix = [ind.fitness.values for ind in pareto_front] # パレート最適解の目的関数の値を取得
                hypervolume = hv.hypervolume(front_matrix, reference_point) # ハイパーボリュームを計算

                # 各個体にハイパーボリュームを属性として追加
                for ind in population: # 集団の個体をループ
                    ind.hypervolume = hypervolume # ハイパーボリュームを属性として追加

            all_individuals_by_generation.append(copy.deepcopy(population)) # 各世代の個体を格納するリストに追加

        return all_individuals_by_generation  # 各世代のパレート最適個体のリストを返す