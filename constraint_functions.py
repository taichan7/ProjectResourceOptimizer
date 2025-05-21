class ConstraintFunctions:  # 制約条件クラス
    def __init__(self, tasks, members, constraint_weights, individual):  # コンストラクタ
        self.tasks = tasks  # タスクリスト
        self.members = members  # メンバーリスト
        self.constraint_weights = constraint_weights  # 制約条件の重み
        self.individual = individual  # 個体

    # def c1(self, task_index):  # C1制約
    #     task = self.tasks[task_index]  # タスク
    #     assigned_member1 = self.members[self.individual[task_index]]  # タスクの担当メンバー1
    #     penalty = 0  # ペナルティ
    #     task_violations = []  # タスク違反リスト
    #     overlap_task_count = 0  # 重複タスク数の初期化
    #     for t2, task2 in enumerate(self.tasks):  # タスクリストをループ
    #         if task != task2:  # タスクが異なる場合
    #             assigned_member2 = self.members[self.individual[t2]]  # タスク2の担当メンバー2
    #             if assigned_member1 == assigned_member2 and not (
    #                     task.end_date <= task2.start_date or task2.end_date <= task.start_date):  # タスク1とタスク2の担当メンバーが同じかつタスク1とタスク2の期間が重なる場合
    #                 task_violations.append("C1")  # タスク違反リストにC1を追加
    #                 overlap = min(task.end_date, task2.end_date) - max(task.start_date, task2.start_date)  # タスクの重複期間を計算
    #                 penalty += self.constraint_weights[0] * overlap.days / max((task.end_date - task.start_date).days, (task2.end_date - task2.start_date).days)  # ペナルティにC1の重みとタスクの重複期間をタスクの最大期間で割った値を加算
    #                 overlap_task_count += 1  # 重複タスク数を加算
    #     penalty += self.constraint_weights[0] * overlap_task_count  # 重複タスク数に対するペナルティを加算（C1の重みを利用）      
          
    #     return penalty, task_violations  # ペナルティとタスク違反リストを返す

    def c1(self, task_index):  # C1制約
        task = self.tasks[task_index]  # タスク
        assigned_member1 = self.members[self.individual[task_index]]  # タスクの担当メンバー1
        penalty = 0  # ペナルティ
        task_violations = []  # タスク違反リスト

        for t2, task2 in enumerate(self.tasks):  # タスクリストをループ
            if task != task2:  # タスクが異なる場合
                assigned_member2 = self.members[self.individual[t2]]  # タスク2の担当メンバー2
                # タスク1とタスク2の担当メンバーが同じかつタスク1とタスク2の期間が重なる場合
                if assigned_member1 == assigned_member2 and not (task.end_date <= task2.start_date or task2.end_date <= task.start_date):
                    task_violations.append("C1")  # タスク違反リストにC1を追加
                    penalty = self.constraint_weights[0]  # 一度でも違反があればペナルティを加算
                    break  # 重複が見つかった時点でループを終了

        return penalty, task_violations  # ペナルティとタスク違反リストを返す

    # def c2(self, task_index):  # C2制約
    #     task = self.tasks[task_index]  # タスク
    #     assigned_member = self.members[self.individual[task_index]]  # タスクの担当メンバー
    #     penalty = 0  # ペナルティ
    #     task_violations = []  # タスク違反リスト
    #     actual_cost = assigned_member.cost * task.get_duration()  # メンバーのコストとタスクの期間による実際のコスト
    #     budget_ratio = actual_cost / task.budget  # 実際のコストとタスクの予算との比率（コスト超過率）
    #     if budget_ratio > 1:  # コスト超過率が1を超える場合（つまり、実際のコストが予算を超える場合）
    #         task_violations.append("C2")  # タスク違反リストにC2を追加
    #         penalty = self.constraint_weights[1] * (budget_ratio - 1) # ペナルティにC2の重みとコスト超過率から1を引いた値を加算
 
    #     return penalty, task_violations  # ペナルティとリワードを合算した結果とタスク違反リストを返す

    def c2(self, task_index):  # C2制約
        task = self.tasks[task_index]  # タスク
        assigned_member = self.members[self.individual[task_index]]  # タスクの担当メンバー
        penalty = 0  # ペナルティ
        task_violations = []  # タスク違反リスト
        actual_cost = assigned_member.cost * task.get_duration()  # メンバーのコストとタスクの期間による実際のコスト

        if actual_cost > task.budget:  # 実際のコストが予算を超える場合
            task_violations.append("C2")  # タスク違反リストにC2を追加
            penalty = self.constraint_weights[1]  # 一定のペナルティを適用

        return penalty, task_violations  # ペナルティとタスク違反リストを返す

    # def c3(self, task_index):  # C3制約
    #     task = self.tasks[task_index]  # タスク
    #     assigned_member = self.members[self.individual[task_index]]  # タスクの担当メンバー
    #     penalty = 0  # ペナルティ
    #     task_violations = []  # タスク違反リスト
    #     required_skills = set(task.skill_set)  # タスクの必要スキル
    #     member_skills = assigned_member.skill_set  # メンバーのスキル
    #     matched_skills = required_skills.intersection(member_skills)  # タスクの必要スキルとメンバーのスキルの積集合
    #     match_ratio = len(matched_skills) / len(required_skills)  # タスクの必要スキルとメンバーのスキルの積集合の要素数をタスクの必要スキルの要素数で割った値
    #     if match_ratio < 1:  # タスクの必要スキルとメンバーのスキルの積集合の要素数がタスクの必要スキルの要素数より小さい場合
    #         task_violations.append("C3")  # タスク違反リストにC3を追加
    #         penalty = self.constraint_weights[2] * (1 - match_ratio) # ペナルティをC3の重みとタスクの必要スキルとメンバーのスキルの積集合の要素数をタスクの必要スキルの要素数で割った値の差とする

    #     return penalty, task_violations  # ペナルティとリワードの和とタスク違反リストを返す

    def c3(self, task_index):  # C3制約
        task = self.tasks[task_index]  # タスク
        assigned_member = self.members[self.individual[task_index]]  # タスクの担当メンバー
        penalty = 0  # ペナルティ
        task_violations = []  # タスク違反リスト
        required_skills = set(task.skill_set)  # タスクの必要スキル
        member_skills = assigned_member.skill_set  # メンバーのスキル

        if not required_skills.issubset(member_skills):  # メンバーのスキルセットがタスクの必要スキルを完全にカバーしていない場合
            task_violations.append("C3")  # タスク違反リストにC3を追加
            penalty = self.constraint_weights[2]  # 一定のペナルティを適用

        return penalty, task_violations  # ペナルティとタスク違反リストを返す

    def apply_constraints(self):  # 制約条件を適用
        penalty = 0  # ペナルティ
        constraint_violations = []  # 制約違反リスト
        constraint_penalties = []  # 制約ペナルティリスト
        for task_index in range(len(self.tasks)):  # タスクリストをループ
            task_violations = []  # タスク違反リスト
            task_penalties = []  # タスクペナルティリスト
            # 各制約メソッドをループし、ペナルティと違反リストを更新
            for constraint_method in [self.c1, self.c2, self.c3]: # 制約メソッドリストをループ
                pen, violations = constraint_method(task_index) # 制約メソッドを実行
                penalty += pen # ペナルティに制約メソッドのペナルティを加算
                task_violations.extend(violations) # タスク違反リストに制約メソッドの違反リストを追加
                task_penalties.append(pen)  # タスクペナルティリストにペナルティを追加

            constraint_violations.append(task_violations)  # 制約違反リストにタスク違反リストを追加
            constraint_penalties.append(task_penalties)  # 制約ペナルティリストにタスクペナルティリストを追加

        # print(f"Violations: ", constraint_violations)  # 制約違反リストを表示
        # print(f"Penalties: ", constraint_penalties)  # 制約ペナルティリストを表示
        self.individual.constraint_violations = constraint_violations  # 個体の制約違反リストに制約違反リストを設定
        self.individual.constraint_penalties = constraint_penalties  # 個体の制約ペナルティリストに制約ペナルティリストを設定

        # print(f"Penalty: ", penalty)  # ペナルティを表示
        return penalty  # ペナルティを返す