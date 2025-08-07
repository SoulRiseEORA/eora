"""
ai_manager_tab.py
- AI 매니저 탭 구현
- AI 모델 관리, 설정 관리, 성능 모니터링 기능 제공
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QLineEdit, QFileDialog,
    QMessageBox, QSplitter, QFrame, QToolButton,
    QTableWidget, QTableWidgetItem, QProgressBar,
    QComboBox, QSpinBox, QCheckBox, QGroupBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QFont, QIcon, QTextCursor, QColor, QPalette

logger = logging.getLogger(__name__)

class AIModelWorker(QThread):
    """AI 모델 작업자 스레드"""
    
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, model_data: Dict[str, Any]):
        super().__init__()
        self.model_data = model_data
        self.loop = None
        
    def run(self):
        """작업 실행"""
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # 모델 작업 실행
            result = self.loop.run_until_complete(self.process_model())
            self.finished.emit(result)
            
        except Exception as e:
            logger.error(f"❌ 모델 작업 실패: {str(e)}")
            self.error.emit(str(e))
        finally:
            if self.loop:
                self.loop.close()
                
    async def process_model(self) -> Dict[str, Any]:
        """모델 처리"""
        try:
            # 모델 처리 로직
            for i in range(101):
                self.progress.emit(i)
                await asyncio.sleep(0.1)
                
            result = {
                "status": "success",
                "message": "모델 처리가 완료되었습니다.",
                "timestamp": datetime.now().isoformat()
            }
            return result
            
        except Exception as e:
            logger.error(f"❌ 모델 처리 실패: {str(e)}")
            raise

class AIManagerTab(QWidget):
    """AI 매니저 탭"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # AI 모델 데이터 초기화
        self.models = []
        self.current_model = None
        
        # UI 설정
        self.setup_ui()
        
    def setup_ui(self):
        """UI 설정"""
        try:
            # 메인 레이아웃
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(10)
            
            # 모델 목록
            self.model_list = QTableWidget()
            self.model_list.setColumnCount(4)
            self.model_list.setHorizontalHeaderLabels(["모델명", "타입", "상태", "성능"])
            self.model_list.setSelectionBehavior(QTableWidget.SelectRows)
            self.model_list.setSelectionMode(QTableWidget.SingleSelection)
            self.model_list.itemSelectionChanged.connect(self.on_model_selected)
            layout.addWidget(self.model_list)
            
            # 모델 정보 영역
            info_layout = QHBoxLayout()
            
            # 왼쪽 패널 (모델 정보)
            left_panel = QWidget()
            left_layout = QVBoxLayout(left_panel)
            
            # 모델명
            name_layout = QHBoxLayout()
            name_layout.addWidget(QLabel("모델명:"))
            self.model_name = QLineEdit()
            name_layout.addWidget(self.model_name)
            left_layout.addLayout(name_layout)
            
            # 모델 타입
            type_layout = QHBoxLayout()
            type_layout.addWidget(QLabel("타입:"))
            self.model_type = QComboBox()
            self.model_type.addItems(["GPT", "BERT", "T5", "기타"])
            type_layout.addWidget(self.model_type)
            left_layout.addLayout(type_layout)
            
            # 상태
            status_layout = QHBoxLayout()
            status_layout.addWidget(QLabel("상태:"))
            self.status = QComboBox()
            self.status.addItems(["활성", "비활성", "학습중"])
            status_layout.addWidget(self.status)
            left_layout.addLayout(status_layout)
            
            # 성능 설정
            performance_group = QGroupBox("성능 설정")
            performance_layout = QVBoxLayout(performance_group)
            
            # 정확도
            accuracy_layout = QHBoxLayout()
            accuracy_layout.addWidget(QLabel("정확도:"))
            self.accuracy = QSpinBox()
            self.accuracy.setRange(0, 100)
            self.accuracy.setValue(95)
            accuracy_layout.addWidget(self.accuracy)
            performance_layout.addLayout(accuracy_layout)
            
            # 속도
            speed_layout = QHBoxLayout()
            speed_layout.addWidget(QLabel("속도:"))
            self.speed = QSpinBox()
            self.speed.setRange(1, 10)
            self.speed.setValue(5)
            speed_layout.addWidget(self.speed)
            performance_layout.addLayout(speed_layout)
            
            left_layout.addWidget(performance_group)
            
            # 설명
            left_layout.addWidget(QLabel("설명:"))
            self.description = QTextEdit()
            left_layout.addWidget(self.description)
            
            info_layout.addWidget(left_panel)
            
            # 오른쪽 패널 (학습 데이터)
            right_panel = QWidget()
            right_layout = QVBoxLayout(right_panel)
            
            # 학습 데이터
            right_layout.addWidget(QLabel("학습 데이터:"))
            self.data_list = QTableWidget()
            self.data_list.setColumnCount(3)
            self.data_list.setHorizontalHeaderLabels(["데이터명", "크기", "상태"])
            right_layout.addWidget(self.data_list)
            
            # 데이터 추가 버튼
            add_data_btn = QPushButton("데이터 추가")
            add_data_btn.clicked.connect(self.add_data)
            right_layout.addWidget(add_data_btn)
            
            info_layout.addWidget(right_panel)
            layout.addLayout(info_layout)
            
            # 버튼 영역
            button_layout = QHBoxLayout()
            
            # 새 모델 버튼
            new_btn = QPushButton("새 모델")
            new_btn.clicked.connect(self.new_model)
            button_layout.addWidget(new_btn)
            
            # 저장 버튼
            save_btn = QPushButton("저장")
            save_btn.clicked.connect(self.save_model)
            button_layout.addWidget(save_btn)
            
            # 삭제 버튼
            delete_btn = QPushButton("삭제")
            delete_btn.clicked.connect(self.delete_model)
            button_layout.addWidget(delete_btn)
            
            # 학습 버튼
            train_btn = QPushButton("학습")
            train_btn.clicked.connect(self.train_model)
            button_layout.addWidget(train_btn)
            
            layout.addLayout(button_layout)
            
            # 진행 상태
            self.progress_bar = QProgressBar()
            self.progress_bar.setVisible(False)
            layout.addWidget(self.progress_bar)
            
        except Exception as e:
            logger.error(f"❌ UI 설정 실패: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise
            
    def new_model(self):
        """새 모델 생성"""
        try:
            self.model_name.clear()
            self.model_type.setCurrentIndex(0)
            self.status.setCurrentIndex(0)
            self.accuracy.setValue(95)
            self.speed.setValue(5)
            self.description.clear()
            self.data_list.setRowCount(0)
            self.current_model = None
        except Exception as e:
            logger.error(f"❌ 새 모델 생성 실패: {str(e)}")
            
    def save_model(self):
        """모델 저장"""
        try:
            if not self.model_name.text():
                QMessageBox.warning(self, "경고", "모델명을 입력하세요.")
                return
                
            model = {
                "name": self.model_name.text(),
                "type": self.model_type.currentText(),
                "status": self.status.currentText(),
                "accuracy": self.accuracy.value(),
                "speed": self.speed.value(),
                "description": self.description.toPlainText(),
                "data": []
            }
            
            # 학습 데이터 저장
            for row in range(self.data_list.rowCount()):
                data = {
                    "name": self.data_list.item(row, 0).text(),
                    "size": self.data_list.item(row, 1).text(),
                    "status": self.data_list.item(row, 2).text()
                }
                model["data"].append(data)
                
            # 모델 목록 업데이트
            if self.current_model is None:
                self.models.append(model)
            else:
                self.models[self.current_model] = model
                
            self.update_model_list()
            QMessageBox.information(self, "알림", "모델이 저장되었습니다.")
            
        except Exception as e:
            logger.error(f"❌ 모델 저장 실패: {str(e)}")
            
    def delete_model(self):
        """모델 삭제"""
        try:
            if self.current_model is None:
                QMessageBox.warning(self, "경고", "삭제할 모델을 선택하세요.")
                return
                
            reply = QMessageBox.question(
                self, "확인",
                "선택한 모델을 삭제하시겠습니까?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                del self.models[self.current_model]
                self.update_model_list()
                self.new_model()
                QMessageBox.information(self, "알림", "모델이 삭제되었습니다.")
                
        except Exception as e:
            logger.error(f"❌ 모델 삭제 실패: {str(e)}")
            
    def add_data(self):
        """학습 데이터 추가"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "학습 데이터 선택",
                "",
                "모든 파일 (*.*)"
            )
            
            if file_path:
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                size_str = f"{file_size / 1024 / 1024:.2f} MB"
                
                row = self.data_list.rowCount()
                self.data_list.insertRow(row)
                self.data_list.setItem(row, 0, QTableWidgetItem(file_name))
                self.data_list.setItem(row, 1, QTableWidgetItem(size_str))
                self.data_list.setItem(row, 2, QTableWidgetItem("대기"))
                
        except Exception as e:
            logger.error(f"❌ 학습 데이터 추가 실패: {str(e)}")
            
    def on_model_selected(self):
        """모델 선택 시"""
        try:
            selected = self.model_list.selectedItems()
            if not selected:
                return
                
            row = selected[0].row()
            self.current_model = row
            model = self.models[row]
            
            self.model_name.setText(model["name"])
            self.model_type.setCurrentText(model["type"])
            self.status.setCurrentText(model["status"])
            self.accuracy.setValue(model["accuracy"])
            self.speed.setValue(model["speed"])
            self.description.setText(model["description"])
            
            # 학습 데이터 업데이트
            self.data_list.setRowCount(0)
            for data in model["data"]:
                row = self.data_list.rowCount()
                self.data_list.insertRow(row)
                self.data_list.setItem(row, 0, QTableWidgetItem(data["name"]))
                self.data_list.setItem(row, 1, QTableWidgetItem(data["size"]))
                self.data_list.setItem(row, 2, QTableWidgetItem(data["status"]))
                
        except Exception as e:
            logger.error(f"❌ 모델 선택 실패: {str(e)}")
            
    def update_model_list(self):
        """모델 목록 업데이트"""
        try:
            self.model_list.setRowCount(len(self.models))
            for i, model in enumerate(self.models):
                self.model_list.setItem(i, 0, QTableWidgetItem(model["name"]))
                self.model_list.setItem(i, 1, QTableWidgetItem(model["type"]))
                self.model_list.setItem(i, 2, QTableWidgetItem(model["status"]))
                self.model_list.setItem(i, 3, QTableWidgetItem(f"{model['accuracy']}%"))
                
        except Exception as e:
            logger.error(f"❌ 모델 목록 업데이트 실패: {str(e)}")
            
    def train_model(self):
        """모델 학습"""
        try:
            if self.current_model is None:
                QMessageBox.warning(self, "경고", "학습할 모델을 선택하세요.")
                return
                
            if self.data_list.rowCount() == 0:
                QMessageBox.warning(self, "경고", "학습 데이터를 추가하세요.")
                return
                
            model = self.models[self.current_model]
            
            # 모델 작업자 생성 및 실행
            worker = AIModelWorker(model)
            worker.progress.connect(self.on_training_progress)
            worker.finished.connect(self.on_training_finished)
            worker.error.connect(self.on_training_error)
            worker.start()
            
            # 진행 상태 표시
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
        except Exception as e:
            logger.error(f"❌ 모델 학습 실패: {str(e)}")
            
    def on_training_progress(self, value: int):
        """학습 진행 상태"""
        try:
            self.progress_bar.setValue(value)
        except Exception as e:
            logger.error(f"❌ 학습 진행 상태 업데이트 실패: {str(e)}")
            
    def on_training_finished(self, result: Dict[str, Any]):
        """학습 완료 시"""
        try:
            if self.current_model is not None:
                self.models[self.current_model]["status"] = "활성"
                self.update_model_list()
                
            self.progress_bar.setVisible(False)
            QMessageBox.information(self, "알림", result["message"])
            
        except Exception as e:
            logger.error(f"❌ 학습 완료 처리 실패: {str(e)}")
            
    def on_training_error(self, error: str):
        """학습 오류 시"""
        try:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, "오류", f"학습 실패: {error}")
            
        except Exception as e:
            logger.error(f"❌ 학습 오류 처리 실패: {str(e)}")
