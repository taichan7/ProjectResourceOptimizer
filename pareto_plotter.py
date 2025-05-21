import os # ファイルパスを扱うためのモジュール
from matplotlib.colors import ListedColormap, BoundaryNorm # グラフの色を指定するためのモジュール
import matplotlib.pyplot as plt # グラフを描画するためのモジュール
import matplotlib.patches as mpatches # グラフの凡例を作成するためのモジュール
import numpy as np # 数値計算を行うためのモジュール
import imageio # 画像を扱うためのモジュール

class ParetoPlotter: # ParetoPlotterクラスの定義
    def __init__(self, gen_interval, max_individuals): # ParetoPlotterクラスのコンストラクタ
        self.gen_interval = gen_interval # 世代間隔
        self.max_individuals = max_individuals # 最大個体数
        self.violation_markers = {
            "C1": {"marker": "o", "color": "red"},
            "C2": {"marker": "^", "color": "blue"},
            "C3": {"marker": "v", "color": "green"},
        } # 制約違反を示すマーカーと色の辞書

    def identify_pareto_front(self, individuals): # パレートフロントを識別するメソッド
        pareto_front = [] # パレートフロント
        for ind1 in individuals: # 個体ind1について
            is_dominated = False # 個体ind1が他の個体に支配されているかどうか
            for ind2 in individuals: # 個体ind2について
                if ind2.fitness.dominates(ind1.fitness): # 個体ind2が個体ind1に支配されている場合
                    is_dominated = True # 個体ind1は他の個体に支配されている
                    break # 個体ind1は他の個体に支配されているので、ループを抜ける
            if not is_dominated: # 個体ind1が他の個体に支配されていない場合
                pareto_front.append(ind1) # 個体ind1をパレートフロントに追加
        return pareto_front # パレートフロントを返す

    def update_plot(self, gen, individuals, ax): # グラフを更新するメソッド
        plt.clf() # グラフをクリア
        ax = plt.gca() # グラフの軸を取得

        # 異なる違反を示すマーカーと色の凡例を作成
        patches = [mpatches.Patch(color=self.violation_markers[vio_type]["color"], 
                                label=f'Constraint {vio_type}') for vio_type in self.violation_markers.keys()] # 制約違反を示すマーカーと色の凡例を作成
        # 制約違反なしの個体を示す凡例を追加
        patches.append(mpatches.Patch(color='silver', label='No violation')) # 制約違反なしの個体を示す凡例を追加
        patches.append(mpatches.Patch(color='gold', label='No violation & Pareto front')) # 制約違反なしでパレートフロントの個体を示す凡例を追加
        # 凡例をグラフに追加
        plt.legend(handles=patches) # 凡例をグラフに追加

        plt.xlabel("Objective 1 (Total Cost)")  # x軸のラベル（目的関数1に対応）
        plt.ylabel("Objective 2 (Std. Dev. of Labor)")  # y軸のラベル（目的関数2に対応）
        plt.title(f"Pareto Front and Constraint Violations (Generation {gen + 1})")  # グラフのタイトル

        # 先ず、制約条件に違反しない個体（実行可能解）と違反する個体を分離
        feasible_individuals = [ind for ind in individuals if ind.constraint_violations is None or not any(ind.constraint_violations)] # 実行可能解
        infeasible_individuals = [ind for ind in individuals if ind not in feasible_individuals] # 制約違反

        # 実行可能解を目的関数の値が最小となるものからソート
        feasible_individuals_sorted = sorted(feasible_individuals, key=lambda x: (x.fitness.values[0], x.fitness.values[1])) # 実行可能解を目的関数の値が最小となるものからソート

        # 実行可能解が不足している場合、制約違反の個体を追加する
        if len(feasible_individuals_sorted) < self.max_individuals: # 実行可能解が不足している場合
            infeasible_individuals_sorted = sorted(infeasible_individuals, key=lambda x: (x.fitness.values[0], x.fitness.values[1])) # 制約違反の個体を目的関数の値が最小となるものからソート
            feasible_individuals_sorted.extend(infeasible_individuals_sorted) # 制約違反の個体を追加

        # ソートされたリストから上位の個体を選択
        individuals_sampled = feasible_individuals_sorted[:min(self.max_individuals, len(feasible_individuals_sorted))] # ソートされたリストから上位の個体を選択

        pareto_front_individuals = self.identify_pareto_front(feasible_individuals_sorted) # パレートフロントを識別

        # if pareto_front_individuals: # パレートフロントが存在する場合
        #     # pareto_front_points = np.array([ind.fitness.values for ind in pareto_front_individuals]) # パレートフロントの目的関数の値を取得
        #     pareto_front_points = np.array([ind.original_objective_values for ind in pareto_front_individuals])  # パレートフロントのペナルティ加算前の目的関数の値を取得
        #     ax.plot(pareto_front_points[:, 0], pareto_front_points[:, 1], 'k-') # パレートフロントをグラフに追加

        for ind in individuals_sampled: # 個体indについて
            unique_violations = set()  # 一意の制約違反を格納するセット（この行を移動）
            if ind.constraint_violations is not None and any(ind.constraint_violations): # 制約違反が存在する場合
                for task_violations in ind.constraint_violations: # 個体indの制約違反をループ
                    if task_violations: # 制約違反が存在する場合
                        for violation in task_violations:   # Loop over the individual violations
                            if violation in self.violation_markers: # 制約違反の種類が存在する場合
                                if violation not in unique_violations:  # 制約違反が一意な場合
                                    ax.scatter(ind.original_objective_values[0], ind.original_objective_values[1], **self.violation_markers[violation]) # 制約違反を示すマーカーをグラフに追加
                                    unique_violations.add(violation)  # 制約違反をセットに追加
            elif ind in pareto_front_individuals: # パレートフロントの個体の場合
                ax.scatter(ind.original_objective_values[0], ind.original_objective_values[1], marker='o', color='gold', edgecolors='black', s=100)  # Pareto front and feasible
            else: # 制約違反が存在しない場合
                ax.scatter(ind.original_objective_values[0], ind.original_objective_values[1], marker='o', color='silver')  # Feasible but not on Pareto front

    def plot_pareto_front_and_violations(self, output_dir, all_individuals_by_generation, experiment_name): # パレートフロントと制約違反をグラフに描画
        if not os.path.exists(output_dir): # 出力先のディレクトリが存在しない場合
            os.makedirs(output_dir) # ディレクトリを作成

        plt.style.use("seaborn-darkgrid") # グラフのスタイルを指定

        # all_fitness_values = [ind.fitness.values for individuals in all_individuals_by_generation for ind in individuals] # 全ての個体の目的関数の値を取得
        all_fitness_values = [ind.original_objective_values for individuals in all_individuals_by_generation for ind in individuals]  # 全ての個体のペナルティ加算前の目的関数の値を取得

        all_x_values = [x for x, y in all_fitness_values] # 目的関数1の値を取得
        all_y_values = [y for x, y in all_fitness_values] # 目的関数2の値を取得
        x_min, x_max = min(all_x_values), max(all_x_values) # 目的関数1の最小値と最大値を取得
        y_min, y_max = min(all_y_values), max(all_y_values) # 目的関数2の最小値と最大値を取得

        fig = plt.figure() # グラフを作成
        ax = plt.gca() # グラフの軸を取得

        for gen, individuals in enumerate(all_individuals_by_generation): # 各世代について
            if gen % self.gen_interval == 0 or gen == 0 or gen == len(all_individuals_by_generation) - 1: # 世代数がgen_intervalの倍数の場合、最初の世代、最後の世代の場合
                self.update_plot(gen, individuals, ax) # グラフを更新
                plt.text(0.5, 1.08, experiment_name, ha='center', va='bottom', transform=ax.transAxes, fontsize=7) # グラフの上部に実験名を表示
                plt.xlim(x_min, x_max) # x軸の範囲を指定
                plt.ylim(y_min, y_max) # y軸の範囲を指定
                padded_gen_str = "{:03}".format(gen + 1)  # 世代数を3桁の数字に変換
                plt.savefig(os.path.join(output_dir, f"pareto_front_and_violations_gen_{padded_gen_str}.png")) # グラフを画像として保存

        plt.close() # グラフを閉じる

        # GIFを作成するための画像ファイル名を取得
        image_files = sorted([img for img in os.listdir(output_dir) if img.startswith("pareto_front_and_violations_gen_")]) # 画像ファイル名を取得

        # GIFファイルのパスを指定
        gif_output_path = os.path.join(output_dir, 'pareto_front_and_violations.gif') # GIFファイルのパスを指定

        # 画像ファイルからGIFを作成
        with imageio.get_writer(gif_output_path, mode='I', duration=1000.0, loop=0) as writer:  # durationとloopパラメータを追加
            for filename in image_files: # 画像ファイルをループ
                image_path = os.path.join(output_dir, filename) # 画像ファイルのパスを取得
                image = imageio.imread(image_path) # 画像ファイルを読み込み
                writer.append_data(image) # GIFに画像を追加

    def plot_all_generations_pareto_front(self, output_dir, all_individuals_by_generation, gen_interval, experiment_name, summary_csv_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        plt.style.use("seaborn-darkgrid")

        all_fitness_values = [ind.original_objective_values for individuals in all_individuals_by_generation for ind in individuals]
        all_x_values = [x for x, y in all_fitness_values]
        all_y_values = [y for x, y in all_fitness_values]
        x_min, x_max = min(all_x_values), max(all_x_values)
        y_min, y_max = min(all_y_values), max(all_y_values)

        fig, ax = plt.subplots()

        cmap = plt.get_cmap('viridis')
        num_gen = len(all_individuals_by_generation)

        # 修正部分: ビンのサイズを適切に調整
        if num_gen > cmap.N:
            bin_size = int(np.ceil(num_gen / cmap.N))
            bins = np.arange(0, num_gen + bin_size, bin_size)
        else:
            bins = np.arange(0, num_gen + 1)

        norm = BoundaryNorm(bins, cmap.N)

        # for gen, individuals in enumerate(all_individuals_by_generation):
        #     if gen % gen_interval == 0 or gen == 0 or gen == num_gen - 1:
        #         pareto_front_individuals = self.identify_pareto_front(individuals)
        #         if pareto_front_individuals:
        #             pareto_front_points = np.array([ind.original_objective_values for ind in pareto_front_individuals])
        #             ax.scatter(pareto_front_points[:, 0], pareto_front_points[:, 1], color=cmap(norm(gen)))

        for gen, individuals in enumerate(all_individuals_by_generation):
            if gen % gen_interval == 0 or gen == 0 or gen == num_gen - 1:
                # パレートフロントの識別は行わず、各世代の全個体をプロット
                points = np.array([ind.original_objective_values for ind in individuals])
                ax.scatter(points[:, 0], points[:, 1], color=cmap(norm(gen)))

        plt.xlim(x_min, x_max)
        plt.ylim(y_min, y_max)
        plt.xlabel("Objective 1 (Total Cost)")
        plt.ylabel("Objective 2 (Std. Dev. of Labor)")
        plt.title("Pareto Front for all generations")
        plt.text(0.6, 1.08, experiment_name, ha='center', va='bottom', transform=ax.transAxes, fontsize=7) # グラフの上部に実験名を表示

        # グラデーションの棒を修正
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ticks=np.linspace(0, num_gen, min(6, cmap.N)), boundaries=np.arange(-0.5, num_gen + 1.5), format='%1i')
        cbar.set_label('Generation')

        plt.savefig(os.path.join(output_dir, "pareto_front_all_generations.png"))
        plt.close()

        # GIFファイルのパスを指定
        gif_output_path = os.path.join(summary_csv_dir, 'pareto_front_all_generations.gif')

        # 現在の実験からのPNG画像ファイルを取得
        current_image_path = os.path.join(output_dir, "pareto_front_all_generations.png")
        current_image = imageio.imread(current_image_path)

        # 既存のGIFがあれば、それに新しい画像を追加する
        if os.path.exists(gif_output_path):
            # 既存のGIFから全てのフレームを読み込む
            with imageio.get_reader(gif_output_path) as reader:
                frames = [frame for frame in reader]

            # 新しい画像を追加
            frames.append(current_image)

            # 更新されたフレームリストから新しいGIFを作成
            with imageio.get_writer(gif_output_path, mode='I', duration=1.0, loop=0) as writer:
                for frame in frames:
                    writer.append_data(frame)
        else:  # GIFファイルが存在しない場合、新たに作成する
            with imageio.get_writer(gif_output_path, mode='I', duration=1.0, loop=0) as writer:
                writer.append_data(current_image)

        plt.close()