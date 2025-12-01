import json
import os
import re

class KnowledgeBase:
    def __init__(self, kb_path):
        self.kb_path = kb_path
        self.data = {"errors": []}
        self.load()

    def load(self):
        if os.path.exists(self.kb_path):
            with open(self.kb_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            # создать пустой kb
            self.save()

    def save(self):
        with open(self.kb_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def find_fix(self, message):
        """Ищет подходящую запись по тексту ошибки."""
        for item in self.data.get("errors", []):
            if re.search(item["pattern"], message):
                return item
        return None

    def register_error(self, pattern, description, fix):
        """Добавляет новый шаблон ошибки."""
        self.data["errors"].append({
            "pattern": pattern,
            "description": description,
            "fix": fix
        })
        self.save()

# Быстрый метод для использования
def load_kb():
    kb_path = os.path.join("Gui", "knowledge.json")
    return KnowledgeBase(kb_path)
