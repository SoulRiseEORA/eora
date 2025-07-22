import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from aura_system.meta_store import get_all_atom_ids, get_atoms_by_ids

print("🔎 회상 시스템 진단 시작")
atom_ids = get_all_atom_ids()
print(f"📄 MongoDB 메모 개수: {len(atom_ids)}")

some_ids = atom_ids[:3]
atoms = get_atoms_by_ids(some_ids)

for a in atoms:
    print(f"🧠 {a.get('user_input', '')[:30]} → {a.get('response', '')[:30]}")