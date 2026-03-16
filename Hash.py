import math
from Database import Database
class StaticHashIndex:
    def __init__(self):
        self.buckets = {}
        self.nb = 0 # Número de buckets
        self.fr = 0 # Fator de bloco (Capacidade do bucket)
        self.total_collisions = 0
        self.overflow_buckets = set()

    def deterministic_hash(self, key):
        # RNF05: Função Hash determinística. 
        # Algoritmo djb2 (simples e distribui bem strings)
        hash_val = 5381
        for char in key:
            hash_val = ((hash_val << 5) + hash_val) + ord(char)
        return hash_val % self.nb

    def build_index(self, db: Database, fr: int):
        nr = len(db.records)
        self.fr = fr
        # RN08: NB > NR / FR
        self.nb = math.ceil(nr / fr) + 1 # +1 para garantir que é maior
        
        self.buckets = {i:[] for i in range(self.nb)}
        self.total_collisions = 0
        self.overflow_buckets = set()

        # HU06: Construir índice percorrendo páginas
        for page_id, page in enumerate(db.pages):
            for key in page:
                bucket_addr = self.deterministic_hash(key)
                
                # Regra do Professor (RN14): Colisão é considerada quando bucket enche.
                if len(self.buckets[bucket_addr]) >= self.fr:
                    self.total_collisions += 1
                    self.overflow_buckets.add(bucket_addr)
                
                # Armazena tupla: (Chave, ID da Página)
                self.buckets[bucket_addr].append((key, page_id))

    def search_index(self, search_key):
        # HU09: Busca usando índice
        bucket_addr = self.deterministic_hash(search_key)
        bucket = self.buckets.get(bucket_addr,[])
        
        # Custo: 1 leitura de índice (bucket principal) + leituras de overflow + 1 leitura da página de dados
        # Vamos estimar que cada bloco extra no bucket (acima de FR) conte como leitura de bloco de overflow
        blocos_overflow = math.ceil(len(bucket) / self.fr) if len(bucket) > 0 else 0
        
        for key, page_id in bucket:
            if key == search_key:
                # Custo = blocos lidos no índice + 1 (a página de dados)
                custo_estimado = blocos_overflow + 1 
                return True, page_id, bucket_addr, custo_estimado
        
        return False, -1, bucket_addr, blocos_overflow
