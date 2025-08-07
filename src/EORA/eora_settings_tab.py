# eora_settings_tab.py (패치 후)
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton,
    QMessageBox, QLineEdit, QHBoxLayout
)
import json
import os

class EORASettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("📝 EORA (AI1) 프롬프트 - SYSTEM / ROLE / GUIDE / FORMAT"))

        self.prompt_box = QTextEdit()
        layout.addWidget(self.prompt_box)

        # 검색 UI
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 검색어 입력")
        self.search_input.returnPressed.connect(self.search_matches)

        self.search_btn = QPushButton("🔍 검색")
        self.search_btn.clicked.connect(self.search_matches)

        self.search_btn_prev = QPushButton("⬆ 이전")
        self.search_btn_next = QPushButton("⬇ 다음")
        self.lbl_result = QLabel("검색 결과 없음")

        self.search_btn_prev.clicked.connect(self.find_previous)
        self.search_btn_next.clicked.connect(self.find_next)

        search_row.addWidget(self.search_input)
        search_row.addWidget(self.search_btn)
        search_row.addWidget(self.search_btn_prev)
        search_row.addWidget(self.search_btn_next)
        search_row.addWidget(self.lbl_result)
        layout.addLayout(search_row)

        # 저장 / 새로고침
        btn_row = QHBoxLayout()
        self.btn_refresh = QPushButton("🔄 새로고침")
        self.btn_save = QPushButton("💾 저장")
        self.btn_refresh.clicked.connect(self.load_prompt)
        self.btn_save.clicked.connect(self.save_prompt)
        btn_row.addWidget(self.btn_refresh)
        btn_row.addWidget(self.btn_save)
        layout.addLayout(btn_row)

        self.setLayout(layout)
        self.match_positions = []
        self.current_match_index = -1
        self.load_prompt()

    def load_prompt(self):
        try:
            path = os.path.join("ai_brain", "ai_prompts.json")
            if not os.path.exists(path):
                raise FileNotFoundError("ai_prompts.json 파일이 없습니다.")
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                ai1 = data.get("ai1", {})
                prompt_text = (
                    f"### SYSTEM\n{ai1.get('system','')}\n\n"
                    f"### ROLE\n{ai1.get('role','')}\n\n"
                    f"### GUIDE\n{ai1.get('guide','')}\n\n"
                    f"### FORMAT\n{ai1.get('format','')}"
                )
                self.prompt_box.setText(prompt_text)
        except Exception as e:
            QMessageBox.critical(self, "불러오기 실패", str(e))

    def save_prompt(self):
        try:
            raw = self.prompt_box.toPlainText()
            parts = {"system": "", "role": "", "guide": "", "format": ""}
            section = None
            for line in raw.splitlines():
                line = line.strip()
                if line.startswith("###"):
                    section = line.replace("#", "").strip().lower()
                elif section in parts:
                    parts[section] += line + "\n"

            path = os.path.join("ai_brain", "ai_prompts.json")
            with open(path, "r+", encoding="utf-8") as f:
                data = json.load(f)
                data["ai1"].update({k: v.strip() for k, v in parts.items()})
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.truncate()

            QMessageBox.information(self, "저장 완료", "프롬프트가 업데이트 되었습니다.")
        except Exception as e:
            QMessageBox.critical(self, "저장 실패", str(e))

    def search_matches(self):
        text = self.prompt_box.toPlainText()
        keyword = self.search_input.text().strip()
        self.match_positions.clear()
        if keyword:
            cursor = self.prompt_box.textCursor()
            cursor.setPosition(0)
            self.prompt_box.setTextCursor(cursor)

            while True:
                found = self.prompt_box.find(keyword)
                if not found:
                    break
                self.match_positions.append(self.prompt_box.textCursor().selectionStart())

        self.current_match_index = 0 if self.match_positions else -1
        self.lbl_result.setText(f"{len(self.match_positions)}개 결과")
        if self.match_positions:
            self.move_to_match("next")

    def move_to_match(self, direction):
        if not self.match_positions:
            return
        if direction == "next":
            self.current_match_index = (self.current_match_index + 1) % len(self.match_positions)
        elif direction == "prev":
            self.current_match_index = (self.current_match_index - 1) % len(self.match_positions)

        cursor = self.prompt_box.textCursor()
        pos = self.match_positions[self.current_match_index]
        cursor.setPosition(pos)
        cursor.movePosition(cursor.Right, cursor.KeepAnchor, len(self.search_input.text()))
        self.prompt_box.setTextCursor(cursor)
        self.prompt_box.setFocus()
        self.lbl_result.setText(f"{self.current_match_index + 1} / {len(self.match_positions)}")

    def find_next(self):
        self.move_to_match("next")

    def find_previous(self):
        self.move_to_match("prev")


# eora_parameter_tuner_tab.py (패치 후)
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton,
    QMessageBox, QCheckBox, QComboBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
import os
import json
import statistics
from EORA.eora_dynamic_params import KEYWORD_PARAMS, DEFAULT_PARAMS, decide_chat_params

class ParameterTunerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        warning = QLabel(
            "주의: 시나리오는 한 줄에 하나씩 입력하세요. 최대 200개. 과도한 개수나 잘못된 문장은 성능 저하를 일으킬 수 있습니다."
        )
        warning.setStyleSheet("color: red;")
        self.layout.addWidget(warning)

        self.scenario_input = QTextEdit()
        self.scenario_input.setPlaceholderText(
            "예시: 안녕, 오늘 날씨가 궁금해\n새로운 모바일 앱 기획 아이디어가 필요해"
        )
        self.layout.addWidget(self.scenario_input)

        self.run_button = QPushButton("자동 파라미터 튜닝 실행")
        self.run_button.clicked.connect(self.run_optimization)
        self.layout.addWidget(self.run_button)

        self.apply_button = QPushButton("제안 파라미터 적용")
        self.apply_button.clicked.connect(self.apply_suggestions)
        self.apply_button.setEnabled(False)
        self.layout.addWidget(self.apply_button)

        # ─── 자동 재튜닝 설정 추가 ───
        self.auto_re_tune_cb = QCheckBox("자동 재튜닝 활성화")
        self.auto_re_tune_cb.stateChanged.connect(self.toggle_auto_re_tune)
        self.layout.addWidget(self.auto_re_tune_cb)

        interval_row = QHBoxLayout()
        interval_row.addWidget(QLabel("주기:"))
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["매일", "매주", "매월"])
        interval_row.addWidget(self.interval_combo)
        self.layout.addLayout(interval_row)
        # ─────────────────────────────

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.layout.addWidget(self.log)

        self.setLayout(self.layout)
        self.suggestions = None

    def toggle_auto_re_tune(self, state):
        if state == Qt.Checked:
            interval = self.interval_combo.currentText()
            self.log.append(f"✅ 자동 재튜닝 활성화: {interval}")
            # TODO: 스케줄 등록 로직 추가
        else:
            self.log.append("❌ 자동 재튜닝 비활성화")
            # TODO: 스케줄 해제 로직 추가

    def run_optimization(self):
        text = self.scenario_input.toPlainText().strip()
        scenarios = [line.strip() for line in text.splitlines() if line.strip()]
        if not scenarios:
            QMessageBox.warning(self, "입력 오류", "시나리오를 한 줄에 하나씩 입력해주세요.")
            return
        if len(scenarios) > 200:
            QMessageBox.warning(self, "입력 오류", "시나리오는 최대 200개까지만 허용됩니다.")
            return

        self.log.append(f"🔄 시뮬레이션 시작: {len(scenarios)}개 시나리오")
        results = {kw: [] for kw in KEYWORD_PARAMS}
        results['DEFAULT'] = []
        iterations = 10
        for _ in range(iterations):
            for scenario in scenarios:
                params = decide_chat_params([{"role": "user", "content": scenario}])
                bucket = next((kw for kw in KEYWORD_PARAMS if kw in scenario), 'DEFAULT')
                results.setdefault(bucket, []).append((params['temperature'], params['top_p']))

        suggestions = {}
        for bucket, vals in results.items():
            if not vals:
                continue
            temps = [v[0] for v in vals]
            tops  = [v[1] for v in vals]
            suggestions[bucket] = {
                "temperature": round(statistics.mean(temps), 2),
                "top_p": round(statistics.mean(tops), 2)
            }

        output_file = os.path.join(os.path.dirname(__file__), '..', 'suggested_params.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(suggestions, f, ensure_ascii=False, indent=2)

        self.log.append(f"시뮬레이션 완료. 제안 파일: {output_file}")
        self.log.append(json.dumps(suggestions, ensure_ascii=False, indent=2))
        self.suggestions = suggestions
        self.apply_button.setEnabled(True)

    def apply_suggestions(self):
        if not self.suggestions:
            QMessageBox.warning(self, "실행 오류", "먼저 최적화 실행을 해주세요.")
            return
        dyn_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'eora_dynamic_params.py'))
        try:
            lines = []
            with open(dyn_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith('KEYWORD_PARAMS'):
                        data = {k: (v['temperature'], v['top_p']) for k, v in self.suggestions.items() if k != 'DEFAULT'}
                        lines.append('KEYWORD_PARAMS = ' + json.dumps(data, ensure_ascii=False, indent=4) + '\n')
                    elif line.strip().startswith('DEFAULT_PARAMS'):
                        d = self.suggestions.get('DEFAULT')
                        if d:
                            lines.append(f"DEFAULT_PARAMS = ({d['temperature']}, {d['top_p']})\n")
                        else:
                            lines.append(line)
                    else:
                        lines.append(line)
            with open(dyn_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            self.log.append("✅ 파라미터가 eora_dynamic_params.py 에 반영되었습니다.")
            QMessageBox.information(self, "완료", "파라미터 적용이 완료되었습니다.")
        except Exception as e:
            self.log.append(f"❌ 적용 실패: {e}")
            QMessageBox.critical(self, "적용 오류", str(e))
