"""
ai_manager_macro_tab.py
- AI 매니저 매크로 탭 구현
- 매크로 자동화, 작업 스케줄링, 이벤트 처리 기능 제공
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
    QTableWidget, QTableWidgetItem, QCalendarWidget,
    QComboBox, QSpinBox, QCheckBox, QTimeEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QTime
from PyQt5.QtGui import QFont, QIcon, QTextCursor, QColor, QPalette

logger = logging.getLogger(__name__)

class MacroWorker(QThread):
    """매크로 작업자 스레드"""
    
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, macro_data: Dict[str, Any]):
        super().__init__()
        self.macro_data = macro_data
        self.loop = None
        
    def run(self):
        """작업 실행"""
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # 매크로 실행
            result = self.loop.run_until_complete(self.execute_macro())
            self.finished.emit(result)
            
        except Exception as e:
            logger.error(f"❌ 매크로 실행 실패: {str(e)}")
            self.error.emit(str(e))
        finally:
            if self.loop:
                self.loop.close()
                
    async def execute_macro(self) -> Dict[str, Any]:
        """매크로 실행"""
        try:
            # 매크로 실행 로직
            result = {
                "status": "success",
                "message": "매크로가 성공적으로 실행되었습니다.",
                "timestamp": datetime.now().isoformat()
            }
            return result
            
        except Exception as e:
            logger.error(f"❌ 매크로 실행 실패: {str(e)}")
            raise

class AIManagerMacroTab(QWidget):
    """AI 매니저 매크로 탭"""
    
    def __init__(self, parent=None, global_logger=None):
        super().__init__(parent)
        self.parent = parent
        self.global_logger = global_logger
        
        # 매크로 데이터 초기화
        self.macros = []
        self.current_macro = None
        
        # UI 설정
        self.setup_ui()
        
    def setup_ui(self):
        """UI 설정"""
        try:
            # 메인 레이아웃
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(10)
            
            # 매크로 목록
            self.macro_list = QTableWidget()
            self.macro_list.setColumnCount(4)
            self.macro_list.setHorizontalHeaderLabels(["매크로명", "트리거", "상태", "마지막 실행"])
            self.macro_list.setSelectionBehavior(QTableWidget.SelectRows)
            self.macro_list.setSelectionMode(QTableWidget.SingleSelection)
            self.macro_list.itemSelectionChanged.connect(self.on_macro_selected)
            layout.addWidget(self.macro_list)
            
            # 매크로 정보 영역
            info_layout = QHBoxLayout()
            
            # 왼쪽 패널 (매크로 정보)
            left_panel = QWidget()
            left_layout = QVBoxLayout(left_panel)
            
            # 매크로명
            name_layout = QHBoxLayout()
            name_layout.addWidget(QLabel("매크로명:"))
            self.macro_name = QLineEdit()
            name_layout.addWidget(self.macro_name)
            left_layout.addLayout(name_layout)
            
            # 트리거 설정
            trigger_layout = QHBoxLayout()
            trigger_layout.addWidget(QLabel("트리거:"))
            self.trigger_type = QComboBox()
            self.trigger_type.addItems(["수동", "시간", "이벤트"])
            self.trigger_type.currentTextChanged.connect(self.on_trigger_changed)
            trigger_layout.addWidget(self.trigger_type)
            
            # 시간 설정
            self.time_trigger = QTimeEdit()
            self.time_trigger.setTime(QTime.currentTime())
            self.time_trigger.setVisible(False)
            trigger_layout.addWidget(self.time_trigger)
            
            left_layout.addLayout(trigger_layout)
            
            # 상태
            status_layout = QHBoxLayout()
            status_layout.addWidget(QLabel("상태:"))
            self.status = QComboBox()
            self.status.addItems(["활성", "비활성", "일시중지"])
            status_layout.addWidget(self.status)
            left_layout.addLayout(status_layout)
            
            # 설명
            left_layout.addWidget(QLabel("설명:"))
            self.description = QTextEdit()
            left_layout.addWidget(self.description)
            
            info_layout.addWidget(left_panel)
            
            # 오른쪽 패널 (작업 목록)
            right_panel = QWidget()
            right_layout = QVBoxLayout(right_panel)
            
            # 작업 목록
            right_layout.addWidget(QLabel("작업 목록:"))
            self.task_list = QTableWidget()
            self.task_list.setColumnCount(3)
            self.task_list.setHorizontalHeaderLabels(["작업명", "순서", "상태"])
            right_layout.addWidget(self.task_list)
            
            # 작업 추가 버튼
            add_task_btn = QPushButton("작업 추가")
            add_task_btn.clicked.connect(self.add_task)
            right_layout.addWidget(add_task_btn)
            
            info_layout.addWidget(right_panel)
            layout.addLayout(info_layout)
            
            # 버튼 영역
            button_layout = QHBoxLayout()
            
            # 새 매크로 버튼
            new_btn = QPushButton("새 매크로")
            new_btn.clicked.connect(self.new_macro)
            button_layout.addWidget(new_btn)
            
            # 저장 버튼
            save_btn = QPushButton("저장")
            save_btn.clicked.connect(self.save_macro)
            button_layout.addWidget(save_btn)
            
            # 삭제 버튼
            delete_btn = QPushButton("삭제")
            delete_btn.clicked.connect(self.delete_macro)
            button_layout.addWidget(delete_btn)
            
            # 실행 버튼
            run_btn = QPushButton("실행")
            run_btn.clicked.connect(self.run_macro)
            button_layout.addWidget(run_btn)
            
            layout.addLayout(button_layout)
            
        except Exception as e:
            logger.error(f"❌ UI 설정 실패: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise
            
    def new_macro(self):
        """새 매크로 생성"""
        try:
            self.macro_name.clear()
            self.trigger_type.setCurrentIndex(0)
            self.time_trigger.setTime(QTime.currentTime())
            self.status.setCurrentIndex(0)
            self.description.clear()
            self.task_list.setRowCount(0)
            self.current_macro = None
        except Exception as e:
            logger.error(f"❌ 새 매크로 생성 실패: {str(e)}")
            
    def save_macro(self):
        """매크로 저장"""
        try:
            if not self.macro_name.text():
                QMessageBox.warning(self, "경고", "매크로명을 입력하세요.")
                return
                
            macro = {
                "name": self.macro_name.text(),
                "trigger_type": self.trigger_type.currentText(),
                "trigger_time": self.time_trigger.time().toString("HH:mm") if self.trigger_type.currentText() == "시간" else None,
                "status": self.status.currentText(),
                "description": self.description.toPlainText(),
                "tasks": []
            }
            
            # 작업 목록 저장
            for row in range(self.task_list.rowCount()):
                task = {
                    "name": self.task_list.item(row, 0).text(),
                    "order": int(self.task_list.item(row, 1).text()),
                    "status": self.task_list.item(row, 2).text()
                }
                macro["tasks"].append(task)
                
            # 매크로 목록 업데이트
            if self.current_macro is None:
                self.macros.append(macro)
            else:
                self.macros[self.current_macro] = macro
                
            self.update_macro_list()
            QMessageBox.information(self, "알림", "매크로가 저장되었습니다.")
            
        except Exception as e:
            logger.error(f"❌ 매크로 저장 실패: {str(e)}")
            
    def delete_macro(self):
        """매크로 삭제"""
        try:
            if self.current_macro is None:
                QMessageBox.warning(self, "경고", "삭제할 매크로를 선택하세요.")
                return
                
            reply = QMessageBox.question(
                self, "확인",
                "선택한 매크로를 삭제하시겠습니까?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                del self.macros[self.current_macro]
                self.update_macro_list()
                self.new_macro()
                QMessageBox.information(self, "알림", "매크로가 삭제되었습니다.")
                
        except Exception as e:
            logger.error(f"❌ 매크로 삭제 실패: {str(e)}")
            
    def add_task(self):
        """작업 추가"""
        try:
            row = self.task_list.rowCount()
            self.task_list.insertRow(row)
            
            # 작업명
            self.task_list.setItem(row, 0, QTableWidgetItem(""))
            
            # 순서
            self.task_list.setItem(row, 1, QTableWidgetItem(str(row + 1)))
            
            # 상태
            self.task_list.setItem(row, 2, QTableWidgetItem("대기"))
            
        except Exception as e:
            logger.error(f"❌ 작업 추가 실패: {str(e)}")
            
    def on_macro_selected(self):
        """매크로 선택 시"""
        try:
            selected = self.macro_list.selectedItems()
            if not selected:
                return
                
            row = selected[0].row()
            self.current_macro = row
            macro = self.macros[row]
            
            self.macro_name.setText(macro["name"])
            self.trigger_type.setCurrentText(macro["trigger_type"])
            if macro["trigger_time"]:
                self.time_trigger.setTime(QTime.fromString(macro["trigger_time"], "HH:mm"))
            self.status.setCurrentText(macro["status"])
            self.description.setText(macro["description"])
            
            # 작업 목록 업데이트
            self.task_list.setRowCount(0)
            for task in macro["tasks"]:
                row = self.task_list.rowCount()
                self.task_list.insertRow(row)
                self.task_list.setItem(row, 0, QTableWidgetItem(task["name"]))
                self.task_list.setItem(row, 1, QTableWidgetItem(str(task["order"])))
                self.task_list.setItem(row, 2, QTableWidgetItem(task["status"]))
                
        except Exception as e:
            logger.error(f"❌ 매크로 선택 실패: {str(e)}")
            
    def update_macro_list(self):
        """매크로 목록 업데이트"""
        try:
            self.macro_list.setRowCount(len(self.macros))
            for i, macro in enumerate(self.macros):
                self.macro_list.setItem(i, 0, QTableWidgetItem(macro["name"]))
                self.macro_list.setItem(i, 1, QTableWidgetItem(macro["trigger_type"]))
                self.macro_list.setItem(i, 2, QTableWidgetItem(macro["status"]))
                self.macro_list.setItem(i, 3, QTableWidgetItem(macro.get("last_run", "-")))
                
        except Exception as e:
            logger.error(f"❌ 매크로 목록 업데이트 실패: {str(e)}")
            
    def on_trigger_changed(self, trigger_type: str):
        """트리거 타입 변경 시"""
        try:
            self.time_trigger.setVisible(trigger_type == "시간")
        except Exception as e:
            logger.error(f"❌ 트리거 타입 변경 실패: {str(e)}")
            
    def run_macro(self):
        """매크로 실행"""
        try:
            if self.current_macro is None:
                QMessageBox.warning(self, "경고", "실행할 매크로를 선택하세요.")
                return
                
            macro = self.macros[self.current_macro]
            
            # 매크로 작업자 생성 및 실행
            worker = MacroWorker(macro)
            worker.finished.connect(self.on_macro_finished)
            worker.error.connect(self.on_macro_error)
            worker.start()
            
        except Exception as e:
            logger.error(f"❌ 매크로 실행 실패: {str(e)}")
            
    def on_macro_finished(self, result: Dict[str, Any]):
        """매크로 실행 완료 시"""
        try:
            if self.current_macro is not None:
                self.macros[self.current_macro]["last_run"] = result["timestamp"]
                self.update_macro_list()
                
            if self.global_logger:
                self.global_logger.append(f"✅ 매크로 실행 완료: {result['message']}")
                
        except Exception as e:
            logger.error(f"❌ 매크로 실행 완료 처리 실패: {str(e)}")
            
    def on_macro_error(self, error: str):
        """매크로 실행 오류 시"""
        try:
            if self.global_logger:
                self.global_logger.append(f"❌ 매크로 실행 실패: {error}")
                
        except Exception as e:
            logger.error(f"❌ 매크로 오류 처리 실패: {str(e)}") 