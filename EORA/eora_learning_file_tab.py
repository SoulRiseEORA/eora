from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget, QFileDialog,
    QTextEdit, QLabel, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer
import os, json, time
from datetime import datetime

from EORA.eora_backend import extract_text_from_file
from EORA.gpt_router import ask
from memory_db import save_chunk
from ai_chat import get_eora_instance

class EORALearningFileTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.file_list = QListWidget()
        layout.addWidget(QLabel("📎 첨부 문서 목록"))
        layout.addWidget(self.file_list)

        row = QHBoxLayout()
        add = QPushButton("➕ 추가")
        remove = QPushButton("❌ 선택 제거")
        clear = QPushButton("🧹 전체 제거")
        row.addWidget(add)
        row.addWidget(remove)
        row.addWidget(clear)
        layout.addLayout(row)

        simulate = QPushButton("🧠 분석 및 시뮬레이션 (EORA)")
        layout.addWidget(simulate)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(QLabel("📜 분석 결과 및 응답"))
        layout.addWidget(self.log)

        add.clicked.connect(self.add_files)
        remove.clicked.connect(self.remove_selected)
        clear.clicked.connect(self.file_list.clear)
        simulate.clicked.connect(self.run_simulation)

        self.queue = []
        self.current_index = 0
        self.auto_mode = True
        self.paused = False
        self.last_activity = time.time()

        ctrl = QHBoxLayout()
        self.btn_start = QPushButton("▶ 재생")
        self.btn_pause = QPushButton("⏸ 중지")
        self.btn_next = QPushButton("⏭ 다음")
        ctrl.addWidget(self.btn_start)
        ctrl.addWidget(self.btn_pause)
        ctrl.addWidget(self.btn_next)
        layout.addLayout(ctrl)

        self.btn_start.clicked.connect(self.start_loop)
        self.btn_pause.clicked.connect(self.pause_loop)
        self.btn_next.clicked.connect(self.step_once)

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.loop_runner)
        self.timer.start()

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "파일 선택", "", "문서 파일 (*.txt *.pdf *.docx *.hwp *.json)")
        for f in files:
            if f not in [self.file_list.item(i).text() for i in range(self.file_list.count())]:
                self.file_list.addItem(f)

    def remove_selected(self):
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))

    def run_simulation(self):
        self.log.clear()
        self.queue.clear()
        self.current_index = 0
        self.auto_mode = False
        self.paused = False

        files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        if not files:
            self.log.append("❗ 파일이 없습니다.")
            return

        ai = get_eora_instance()
        conv = []

        for path in files:
            try:
                self.log.append(f"📎 분석 중: {os.path.basename(path)}")
                chunks = extract_text_from_file(path)
                for ch in chunks:
                    save_chunk("최근기억", ch)
                    gpt_reply = ask(ch, system_msg="내용 요약 + 정리", max_tokens=512)
                    self.queue.append({"user": ch, "reply": gpt_reply})
                    self.log.append(f"👤 질문: {ch[:100]}...")
                    self.log.append(f"🤖 GPT: {gpt_reply[:200]}")
                    conv.append({"user": ch, "reply": gpt_reply})
            except Exception as e:
                self.log.append(f"❌ 분석 실패: {e}")

        if conv:
            self.save_prompt(conv)

    def save_prompt(self, data):
        folder = "training_prompts"
        os.makedirs(folder, exist_ok=True)
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(folder, f"EORA_training_{now}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self.log.append(f"✅ 훈련 저장 완료: {path}")

    def loop_runner(self):
        now = time.time()
        if self.auto_mode and not self.paused and self.queue:
            if now - self.last_activity >= 5:
                self.step_once()
        elif self.paused and now - self.last_activity >= 60:
            self.log.append("⏳ 1분 정지됨. 계속 진행할까요?")
            self.paused = False

    def start_loop(self):
        self.auto_mode = True
        self.paused = False
        self.log.append("▶ 재생 시작")
        self.last_activity = time.time()

    def pause_loop(self):
        self.paused = True
        self.log.append("⏸ 중지됨")

    def step_once(self):
        if self.current_index >= len(self.queue):
            self.log.append("✅ 시뮬레이션 완료")
            self.auto_mode = False
            return
        turn = self.queue[self.current_index]
        q = turn.get("user", "")
        a = turn.get("reply", "")
        self.log.append(f"👤 사용자: {q[:150]}")
        self.log.append(f"🤖 GPT: {a[:150]}")
        reply = get_eora_instance().ask(q + "\n" + a)
        self.log.append(f"🧠 EORA: {reply[:300]}")
        self.log.append("—" * 40)
        self.current_index += 1
        self.last_activity = time.time()
