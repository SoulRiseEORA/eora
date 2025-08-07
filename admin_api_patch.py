# 관리자 API 패치
# 이 코드를 src/app.py의 메인 실행 부분 전에 추가하세요

@app.post("/api/admin/learn-dialog-file")
async def learn_dialog_file(request: Request, file: UploadFile = File(...)):
    """대화 파일 학습 API"""
    try:
        user = get_current_user(request)
        
        # 파일 내용 읽기
        content = await file.read()
        text_content = content.decode('utf-8', errors='ignore')
        
        if not text_content.strip():
            return {"error": "파일 내용이 비어있습니다"}
        
        # 대화 형식 파싱
        lines = text_content.strip().split('\n')
        conversations = []
        current_conv = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Q: 또는 질문: 으로 시작하는 라인
            if line.startswith(('Q:', '질문:', '사용자:')):
                if current_conv and 'answer' in current_conv:
                    conversations.append(current_conv)
                current_conv = {'question': line.split(':', 1)[1].strip()}
            
            # A: 또는 답변: 으로 시작하는 라인
            elif line.startswith(('A:', '답변:', 'AI:', 'EORA:')):
                if current_conv:
                    current_conv['answer'] = line.split(':', 1)[1].strip()
        
        # 마지막 대화 추가
        if current_conv and 'answer' in current_conv:
            conversations.append(current_conv)
        
        # 학습 데이터 저장
        learning_data = {
            "filename": file.filename,
            "type": "dialog",
            "conversations": conversations,
            "total_count": len(conversations),
            "learned_at": datetime.now().isoformat(),
            "user_id": user.get("id", "anonymous") if user else "anonymous"
        }
        
        # MongoDB에 저장
        if memories_collection is not None:
            try:
                result = memories_collection.insert_one(learning_data)
                logger.info(f"✅ 대화 학습 완료 (MongoDB): {file.filename} - {len(conversations)}개 대화")
                
                # 각 대화를 개별적으로도 저장
                for conv in conversations:
                    chat_data = {
                        "type": "learned_dialog",
                        "question": conv['question'],
                        "answer": conv['answer'],
                        "source_file": file.filename,
                        "learned_at": datetime.now(),
                        "user_id": user.get("id", "anonymous") if user else "anonymous"
                    }
                    memories_collection.insert_one(chat_data)
                
                return {
                    "success": True,
                    "message": f"대화 파일 '{file.filename}'이 성공적으로 학습되었습니다",
                    "conversations_count": len(conversations),
                    "file_id": str(result.inserted_id)
                }
            except Exception as e:
                logger.warning(f"⚠️ MongoDB 저장 실패: {e}")
        
        # 메모리에 저장 (fallback)
        if "learned_dialogs" not in memory_cache:
            memory_cache["learned_dialogs"] = []
        
        learning_data["file_id"] = str(uuid.uuid4())
        memory_cache["learned_dialogs"].append(learning_data)
        
        logger.info(f"✅ 대화 학습 완료 (메모리): {file.filename} - {len(conversations)}개 대화")
        return {
            "success": True,
            "message": f"대화 파일 '{file.filename}'이 성공적으로 학습되었습니다",
            "conversations_count": len(conversations),
            "file_id": learning_data["file_id"]
        }
        
    except Exception as e:
        logger.error(f"❌ 대화 파일 학습 오류: {e}")
        return {
            "success": False,
            "error": f"대화 파일 학습 중 오류가 발생했습니다: {str(e)}"
        }

@app.get("/api/admin/storage")
async def get_storage_stats(request: Request):
    """저장소 통계 조회"""
    try:
        user = get_current_user(request)
        if not user or not user.get('is_admin', False):
            return {"success": False, "message": "관리자 권한이 필요합니다"}
        
        storage = {
            "db_size": 0,
            "file_size": 0,
            "backup_size": 0
        }
        
        # MongoDB 크기 조회
        if db is not None:
            try:
                stats = db.command("dbStats")
                storage["db_size"] = round(stats.get("dataSize", 0) / 1024 / 1024, 2)  # MB
            except:
                pass
        
        # 백업 폴더 크기 조회
        backup_path = Path("backups")
        if backup_path.exists():
            total_size = sum(f.stat().st_size for f in backup_path.glob('**/*') if f.is_file())
            storage["backup_size"] = round(total_size / 1024 / 1024, 2)  # MB
        
        # 업로드 폴더 크기 조회
        upload_path = Path("uploads")
        if upload_path.exists():
            total_size = sum(f.stat().st_size for f in upload_path.glob('**/*') if f.is_file())
            storage["file_size"] = round(total_size / 1024 / 1024, 2)  # MB
        
        return {"success": True, "storage": storage}
        
    except Exception as e:
        logger.error(f"❌ 저장소 통계 조회 오류: {e}")
        return {"success": False, "error": str(e)} 