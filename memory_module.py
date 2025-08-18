import logging
import numpy as np
import os
import json
from config import VECTOR_DB, PINECONE_API_KEY, PINECONE_ENV, MEMORY_STORAGE_PATH, SIA_ENCRYPTION_KEY
from cryptography.fernet import Fernet, InvalidToken
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import faiss
except ImportError:
    faiss = None

try:
    import pinecone
except ImportError:
    pinecone = None

class MemoryModule:
    """
    Core memory management module for SIA.
    All persistent memory data is encrypted at rest using Fernet symmetric encryption.

    Now supports persistent storage of memories and metadata to disk using JSON.
    Storage location is configurable via config.py (MEMORY_STORAGE_PATH).

    Responsibilities:
    - Stores, retrieves, and manages persistent and transient data as described in the PRD.
    - Provides interfaces for other modules to access and update memory.
    - Ensures data consistency and efficient access patterns.
    """

    def __init__(self, embedding_dim=384, storage_path=None):
        """
        Initialize the MemoryModule with vector DB integration (FAISS or Pinecone) and persistent storage.
        All persistent memory data is encrypted at rest.

        Args:
            embedding_dim (int): Dimension of the embedding vectors.
            storage_path (str, optional): Path to store memory data. Defaults to MEMORY_STORAGE_PATH from config.
        """
        self.embedding_dim = embedding_dim
        # Each memory is a dict: {"text": ..., "type": ..., "meta": ...}
        self.memories = []
        self.vector_db = VECTOR_DB.lower()
        self.index = None
        self.pinecone_index = None
        self.storage_path = storage_path or MEMORY_STORAGE_PATH

        # Setup encryption
        if not SIA_ENCRYPTION_KEY:
            logger.error("SIA_ENCRYPTION_KEY is not set. Generate one with Fernet.generate_key() and set as env variable.")
            raise ValueError("SIA_ENCRYPTION_KEY is required for encryption.")
        try:
            self.fernet = Fernet(SIA_ENCRYPTION_KEY.encode() if isinstance(SIA_ENCRYPTION_KEY, str) else SIA_ENCRYPTION_KEY)
        except Exception as e:
            logger.error(f"Invalid SIA_ENCRYPTION_KEY: {e}", exc_info=True)
            raise

        if self.vector_db == "faiss":
            if faiss:
                self.index = faiss.IndexFlatL2(embedding_dim)
            else:
                logger.error("FAISS is not installed but selected as vector DB.")
                raise ImportError("FAISS is not installed but selected as vector DB.")
        elif self.vector_db == "pinecone":
            if pinecone:
                try:
                    if not pinecone.list_indexes():
                        pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
                    index_name = "sia-memory"
                    if index_name not in pinecone.list_indexes():
                        pinecone.create_index(index_name, dimension=embedding_dim)
                    self.pinecone_index = pinecone.Index(index_name)
                except Exception as e:
                    logger.error(f"Error initializing Pinecone: {e}", exc_info=True)
                    raise
            else:
                logger.error("Pinecone is not installed but selected as vector DB.")
                raise ImportError("Pinecone is not installed but selected as vector DB.")

        self.load_from_disk()

    def _embed(self, text):
        """
        Generate an embedding for the given text.
        Placeholder: returns a random vector.

        Args:
            text (str): Input text to embed.

        Returns:
            np.ndarray: Embedding vector.
        """
        # Replace with real embedding model (e.g., Sentence Transformers) when available
        np.random.seed(abs(hash(text)) % (2**32))
        return np.random.rand(self.embedding_dim).astype('float32')

    def store_memory(self, text, meta=None, memory_type="semantic"):
        """
        Store a memory with its embedding in the configured vector DB and persist to disk.

        Args:
            text (str): The memory content.
            meta (dict, optional): Additional metadata.
            memory_type (str): Type of memory ("episodic", "semantic", "procedural").

        Returns:
            int: Index of the stored memory.
        Includes error handling and logging.
        """
        try:
            embedding = self._embed(text)
            if self.vector_db == "faiss" and self.index:
                self.index.add(np.expand_dims(embedding, axis=0))
            elif self.vector_db == "pinecone" and self.pinecone_index:
                idx = str(len(self.memories))
                self.pinecone_index.upsert([(idx, embedding.tolist())])
            mem = {
                "text": text,
                "type": memory_type,
                "meta": meta or {}
            }
            self.memories.append(mem)
            self.save_to_disk()
            logger.info("Memory stored successfully.")
            return len(self.memories) - 1
        except Exception as e:
            logger.error(f"Error storing memory: {e}", exc_info=True)
            return -1

    def retrieve_memory(self, query, top_k=5, memory_type=None, hybrid=True):
        """
        Retrieve memories most semantically similar to the query using hybrid retrieval (vector + keyword).

        Args:
            query (str): Query text.
            top_k (int): Number of top results to return.
            memory_type (str, optional): Filter by memory type ("episodic", "semantic", "procedural").
            hybrid (bool): If True, combine vector search with keyword search.

        Returns:
            list of dict: Each dict contains "text", "type", "meta", "score".
        Includes error handling and logging.
        """
        try:
            if len(self.memories) == 0:
                return []
            # Filter by memory type if specified
            filtered = [
                (i, m) for i, m in enumerate(self.memories)
                if memory_type is None or m.get("type", "semantic") == memory_type
            ]
            if not filtered:
                return []
            idx_map = {i: orig_idx for i, (orig_idx, _) in enumerate(filtered)}
            texts = [m["text"] for _, m in filtered]

            # Vector search
            query_vec = self._embed(query)
            results = []
            if self.vector_db == "faiss" and self.index:
                # Build a temporary index for filtered memories if needed
                if len(filtered) != len(self.memories):
                    # Re-embed filtered memories for temp index
                    import faiss
                    temp_index = faiss.IndexFlatL2(self.embedding_dim)
                    for _, m in filtered:
                        temp_index.add(np.expand_dims(self._embed(m["text"]), axis=0))
                    D, I = temp_index.search(np.expand_dims(query_vec, axis=0), min(top_k, len(filtered)))
                else:
                    D, I = self.index.search(np.expand_dims(query_vec, axis=0), min(top_k, len(filtered)))
                for idx, dist in zip(I[0], D[0]):
                    orig_idx = idx_map.get(idx, idx)
                    m = self.memories[orig_idx]
                    score = float(-dist)
                    results.append({"text": m["text"], "type": m.get("type"), "meta": m.get("meta"), "score": score})
            elif self.vector_db == "pinecone" and self.pinecone_index:
                # Pinecone does not support sub-indexing, so filter after retrieval
                query_results = self.pinecone_index.query(
                    vector=query_vec.tolist(), top_k=top_k * 2, include_values=False, include_metadata=False
                )
                for match in query_results.matches:
                    idx = int(match.id)
                    if idx < len(self.memories):
                        m = self.memories[idx]
                        if memory_type is None or m.get("type", "semantic") == memory_type:
                            score = float(match.score)
                            results.append({"text": m["text"], "type": m.get("type"), "meta": m.get("meta"), "score": score})
                    if len(results) >= top_k:
                        break

            # Keyword search (simple scoring: count of query words in memory text)
            if hybrid:
                query_words = set(query.lower().split())
                keyword_scores = []
                for _, m in filtered:
                    text_words = set(m["text"].lower().split())
                    overlap = len(query_words & text_words)
                    if overlap > 0:
                        keyword_scores.append({
                            "text": m["text"],
                            "type": m.get("type"),
                            "meta": m.get("meta"),
                            "score": float(overlap) + 0.01  # Ensure keyword matches are not zero
                        })
                # Merge and deduplicate by text, prefer higher score
                all_results = {r["text"]: r for r in results}
                for k in keyword_scores:
                    if k["text"] in all_results:
                        all_results[k["text"]]["score"] = max(all_results[k["text"]]["score"], k["score"])
                    else:
                        all_results[k["text"]] = k
                # Sort by score descending
                sorted_results = sorted(all_results.values(), key=lambda x: x["score"], reverse=True)
                return sorted_results[:top_k]
            else:
                # Only vector results
                return results[:top_k]
        except Exception as e:
            logger.error(f"Error retrieving memory: {e}", exc_info=True)
            return []

    def prune_memories(self, relevance_threshold=-0.5, memory_type=None):
        """
        Prune memories with similarity scores below the relevance threshold.

        Optionally restricts pruning to a specific memory_type ("episodic", "semantic", "procedural").

        Args:
            relevance_threshold (float): Minimum similarity score to keep.
            memory_type (str, optional): Only prune memories of this type.

        Returns:
            int: Number of memories pruned.
        """
        if not self.index or len(self.memories) == 0:
            return 0
        # Filter by memory type if specified
        indices = [
            i for i, m in enumerate(self.memories)
            if memory_type is None or m.get("type", "semantic") == memory_type
        ]
        if not indices:
            return 0
        # Use the centroid as a reference for relevance
        all_embeddings = self.index.reconstruct_n(0, len(self.memories))
        centroid = np.mean([all_embeddings[i] for i in indices], axis=0, keepdims=True)
        D, _ = self.index.search(centroid, len(self.memories))
        to_prune = [i for i, dist in enumerate(D[0]) if -dist < relevance_threshold and (memory_type is None or self.memories[i].get("type", "semantic") == memory_type)]
        for i in sorted(to_prune, reverse=True):
            del self.memories[i]
            if self.index:
                self.index.remove_ids(np.array([i], dtype='int64'))
        self.save_to_disk()
        return len(to_prune)

    def inject_memory(self, text, meta=None, memory_type="semantic"):
        """
        Manually inject a memory (bypassing embedding/index) and persist to disk.

        Args:
            text (str): The memory content.
            meta (dict, optional): Additional metadata.
            memory_type (str): Type of memory.

        Returns:
            int: Index of the injected memory.
        """
        mem = {
            "text": text,
            "type": memory_type,
            "meta": meta or {}
        }
        self.memories.append(mem)
        self.save_to_disk()
        return len(self.memories) - 1

    def get_memory(self, idx):
        """
        Retrieve a memory dict by index.

        Args:
            idx (int): Index of the memory.

        Returns:
            dict: Memory dict with "text", "type", "meta".
        """
        if 0 <= idx < len(self.memories):
            return self.memories[idx]
        return None

    def save_to_disk(self):
        """
        Persist all memories to disk as encrypted JSON.
        The file is stored at self.storage_path.
        Includes error handling and logging.
        Audit log is written for each save operation.
        """
        try:
            data = {
                "memories": self.memories
            }
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            plaintext = json.dumps(data, indent=2).encode("utf-8")
            ciphertext = self.fernet.encrypt(plaintext)
            with open(self.storage_path, "wb") as f:
                f.write(ciphertext)
            logger.info(f"Memories saved (encrypted) to disk at {self.storage_path}")
            self._audit_log("save_to_disk", {"storage_path": self.storage_path, "memory_count": len(self.memories)})
        except Exception as e:
            logger.error(f"Error saving memories to disk: {e}", exc_info=True)
            self._audit_log("save_to_disk_error", {"error": str(e)})

    def load_from_disk(self):
        """
        Load memories from disk if the file exists.
        The file is loaded from self.storage_path.
        Includes error handling and logging.
        Audit log is written for each load operation.
        """
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, "rb") as f:
                    ciphertext = f.read()
                    try:
                        plaintext = self.fernet.decrypt(ciphertext)
                        data = json.loads(plaintext.decode("utf-8"))
                        self.memories = data.get("memories", [])
                        logger.info(f"Memories loaded (decrypted) from disk at {self.storage_path}")
                        self._audit_log("load_from_disk", {"storage_path": self.storage_path, "memory_count": len(self.memories)})
                    except InvalidToken:
                        logger.error("Failed to decrypt memory storage file. Invalid encryption key or corrupted file.", exc_info=True)
                        self.memories = []
                        self._audit_log("load_from_disk_error", {"error": "InvalidToken"})
        except Exception as e:
            logger.error(f"Error loading memories from disk: {e}", exc_info=True)
            self._audit_log("load_from_disk_error", {"error": str(e)})
    def backup_memories(self, backup_dir="./sia_data/backups"):
        """
        Create a timestamped backup of the encrypted memory storage file.
        """
        import shutil
        import datetime
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        backup_path = os.path.join(backup_dir, f"memories_{timestamp}.bak")
        try:
            shutil.copy2(self.storage_path, backup_path)
            self._audit_log("backup_memories", {"backup_path": backup_path})
            logger.info(f"Memory backup created at {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Error creating memory backup: {e}", exc_info=True)
            self._audit_log("backup_memories_error", {"error": str(e)})
            return None