class Database:
    def __init__(self):
        self.records = []
        self.pages =[] # Lista de páginas (cada página é uma lista de registros)
        self.page_size = 0
        self.total_pages = 0

    def load_data(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # Cada linha é tratada como um registro/chave única
                self.records = [line.strip() for line in f if line.strip()]
            return len(self.records)
        except Exception as e:
            raise Exception(f"Erro ao ler arquivo: {e}")

    def paginate_data(self, page_size):
        self.page_size = page_size
        self.pages =[]
        # HU03: Dividir registros em páginas
        for i in range(0, len(self.records), page_size):
            self.pages.append(self.records[i:i+page_size])
        self.total_pages = len(self.pages)

    def table_scan(self, search_key):
        # HU10: Table scan
        pages_read = 0
        for page_idx, page in enumerate(self.pages):
            pages_read += 1
            if search_key in page:
                return True, page_idx, pages_read
        return False, -1, pages_read
