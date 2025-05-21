from typing import List # List型を使うために必要

class Member: # メンバークラス
    def __init__(self, id: int, name: str, skill_set: List[str], cost: float): # コンストラクタ
        self.id = id # メンバーID
        self.name = name # メンバー名
        self.skill_set = skill_set # スキルセット
        self.cost = cost # コスト

    def add_skill(self, skill: str): # スキルを追加するメソッド
        if skill not in self.skill_set: # スキルが既に追加されていないか確認
            self.skill_set.append(skill) # 追加

    def remove_skill(self, skill: str): # スキルを削除するメソッド
        if skill in self.skill_set: # スキルが既に追加されているか確認
            self.skill_set.remove(skill) # 削除 

    def get_skills(self) -> List[str]: # スキルを取得するメソッド
        return self.skill_set # スキルを返す