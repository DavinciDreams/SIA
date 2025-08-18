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