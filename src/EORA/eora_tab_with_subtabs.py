from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QPushButton, QLineEdit, QTextEdit, QHBoxLayout
from EORA.eora_learning_tab import EORALearningTab
from EORA.eora_learning_file_attached_tab import EORALearningFileAttachedTab
from EORA.eora_prompt_planner_tab import PromptPlannerTab
from EORA.eora_prompt_memory_dialogue_tab import EORAPromptMemoryDialogueTab
from EORA.eora_profile_editor_tab import ProfileEditorTab
from EORA.eora_learning_debug_ai2ai3_tab import DebugTabAI2AI3
from EORA.eora_aura_memory_tab import AURAMemoryTab
from EORA.eora_prompt_logger_tab import PromptLoggerTab
from EORA.eora_goal_tracker_tab import GoalTrackerTab
from EORA.eora_goal_conversation_tab import EORAGoalPlannerTab
from EORA.eora_file_analyzer import FileAnalyzerTab
from EORA.eora_training_simulation_tab import EORATrainingSimulationTab
from EORA.eora_mindmap_tab import MindMapTab
from EORA.eora_prompt_graph_editor import PromptGraphEditor
from EORA.eora_prompt_storage_viewer import PromptStorageViewer
from EORA.eora_memory_log_viewer import EmotionMemoryLogViewer
from EORA.eora_journal_viewer import EORAJournalViewer
from EORA.eora_settings_tab import EORASettingsTab
from EORA.eora_parameter_tuner_tab import ParameterTunerTab  # 파라미터 튜닝 탭 추가
from EORA.intuition_training_tab import IntuitionTrainingTab

class EORATab(QWidget):
    def __init__(self, log_panel=None):
        super().__init__()
        layout = QVBoxLayout()
        tabs = QTabWidget()

        # 📘 학습 탭 (서브탭 구성)
        learn_widget = QWidget()
        learn_tabs = QTabWidget()

        # 자동 학습 서브탭
        auto_tab = QWidget()
        auto_layout = QVBoxLayout()
        auto_layout.addWidget(EORALearningTab())
        auto_layout.addWidget(QPushButton("▶️ 학습 시작"))
        auto_layout.addWidget(QPushButton("⏹️ 중지"))
        auto_tab.setLayout(auto_layout)
        learn_tabs.addTab(auto_tab, "자동 학습")

        # 첨부 학습 서브탭
        attach_tab = QWidget()
        attach_layout = QVBoxLayout()
        attach_layout.addWidget(EORALearningFileAttachedTab())
        attach_tab.setLayout(attach_layout)
        learn_tabs.addTab(attach_tab, "첨부 학습")

        # 기타 서브탭
        learn_tabs.addTab(PromptPlannerTab(), "프롬프트 기획")
        learn_widget.setLayout(QVBoxLayout())
        learn_widget.layout().addWidget(learn_tabs)
        tabs.addTab(learn_widget, "📘 학습")

        # 🤖 자아 판단 탭
        think_tab = QWidget()
        think_tabs = QTabWidget()
        think_tabs.addTab(EORAPromptMemoryDialogueTab(), "💬 프롬프트 대화")
        think_tabs.addTab(ProfileEditorTab(), "👤 프로필 설정")
        think_tabs.addTab(DebugTabAI2AI3(), "🧠 AI2/AI3 디버깅")
        think_tabs.addTab(AURAMemoryTab(), "🌀 AURA DB 검색")

        # 사용자 입력 서브탭
        think_input = QWidget()
        think_input_layout = QVBoxLayout()
        input_line = QLineEdit()
        send_btn = QPushButton("💬 전송")
        think_input_layout.addWidget(input_line)
        think_input_layout.addWidget(send_btn)
        think_input.setLayout(think_input_layout)
        think_tabs.addTab(think_input, "📤 사용자 입력")

        think_tab.setLayout(QVBoxLayout())
        think_tab.layout().addWidget(think_tabs)
        tabs.addTab(think_tab, "🤖 자아 판단")

        # 📂 로그 탭
        log_tab = QWidget()
        log_layout = QVBoxLayout()
        logger = PromptLoggerTab()
        refresh_btn = QPushButton("🔄 새로고침")
        refresh_btn.clicked.connect(lambda: logger.load_prompt_log())
        log_layout.addWidget(logger)
        log_layout.addWidget(refresh_btn)
        log_tab.setLayout(log_layout)
        tabs.addTab(log_tab, "📂 로그")

        # 🎯 목표 탭
        goal_tab = QWidget()
        goal_layout = QVBoxLayout()
        goal_layout.addWidget(GoalTrackerTab())
        goal_layout.addWidget(EORAGoalPlannerTab())
        goal_tab.setLayout(goal_layout)
        tabs.addTab(goal_tab, "🎯 목표")

        # 📂 분석기 탭
        tabs.addTab(FileAnalyzerTab(), "📂 분석기")

        # 🧪 시뮬레이션 탭
        tabs.addTab(EORATrainingSimulationTab(), "🧪 시뮬")

        # 🧠 구조 탭
        structure_tab = QTabWidget()
        structure_tab.addTab(MindMapTab(), "🧠 마인드맵")
        structure_tab.addTab(PromptGraphEditor(), "📊 프롬프트 그래프")
        tabs.addTab(structure_tab, "🧠 구조")

        # 📂 기록 탭
        record_tab = QTabWidget()
        record_tab.addTab(PromptStorageViewer(), "📦 저장소")
        record_tab.addTab(EmotionMemoryLogViewer(), "💬 감정/기억")
        record_tab.addTab(EORAJournalViewer(), "📓 저널")
        tabs.addTab(record_tab, "📂 기록")

        # 🧠 직감 훈련 탭 추가
        tabs.addTab(IntuitionTrainingTab(), "🧠 직감 훈련")

        # ⚙️ 설정 탭 (서브탭)
        settings_tab = QTabWidget()
        settings_tab.addTab(EORASettingsTab(), "기본 설정")
        settings_tab.addTab(ParameterTunerTab(), "파라미터 튜닝")
        tabs.addTab(settings_tab, "⚙️ 설정")

        layout.addWidget(tabs)
        self.setLayout(layout)
