import csv # CSVファイルを読み書きするためのライブラリ
from collections import Counter # リストの要素をカウントするためのライブラリ

class ViolationWriter: # 制約違反の詳細をCSVに出力するクラス
    def __init__(self, all_individuals_by_generation, ga_parameters, timestamp):  # コンストラクタ
        self.all_individuals_by_generation = all_individuals_by_generation  # 世代ごとの個体を格納したリスト
        self.ga_parameters = ga_parameters  # GAのパラメータを格納したオブジェクト
        self.timestamp = timestamp  # 日時情報の追加

    def write_violation_details(self, filename_violation_details, gen_interval, set_name): # 世代ごとの制約違反詳細をCSVに出力
        # ファイルが存在しないか、空の場合にヘッダーを書き込む
        try:
            with open(filename_violation_details, 'r', newline="", encoding="utf-8") as f:
                if f.readable() and f.readline().strip() == "":
                    write_header = True
                else:
                    write_header = False
        except FileNotFoundError:
            write_header = True

        with open(filename_violation_details, "a", newline="", encoding="utf-8") as f:
            csv_writer = csv.writer(f)
            if write_header:
                csv_writer.writerow(["Timestamp", "Parameter_Set", "Generation", "Individual", "Violation_Count_C1", "Violation_Count_C2", "Violation_Count_C3", "Objective1_Post_Penalty", "Objective2_Post_Penalty", "Objective1_Pre_Penalty", "Objective2_Pre_Penalty", "Hypervolume",
                                    "Population_Size", "Num_Generations", "Crossover_Prob", "Crossover_Type", "Mutation_Prob", "Indpb", "Mutation_Type", "Selection_Type", "Objective_Weights", "Constraint_Weights", "Scaling_Factor_F2"])  # ヘッダーを修正

        total_generations = len(self.all_individuals_by_generation)
        for generation_idx, generation in enumerate(self.all_individuals_by_generation):
            if generation_idx == 0 or generation_idx == total_generations - 1 or (generation_idx + 1) % gen_interval == 0:
                for individual_idx, individual in enumerate(generation):
                    violations = Counter(violation for violation_list in individual.constraint_violations for violation in violation_list)
                    with open(filename_violation_details, "a", newline="", encoding="utf-8") as f:
                        csv_writer = csv.writer(f)
                        csv_writer.writerow([self.timestamp, set_name, generation_idx + 1, individual_idx + 1, violations['C1'], violations['C2'], violations['C3'], individual.fitness.values[0], individual.fitness.values[1], individual.original_objective_values[0], individual.original_objective_values[1], individual.hypervolume] + self.ga_parameters)

    def write_generation_stats(self, filename_generation_stats, set_name): # 世代ごとの制約違反数をCSVに出力
        # ファイルが存在しないか、空の場合にヘッダーを書き込む
        try:
            with open(filename_generation_stats, 'r', newline="", encoding="utf-8") as f:
                if f.readable() and f.readline().strip() == "":
                    write_header = True
                else:
                    write_header = False
        except FileNotFoundError:
            write_header = True

        with open(filename_generation_stats, "a", newline="", encoding="utf-8") as f:
            csv_writer = csv.writer(f)
            if write_header:
                csv_writer.writerow(["Timestamp", "Parameter_Set", "Generation", 
                                    "Total_Violations_C1_Generation", "Total_Violations_C2_Generation", "Total_Violations_C3_Generation", 
                                    "Average_Violations_C1_Generation", "Average_Violations_C2_Generation", "Average_Violations_C3_Generation",
                                    "Total_Penalty_C1_Generation", "Total_Penalty_C2_Generation", "Total_Penalty_C3_Generation",
                                    "Average_Penalty_C1_Individual", "Average_Penalty_C2_Individual", "Average_Penalty_C3_Individual", 
                                    "Feasible_Solutions", "Total_Objective1_Generation", "Total_Objective2_Generation", 
                                    "Average_Objective1_Individual", "Average_Objective2_Individual", "Average_Objective1_Pre_Penalty_Individual", "Average_Objective2_Pre_Penalty_Individual", "Hypervolume",
                                    "Population_Size", "Num_Generations", "Crossover_Prob", "Crossover_Type", "Mutation_Prob", "Indpb", "Mutation_Type", "Selection_Type", "Objective_Weights", "Constraint_Weights","Scaling_Factor_F2"])

        # 世代ごとの制約違反とペナルティの統計情報を計算し、CSVに出力
        for generation_idx, generation in enumerate(self.all_individuals_by_generation): # 世代ごとにループ
            # 各種初期化
            total_violations = Counter({'C1': 0, 'C2': 0, 'C3': 0}) # 制約違反回数をカウント
            total_penalties = [0.0, 0.0, 0.0] # ペナルティの合計
            count_penalties = [0, 0, 0] # ペナルティの個数
            # 実行可能解の数をカウント
            feasible_solutions = sum(1 for individual in generation if not any(individual.constraint_violations)) # 実行可能解の数をカウント

            # 個体ごとに制約違反とペナルティを集計
            for individual in generation: # 個体ごとにループ
                violations = individual.constraint_violations # 制約違反を取得
                penalties = individual.constraint_penalties # ペナルティを取得
                for v_list, p_list in zip(violations, penalties): # 制約違反とペナルティをループ
                    for v, p in zip(v_list, p_list): # 制約違反とペナルティをループ
                        if v == 'C1': # 制約違反がC1の場合
                            total_violations['C1'] += 1 # 制約違反回数をカウント
                            total_penalties[0] += p # ペナルティを合計
                            count_penalties[0] += 1 # ペナルティの個数をカウント
                        elif v == 'C2': # 制約違反がC2の場合
                            total_violations['C2'] += 1 # 制約違反回数をカウント
                            total_penalties[1] += p # ペナルティを合計
                            count_penalties[1] += 1 # ペナルティの個数をカウント
                        elif v == 'C3': # 制約違反がC3の場合
                            total_violations['C3'] += 1 # 制約違反回数をカウント
                            total_penalties[2] += p # ペナルティを合計
                            count_penalties[2] += 1 # ペナルティの個数をカウント

            # 目的関数の合計を計算
            total_objective1 = sum(individual.fitness.values[0] for individual in generation) # 目的関数1の合計を計算
            total_objective2 = sum(individual.fitness.values[1] for individual in generation) # 目的関数2の合計を計算
            # 目的関数の平均を計算
            average_objective1 = total_objective1 / len(generation) if len(generation) != 0 else 0.0 # 目的関数1の平均を計算
            average_objective2 = total_objective2 / len(generation) if len(generation) != 0 else 0.0 # 目的関数2の平均を計算
            # オリジナルの目的関数値（ペナルティ加算前）の合計と平均を計算
            total_objective1_pre_penalty = sum(individual.original_objective_values[0] for individual in generation if hasattr(individual, 'original_objective_values'))
            total_objective2_pre_penalty = sum(individual.original_objective_values[1] for individual in generation if hasattr(individual, 'original_objective_values'))
            average_objective1_pre_penalty = total_objective1_pre_penalty / len(generation) if generation else 0.0
            average_objective2_pre_penalty = total_objective2_pre_penalty / len(generation) if generation else 0.0
            # ハイパーボリュームを計算
            hypervolume = generation[0].hypervolume if generation else 0.0

            # 平均ペナルティと違反回数の計算
            avg_penalties = [total_penalties[i] / count_penalties[i] if count_penalties[i] != 0 else 0.0 for i in range(3)] # 平均ペナルティを計算
            avg_violations = [total_violations['C1'] / len(generation), total_violations['C2'] / len(generation), total_violations['C3'] / len(generation)] # 平均違反回数を計算

            # 統計情報をターミナルに表示
            print(f"Generation: {generation_idx+1}")  # 世代数を表示
            print(f"Feasible Solutions: {feasible_solutions}")  # 実行可能解の数を表示
            print(f"Total Violations per Generation - C1: {total_violations['C1']}, C2: {total_violations['C2']}, C3: {total_violations['C3']}")  # 制約違反数を表示
            print(f"Average Violations per Generation - C1: {avg_violations[0]}, C2: {avg_violations[1]}, C3: {avg_violations[2]}")  # 平均違反回数を表示
            print(f"Total Penalty per Generation - C1: {total_penalties[0]}, C2: {total_penalties[1]}, C3: {total_penalties[2]}")  # ペナルティを表示
            print(f"Average Penalty per Individual - C1: {avg_penalties[0]}, C2: {avg_penalties[1]}, C3: {avg_penalties[2]}\n")  # 平均ペナルティを表示

            with open(filename_generation_stats, "a", newline="", encoding="utf-8") as f:
                csv_writer = csv.writer(f)
                csv_writer.writerow([self.timestamp, set_name, generation_idx+1, 
                        total_violations['C1'], total_violations['C2'], total_violations['C3'], 
                        avg_violations[0], avg_violations[1], avg_violations[2],
                        total_penalties[0], total_penalties[1], total_penalties[2],
                        avg_penalties[0], avg_penalties[1], avg_penalties[2],
                        feasible_solutions, total_objective1, total_objective2, 
                        average_objective1, average_objective2, average_objective1_pre_penalty, average_objective2_pre_penalty, hypervolume] + self.ga_parameters)