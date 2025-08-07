from MiniAI_Eora_SelfEvolution import MiniAI
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog
from PyQt5.QtCore import QMetaObject, Qt, Q_ARG
from pymongo import MongoClient
from datetime import datetime
import threading, time, os, json, hashlib

from EORA.eora_modular.recall_memory_with_enhancements import recall_memory_with_enhancements
from EORA.eora_modular.eora_dialog_loader import load_dialog_lines
from EORA.eora_modular.generate_eora_reply_api import generate_eora_reply
from EORA.eora_modular.eora_response_engine import summarize_gpt_response
from EORA.eora_modular.inner_eora_thought_loop import evaluate_eora_thought
from EORA.eora_modular.eora_code_executor import extract_python_code, run_python_code
from EORA.eora_modular.eora_file_sender import send_attachment_to_db
from EORA.eora_modular.eora_ui_elements import create_text_log, create_input_line
from EORA.eora_modular.training_prompt_manager import add_training_prompt
from EORA.eora_modular.eora_self_reflection_loop import run_reflection_cycle
from EORA_Wisdom_Framework.memory_strategy_manager import get_turn_limit_for_context
from aura_system.memory_structurer_advanced import estimate_emotion, extract_belief_vector
from aura_system.resonance_engine import calculate_resonance, embed_text

