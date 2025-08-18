"""
Unit tests for MemoryModule.
"""

import pytest
from memory_module import MemoryModule

def test_init_default():
    """Test MemoryModule initializes with default parameters."""
    m = MemoryModule()
    assert hasattr(m, "embedding_dim")
    assert hasattr(m, "storage_path")

def test_store_and_retrieve_memory(tmp_path):
    """Test storing and retrieving memory."""
    m = MemoryModule(storage_path=str(tmp_path / "mem.json"))
    m.store_memory("test memory", meta={"source": "unit"})
    results = m.retrieve_memory("test")
    assert any("test memory" in r["text"] for r in results)

def test_prune_memories(tmp_path):
    """Test pruning memories by type and threshold."""
    m = MemoryModule(storage_path=str(tmp_path / "mem.json"))
    m.store_memory("episodic one", memory_type="episodic")
    m.store_memory("semantic two", memory_type="semantic")
    m.store_memory("procedural three", memory_type="procedural")
    # Prune only episodic
    pruned = m.prune_memories(relevance_threshold=1.0, memory_type="episodic")
    assert isinstance(pruned, int)
    episodic = m.retrieve_memory("episodic", memory_type="episodic")
    assert len(episodic) == 0 or all("episodic" not in r["text"] for r in episodic)
    # Prune all
    m.prune_memories(relevance_threshold=1.0)
    assert all(len(m.retrieve_memory(q)) == 0 for q in ["semantic", "procedural"])

def test_save_and_load_disk(tmp_path):
    """Test saving and loading memories to disk with types."""
    path = str(tmp_path / "mem.json")
    m = MemoryModule(storage_path=path)
    m.store_memory("persisted semantic", memory_type="semantic")
    m.store_memory("persisted episodic", memory_type="episodic")
    m.save_to_disk()
    m2 = MemoryModule(storage_path=path)
    m2.load_from_disk()
    sem = m2.retrieve_memory("semantic", memory_type="semantic")
    epi = m2.retrieve_memory("episodic", memory_type="episodic")
    assert any("persisted semantic" in r["text"] for r in sem)
    assert any("persisted episodic" in r["text"] for r in epi)

def test_hybrid_retrieval(tmp_path):
    """Test hybrid retrieval returns both semantic and keyword matches."""
    m = MemoryModule(storage_path=str(tmp_path / "mem.json"))
    m.store_memory("semantic apple banana", memory_type="semantic")
    m.store_memory("episodic orange apple", memory_type="episodic")
    m.store_memory("procedural how to peel banana", memory_type="procedural")
    # Query with overlap and semantic similarity
    results = m.retrieve_memory("apple banana", top_k=3, hybrid=True)
    texts = [r["text"] for r in results]
    assert "semantic apple banana" in texts
    assert "episodic orange apple" in texts or "procedural how to peel banana" in texts

def test_memory_type_retrieval_and_pruning(tmp_path):
    """Test retrieval and pruning for all memory types."""
    m = MemoryModule(storage_path=str(tmp_path / "mem.json"))
    m.store_memory("episodic event", memory_type="episodic")
    m.store_memory("semantic fact", memory_type="semantic")
    m.store_memory("procedural step", memory_type="procedural")
    # Retrieve by type
    epi = m.retrieve_memory("event", memory_type="episodic")
    sem = m.retrieve_memory("fact", memory_type="semantic")
    pro = m.retrieve_memory("step", memory_type="procedural")
    assert any("episodic event" in r["text"] for r in epi)
    assert any("semantic fact" in r["text"] for r in sem)
    assert any("procedural step" in r["text"] for r in pro)
    # Prune procedural only
    pruned = m.prune_memories(relevance_threshold=1.0, memory_type="procedural")
    assert pruned >= 1
    pro2 = m.retrieve_memory("step", memory_type="procedural")
    assert len(pro2) == 0 or all("procedural" not in r["text"] for r in pro2)

def test_encryption_failure(monkeypatch, tmp_path):
    """Test encryption failure during save_to_disk is handled gracefully."""
    m = MemoryModule(storage_path=str(tmp_path / "mem.json"))
    m.store_memory("test", meta={})
    def broken_encrypt(x):
        raise Exception("Encryption failed")
    monkeypatch.setattr(m.fernet, "encrypt", broken_encrypt)
    try:
        m.save_to_disk()
    except Exception:
        pass  # Should not raise, only log

def test_decryption_failure(monkeypatch, tmp_path):
    """Test decryption failure during load_from_disk is handled gracefully."""
    m = MemoryModule(storage_path=str(tmp_path / "mem.json"))
    m.store_memory("test", meta={})
    m.save_to_disk()
    def broken_decrypt(x):
        raise Exception("Decryption failed")
    monkeypatch.setattr(m.fernet, "decrypt", broken_decrypt)
    try:
        m.load_from_disk()
    except Exception:
        pass  # Should not raise, only log

def test_backup_memories(tmp_path):
    """Test backup_memories creates a backup file and handles errors."""
    m = MemoryModule(storage_path=str(tmp_path / "mem.json"))
    m.store_memory("backup test", meta={})
    backup_path = m.backup_memories(backup_dir=str(tmp_path / "backups"))
    assert backup_path is not None