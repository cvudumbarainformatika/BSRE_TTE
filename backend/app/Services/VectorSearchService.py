import math
import re
import hashlib
from typing import List

class VectorSearchService:
    """
    Service untuk menghasilkan embedding vektor 1536 dimensi
    untuk mendukung semantic & text search pada PostgreSQL dengan pgvector.
    Mendukung embedding lokal deterministik berdimensi 1536 (standar OpenAI text-embedding-ada-002/3-small).
    """
    DIMENSION = 1536

    @classmethod
    def generate_embedding(cls, text: str) -> List[float]:
        """
        Menghasilkan representasi vektor ternormalisasi (L2 norm = 1.0)
        dengan dimensi 1536 dari teks dokumen rekam medis.
        """
        if not text:
            return [0.0] * cls.DIMENSION

        # Tokenize and clean text
        words = re.findall(r'\b\w+\b', text.lower())
        vec = [0.0] * cls.DIMENSION
        
        for idx, word in enumerate(words):
            # Compute multiple deterministic hash projections
            h = int(hashlib.sha256(word.encode('utf-8')).hexdigest(), 16)
            pos1 = h % cls.DIMENSION
            pos2 = (h >> 16) % cls.DIMENSION
            pos3 = (h >> 32) % cls.DIMENSION
            
            weight = 1.0 / math.log(idx + 3) # position decay
            vec[pos1] += weight
            vec[pos2] += weight * 0.5
            vec[pos3] -= weight * 0.3

        # L2 Normalize
        sq_sum = sum(x * x for x in vec)
        norm = math.sqrt(sq_sum) if sq_sum > 0 else 1.0
        return [float(x / norm) for x in vec]

vector_service = VectorSearchService()