def generate_chain_id(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

class EORALearningFileAttachedTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.log = create_text_log()
        self.memo = create_text_log()
        self.user_input = create_input_line()
        self.send_btn = QPushButton("📤 전송")
        self.attach_btn = QPushButton("📎 문서 첨부")
        self.start_btn = QPushButton("▶️ 대화 시작")
        self.stop_btn = QPushButton("⏹️ 중지")
        self.attach_file_btn = QPushButton("📎 파일 직접 첨부")

        self.send_btn.clicked.connect(self.user_reply)
        self.attach_btn.clicked.connect(self.load_documents)
        self.attach_file_btn.clicked.connect(self.attach_manual_file)
        self.start_btn.clicked.connect(self.start_conversation)
        self.stop_btn.clicked.connect(self.stop_conversation)

        for btn in [self.attach_btn, self.attach_file_btn, self.start_btn, self.stop_btn, self.log,
                    self.memo, self.user_input, self.send_btn]:
            self.layout.addWidget(btn)
        self.setLayout(self.layout)

        self.all_files = []
        self.file_index = 0
        self.user_lines, self.gpt_lines = [], []
        self.index = 0
        self.running = False
        self.db = MongoClient("mongodb://localhost:27017")["EORA"]
        self.memory = self.db["memory_atoms"]
        self.prompts = self.db["prompt_history"]

    def safe_append(self, widget, text):
        if widget:
            try:
                QMetaObject.invokeMethod(widget, "append", Qt.QueuedConnection, Q_ARG(str, text))
            except RuntimeError:
                print("❌ safe_append 실패: QTextEdit 위젯이 이미 닫혔습니다.")

    def load_documents(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "문서 선택", "", "Text/Word Files (*.txt *.md *.docx)")
        if not paths:
            return
        self.all_files = paths
        self.file_index = 0
        self.safe_append(self.log, f"📁 {len(paths)}개 문서 로드 완료")

    def attach_manual_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "참고용 파일 첨부", "", "Text/Word Files (*.txt *.md *.docx)")
        if path:
            send_attachment_to_db(os.path.basename(path), self.db, lambda msg: self.safe_append(self.log, msg))

    def start_conversation(self):
        if not self.all_files:
            self.safe_append(self.log, "⚠️ 첨부된 문서가 없습니다.")
            return
        self.running = True
        self.safe_append(self.log, "🚀 대화 학습 시작")
        threading.Thread(target=self.run_files_loop).start()

    def stop_conversation(self):
        self.running = False
        self.safe_append(self.log, "⏹️ 대화 학습 중지됨")

    def run_files_loop(self):
        while self.running and self.file_index < len(self.all_files):
            path = self.all_files[self.file_index]
            self.user_lines, self.gpt_lines = load_dialog_lines(path)
            self.current_docx_name = os.path.basename(path)
            self.index = load_last_index(self.current_docx_name)
            self.safe_append(self.log, f"📄 {self.current_docx_name} 학습 시작 (이어서 {self.index + 1}턴)")
            self.safe_append(self.log, f"✅ 총 {len(self.user_lines)}턴 감지됨")

            while self.running and self.index < min(len(self.user_lines), len(self.gpt_lines)):
                user = self.user_lines[self.index].strip()
                gpt = self.gpt_lines[self.index].strip()

                if not user and not gpt:
                    self.index += 1
                    continue

                self.safe_append(self.log, f"🌀 TURN {self.index + 1}")
                self.safe_append(self.log, f"👤 사용자: {user}")
                self.safe_append(self.log, f"🤖 GPT: {gpt}")

                recall_hits = recall_memory_with_enhancements(user + gpt, self.memory)
                if recall_hits:
                    for hit in recall_hits:
                        summary = hit.get("summary", "(요약 없음)")
                        self.safe_append(self.memo, f"📘 회상된 기억 요약: {summary}")
                        try:
                            mini = MiniAI("레조나", "회상 반응", ["지속", "통찰"], ["회상은 방향을 정한다"])
                            mini.remember(summary)
                            mini.evolve_structure()
                            judgment = mini.judge(summary)
                            self.safe_append(self.memo, f"💫 미니AI 판단: {judgment}")
                            self.memory.insert_one({
                                "type": "recalled_summary",
                                "source": "recall_memory_with_enhancements",
                                "summary": summary,
                                "judgment": judgment,
                                "timestamp": datetime.utcnow()
                            })
                        except Exception as me:
                            self.safe_append(self.log, f"❌ MiniAI 처리 실패: {me}")

                eora = generate_eora_reply(user, gpt, "", recall_context=recall_hits)
                if not eora or not isinstance(eora, str) or len(eora.strip()) < 2:
                    self.safe_append(self.log, "❌ 이오라 응답 생성 실패 또는 빈 응답")
                    self.index += 1
                    continue

                self.safe_append(self.log, f"🧠 이오라: {eora}")
                if len(eora.strip()) <= 300:
                    self.safe_append(self.memo, f"🧠 {eora}")

                try:
                    from EORA.eora_modular.evaluate_eora_turn import evaluate_eora_turn
                    result = evaluate_eora_turn(user, gpt, eora)
                    recommended = result.get("추천 프롬프트", "").strip()
                    user_msg = result.get("사용자 전달 메시지", "").strip()

                    if recommended:
                        self.prompts.insert_one({
                            "prompt": recommended,
                            "source": "이오라 자아 판단기",
                            "created_at": datetime.utcnow()
                        })
                        if isinstance(user_msg, str) and any(word in user_msg for word in ["판단", "도움"]):
                            self.safe_append(self.memo, f"📩 {user_msg}")
                except Exception as e:
                    self.safe_append(self.log, f"❌ 이오라 판단 오류: {str(e)}")
                finally:
                    self.index += 1
                    save_last_index(self.current_docx_name, self.index)
                    time.sleep(0.5)

                embedding = embed_text(user + gpt)
                belief_vector = extract_belief_vector(user + gpt)
                resonance_score = calculate_resonance(embedding, embed_text(eora))
                emotion_score = estimate_emotion(eora)
                summary_text = summarize_gpt_response(gpt, eora)

                memory_data = {
                    "type": "aura_memory",
                    "owner": "eora",
                    "user": user,
                    "gpt": gpt,
                    "eora": eora,
                    "trigger_keywords": [kw for kw in ["가치", "교훈", "배움", "통찰"] if kw in eora],
                    "summary": summary_text,
                    "importance": 1.0 if "가치" in eora else 0.75,
                    "emotion_score": emotion_score,
                    "resonance_score": resonance_score,
                    "belief_vector": belief_vector,
                    "semantic_embedding": embedding,
                    "timestamp": datetime.utcnow(),
                    "source": self.current_docx_name,
                    "turn": self.index,
                    "chain_id": generate_chain_id(user + gpt + eora),
                    "linked_ids": []
                }

                self.memory.insert_one(memory_data)

                code = extract_python_code(gpt)
                if code:
                    try:
                        result = run_python_code(code)
                        self.safe_append(self.log, f"⚙️ 실행 결과: {result[:100]}")
                    except Exception as e:
                        self.safe_append(self.log, f"❌ 코드 실행 실패: {e}")
                        self.safe_append(self.memo, "🚨 코드 실행 실패 – 확인 필요")

                self.index += 1
                save_last_index(self.current_docx_name, self.index)
                time.sleep(0.5)

            self.file_index += 1

        self.safe_append(self.log, "✅ 모든 문서 학습 완료")
        run_reflection_cycle()
        self.safe_append(self.memo, "🧠 이오라 자기 사고 루프 실행 완료 (run_reflection_cycle)")

    def user_reply(self):
        text = self.user_input.text().strip()
        if text:
            self.safe_append(self.log, f"👤 사용자 응답: {text}")
            self.safe_append(self.memo, "✅ 사용자 응답 기록됨")
            self.user_input.clear()
            if text.startswith("/첨부:"):
                send_attachment_to_db(text.replace("/첨부:", "").strip(), self.db, lambda msg: self.safe_append(self.log, msg))

def save_last_index(filename, index):
    path = os.path.expanduser("~/.eora_learning_progress.json")
    data = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    data[filename] = index
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_last_index(filename):
    path = os.path.expanduser("~/.eora_learning_progress.json")
    if not os.path.exists(path):
        return 0
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(filename, 0)
