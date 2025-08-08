"""
project_planning_panel.py
- 프로젝트 기획 패널 구현
- 프로젝트 관리, 일정 관리, 작업 분배 기능 제공
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QLineEdit, QFileDialog,
    QMessageBox, QSplitter, QFrame, QToolButton,
    QTableWidget, QTableWidgetItem, QCalendarWidget,
    QComboBox, QSpinBox, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QDate
from PyQt5.QtGui import QFont, QIcon, QTextCursor, QColor, QPalette

logger = logging.getLogger(__name__)

class ProjectPlanningPanel(QWidget):
    """프로젝트 기획 패널"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # 프로젝트 데이터 초기화
        self.projects = []
        self.current_project = None
        
        # UI 설정
        self.setup_ui()
        
    def setup_ui(self):
        """UI 설정"""
        try:
            # 메인 레이아웃
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(10)
            
            # 프로젝트 목록
            self.project_list = QTableWidget()
            self.project_list.setColumnCount(4)
            self.project_list.setHorizontalHeaderLabels(["프로젝트명", "시작일", "종료일", "상태"])
            self.project_list.setSelectionBehavior(QTableWidget.SelectRows)
            self.project_list.setSelectionMode(QTableWidget.SingleSelection)
            self.project_list.itemSelectionChanged.connect(self.on_project_selected)
            layout.addWidget(self.project_list)
            
            # 프로젝트 정보 영역
            info_layout = QHBoxLayout()
            
            # 왼쪽 패널 (프로젝트 정보)
            left_panel = QWidget()
            left_layout = QVBoxLayout(left_panel)
            
            # 프로젝트명
            name_layout = QHBoxLayout()
            name_layout.addWidget(QLabel("프로젝트명:"))
            self.project_name = QLineEdit()
            name_layout.addWidget(self.project_name)
            left_layout.addLayout(name_layout)
            
            # 일정
            date_layout = QHBoxLayout()
            date_layout.addWidget(QLabel("시작일:"))
            self.start_date = QCalendarWidget()
            date_layout.addWidget(self.start_date)
            date_layout.addWidget(QLabel("종료일:"))
            self.end_date = QCalendarWidget()
            date_layout.addWidget(self.end_date)
            left_layout.addLayout(date_layout)
            
            # 상태
            status_layout = QHBoxLayout()
            status_layout.addWidget(QLabel("상태:"))
            self.status = QComboBox()
            self.status.addItems(["계획", "진행중", "완료", "보류"])
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
            self.task_list.setColumnCount(4)
            self.task_list.setHorizontalHeaderLabels(["작업명", "담당자", "기한", "완료"])
            right_layout.addWidget(self.task_list)
            
            # 작업 추가 버튼
            add_task_btn = QPushButton("작업 추가")
            add_task_btn.clicked.connect(self.add_task)
            right_layout.addWidget(add_task_btn)
            
            info_layout.addWidget(right_panel)
            layout.addLayout(info_layout)
            
            # 버튼 영역
            button_layout = QHBoxLayout()
            
            # 새 프로젝트 버튼
            new_btn = QPushButton("새 프로젝트")
            new_btn.clicked.connect(self.new_project)
            button_layout.addWidget(new_btn)
            
            # 저장 버튼
            save_btn = QPushButton("저장")
            save_btn.clicked.connect(self.save_project)
            button_layout.addWidget(save_btn)
            
            # 삭제 버튼
            delete_btn = QPushButton("삭제")
            delete_btn.clicked.connect(self.delete_project)
            button_layout.addWidget(delete_btn)
            
            layout.addLayout(button_layout)
            
        except Exception as e:
            logger.error(f"❌ UI 설정 실패: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise
            
    def new_project(self):
        """새 프로젝트 생성"""
        try:
            self.project_name.clear()
            self.start_date.setSelectedDate(QDate.currentDate())
            self.end_date.setSelectedDate(QDate.currentDate())
            self.status.setCurrentIndex(0)
            self.description.clear()
            self.task_list.setRowCount(0)
            self.current_project = None
        except Exception as e:
            logger.error(f"❌ 새 프로젝트 생성 실패: {str(e)}")
            
    def save_project(self):
        """프로젝트 저장"""
        try:
            if not self.project_name.text():
                QMessageBox.warning(self, "경고", "프로젝트명을 입력하세요.")
                return
                
            project = {
                "name": self.project_name.text(),
                "start_date": self.start_date.selectedDate().toString("yyyy-MM-dd"),
                "end_date": self.end_date.selectedDate().toString("yyyy-MM-dd"),
                "status": self.status.currentText(),
                "description": self.description.toPlainText(),
                "tasks": []
            }
            
            # 작업 목록 저장
            for row in range(self.task_list.rowCount()):
                task = {
                    "name": self.task_list.item(row, 0).text(),
                    "assignee": self.task_list.item(row, 1).text(),
                    "due_date": self.task_list.item(row, 2).text(),
                    "completed": self.task_list.cellWidget(row, 3).isChecked()
                }
                project["tasks"].append(task)
                
            # 프로젝트 목록 업데이트
            if self.current_project is None:
                self.projects.append(project)
            else:
                self.projects[self.current_project] = project
                
            self.update_project_list()
            QMessageBox.information(self, "알림", "프로젝트가 저장되었습니다.")
            
        except Exception as e:
            logger.error(f"❌ 프로젝트 저장 실패: {str(e)}")
            
    def delete_project(self):
        """프로젝트 삭제"""
        try:
            if self.current_project is None:
                QMessageBox.warning(self, "경고", "삭제할 프로젝트를 선택하세요.")
                return
                
            reply = QMessageBox.question(
                self, "확인",
                "선택한 프로젝트를 삭제하시겠습니까?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                del self.projects[self.current_project]
                self.update_project_list()
                self.new_project()
                QMessageBox.information(self, "알림", "프로젝트가 삭제되었습니다.")
                
        except Exception as e:
            logger.error(f"❌ 프로젝트 삭제 실패: {str(e)}")
            
    def add_task(self):
        """작업 추가"""
        try:
            row = self.task_list.rowCount()
            self.task_list.insertRow(row)
            
            # 작업명
            self.task_list.setItem(row, 0, QTableWidgetItem(""))
            
            # 담당자
            self.task_list.setItem(row, 1, QTableWidgetItem(""))
            
            # 기한
            self.task_list.setItem(row, 2, QTableWidgetItem(""))
            
            # 완료 여부
            checkbox = QCheckBox()
            checkbox.setChecked(False)
            self.task_list.setCellWidget(row, 3, checkbox)
            
        except Exception as e:
            logger.error(f"❌ 작업 추가 실패: {str(e)}")
            
    def on_project_selected(self):
        """프로젝트 선택 시"""
        try:
            selected = self.project_list.selectedItems()
            if not selected:
                return
                
            row = selected[0].row()
            self.current_project = row
            project = self.projects[row]
            
            self.project_name.setText(project["name"])
            self.start_date.setSelectedDate(QDate.fromString(project["start_date"], "yyyy-MM-dd"))
            self.end_date.setSelectedDate(QDate.fromString(project["end_date"], "yyyy-MM-dd"))
            self.status.setCurrentText(project["status"])
            self.description.setText(project["description"])
            
            # 작업 목록 업데이트
            self.task_list.setRowCount(0)
            for task in project["tasks"]:
                row = self.task_list.rowCount()
                self.task_list.insertRow(row)
                self.task_list.setItem(row, 0, QTableWidgetItem(task["name"]))
                self.task_list.setItem(row, 1, QTableWidgetItem(task["assignee"]))
                self.task_list.setItem(row, 2, QTableWidgetItem(task["due_date"]))
                checkbox = QCheckBox()
                checkbox.setChecked(task["completed"])
                self.task_list.setCellWidget(row, 3, checkbox)
                
        except Exception as e:
            logger.error(f"❌ 프로젝트 선택 실패: {str(e)}")
            
    def update_project_list(self):
        """프로젝트 목록 업데이트"""
        try:
            self.project_list.setRowCount(len(self.projects))
            for i, project in enumerate(self.projects):
                self.project_list.setItem(i, 0, QTableWidgetItem(project["name"]))
                self.project_list.setItem(i, 1, QTableWidgetItem(project["start_date"]))
                self.project_list.setItem(i, 2, QTableWidgetItem(project["end_date"]))
                self.project_list.setItem(i, 3, QTableWidgetItem(project["status"]))
                
        except Exception as e:
            logger.error(f"❌ 프로젝트 목록 업데이트 실패: {str(e)}") 