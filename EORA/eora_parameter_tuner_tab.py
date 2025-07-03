from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox,
    QCheckBox, QComboBox, QHBoxLayout
)
import os
import json
import statistics
from EORA.eora_dynamic_params import KEYWORD_PARAMS, DEFAULT_PARAMS, decide_chat_params

class ParameterTunerTab(QWidget):
    current_instance = None  # ✅ 전역 접근 가능하게 저장

    def __init__(self):
        super().__init__()
        self.__class__.current_instance = self  # ✅ 현재 인스턴스 등록

        self.layout = QVBoxLayout()

        # 경고 라벨
        warning = QLabel(
            "주의: 시나리오는 한 줄에 하나씩 입력하세요. 최대 300개. 과도한 개수나 잘못된 문장은 성능 저하를 일으킬 수 있습니다."
        )
        warning.setStyleSheet("color: red;")
        self.layout.addWidget(warning)

        # 시나리오 입력창
        self.scenario_input = QTextEdit()
        self.scenario_input.setPlaceholderText(
            "예시: 안녕, 오늘 날씨가 궁금해\n새로운 모바일 앱 기획 아이디어가 필요해"
        )
        self.scenario_input.textChanged.connect(self.update_count)
        self.layout.addWidget(self.scenario_input)

        # 시나리오 개수 표시
        self.count_label = QLabel("시나리오: 0/300")
        self.layout.addWidget(self.count_label)

        # 실행 버튼
        self.run_button = QPushButton("자동 파라미터 튜닝 실행")
        self.run_button.clicked.connect(self.run_optimization)
        self.layout.addWidget(self.run_button)

        # 파라미터 적용 버튼
        self.apply_button = QPushButton("제안 파라미터 적용")
        self.apply_button.clicked.connect(self.apply_suggestions)
        self.apply_button.setEnabled(False)
        self.layout.addWidget(self.apply_button)

        # 자동 재튜닝 설정
        auto_layout = QHBoxLayout()
        self.auto_tune_checkbox = QCheckBox("자동 재튜닝 활성화")
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["일간", "주간", "월간"])
        auto_layout.addWidget(self.auto_tune_checkbox)
        auto_layout.addWidget(QLabel("주기:"))
        auto_layout.addWidget(self.interval_combo)
        self.layout.addLayout(auto_layout)

        # 로그 표시창
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.layout.addWidget(self.log)

        self.setLayout(self.layout)
        self.suggestions = None

    def update_count(self):
        lines = [l for l in self.scenario_input.toPlainText().splitlines() if l.strip()]
        count = len(lines)
        self.count_label.setText(f"시나리오: {count}/300")
        if count > 300:
            self.count_label.setStyleSheet("color: red;")
        else:
            self.count_label.setStyleSheet("")

    def run_optimization(self):
        text = self.scenario_input.toPlainText().strip()
        scenarios = [line.strip() for line in text.splitlines() if line.strip()]
        if not scenarios:
            QMessageBox.warning(self, "입력 오류", "시나리오를 한 줄에 하나씩 입력해주세요.")
            return
        if len(scenarios) > 300:
            QMessageBox.warning(self, "입력 오류", "시나리오는 최대 300개까지만 허용됩니다.")
            return

        self.log.append(f"🔄 시뮬레이션 시작: {len(scenarios)}개 시나리오")
        # 결과 수집
        results = {kw: [] for kw in KEYWORD_PARAMS}
        results['DEFAULT'] = []
        iterations = 10
        for i in range(iterations):
            for scenario in scenarios:
                messages = [{"role": "user", "content": scenario}]
                params = decide_chat_params(messages)
                bucket = 'DEFAULT'
                for kw in KEYWORD_PARAMS:
                    if kw in scenario:
                        bucket = kw
                        break
                results.setdefault(bucket, []).append((params['temperature'], params['top_p']))
        # 평균 계산
        suggestions = {}
        for bucket, vals in results.items():
            if not vals:
                continue
            temps = [v[0] for v in vals]
            tops = [v[1] for v in vals]
            suggestions[bucket] = {
                "temperature": round(statistics.mean(temps), 2),
                "top_p": round(statistics.mean(tops), 2)
            }
        # 파일 저장
        output_file = os.path.join(os.path.dirname(__file__), '..', 'suggested_params.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(suggestions, f, ensure_ascii=False, indent=2)
        self.log.append(f"✅ 시뮬레이션 완료. 제안 파일: {output_file}")
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
                        data = {
                            k: (v['temperature'], v['top_p'])
                            for k, v in self.suggestions.items() if k != 'DEFAULT'
                        }
                        lines.append('KEYWORD_PARAMS = ' + json.dumps(data, ensure_ascii=False, indent=4) + '\n')
                    elif line.strip().startswith('DEFAULT_PARAMS'):
                        d = self.suggestions.get('DEFAULT', None)
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

    # ✅ 외부에서 시나리오 자동 추가용
    def add_scenario(self, text):
        current = self.scenario_input.toPlainText().strip()
        if text not in current:
            if current:
                self.scenario_input.setPlainText(current + '\n' + text)
            else:
                self.scenario_input.setPlainText(text)
            self.log.append(f"➕ 시나리오 추가됨: {text}")
            self.update_count()
