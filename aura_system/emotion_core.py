    async def cleanup(self):
        """리소스 정리"""
        try:
            if hasattr(self, 'initialized') and self.initialized:
                self.initialized = False
                logger.info("✅ 감정 코어 정리 완료")
        except Exception as e:
            logger.error(f"❌ 감정 코어 정리 중 오류 발생: {str(e)}") 