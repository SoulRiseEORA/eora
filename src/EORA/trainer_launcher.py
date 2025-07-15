import os
from EORA.offline_trainer import OfflineTrainer

def run_offline_training():
    trainer = OfflineTrainer()
    trainer.load_memory("eora_manifest.yaml")
    trainer.run_loop()

if __name__ == "__main__":
    run_offline_training()