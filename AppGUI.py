import tkinter as tk
from tkinter import filedialog, messagebox
import time
from Database import Database
from Hash import StaticHashIndex
# ==========================================
# INTERFACE GRÁFICA (FRONTEND TKINTER)
# ==========================================

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Índice Hash Estático - Unifor")
        self.root.geometry("850x700")
        
        self.db = Database()
        self.index = StaticHashIndex()
        
        self.create_widgets()

    def create_widgets(self):
        # Frame de Carga
        frame_top = tk.LabelFrame(self.root, text="1. Carga de Dados e Configuração", padx=10, pady=10)
        frame_top.pack(fill="x", padx=10, pady=5)

        tk.Button(frame_top, text="Carregar Arquivo TXT", command=self.load_file).grid(row=0, column=0, padx=5, pady=5)
        self.lbl_file_status = tk.Label(frame_top, text="Nenhum arquivo carregado.", fg="red")
        self.lbl_file_status.grid(row=0, column=1, sticky="w")

        tk.Label(frame_top, text="Tamanho da Página (Reg/Pág):").grid(row=1, column=0, sticky="e")
        self.entry_page_size = tk.Entry(frame_top, width=10)
        self.entry_page_size.insert(0, "100")
        self.entry_page_size.grid(row=1, column=1, sticky="w")

        tk.Label(frame_top, text="Tamanho do Bucket (FR):").grid(row=2, column=0, sticky="e")
        self.entry_fr_size = tk.Entry(frame_top, width=10)
        self.entry_fr_size.insert(0, "5")
        self.entry_fr_size.grid(row=2, column=1, sticky="w")

        tk.Button(frame_top, text="Processar e Construir Índice", command=self.build_system, bg="lightblue").grid(row=3, column=0, columnspan=2, pady=10)

        # Frame de Informações e Métricas
        frame_metrics = tk.LabelFrame(self.root, text="2. Estruturas e Métricas (EPIC 6 e 7)", padx=10, pady=10)
        frame_metrics.pack(fill="x", padx=10, pady=5)

        self.txt_metrics = tk.Text(frame_metrics, height=12, width=100)
        self.txt_metrics.pack()

        # Frame de Pesquisa
        frame_search = tk.LabelFrame(self.root, text="3. Pesquisa e Comparação (EPIC 4 e 5)", padx=10, pady=10)
        frame_search.pack(fill="both", expand=True, padx=10, pady=5)

        tk.Label(frame_search, text="Chave de Busca (Palavra):").grid(row=0, column=0)
        self.entry_search = tk.Entry(frame_search, width=30)
        self.entry_search.grid(row=0, column=1, padx=5)

        tk.Button(frame_search, text="Buscar", command=self.execute_search, bg="lightgreen").grid(row=0, column=2, padx=5)

        self.txt_results = tk.Text(frame_search, height=10, width=100)
        self.txt_results.grid(row=1, column=0, columnspan=3, pady=10)

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filepath:
            try:
                total_words = self.db.load_data(filepath)
                self.lbl_file_status.config(text=f"Carregado: {total_words} palavras.", fg="green")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def build_system(self):
        if not self.db.records:
            messagebox.showwarning("Aviso", "Carregue o arquivo primeiro!")
            return

        try:
            page_size = int(self.entry_page_size.get())
            fr = int(self.entry_fr_size.get())
            if page_size <= 0 or fr <= 0:
                raise ValueError
        except:
            messagebox.showerror("Erro", "Tamanhos devem ser inteiros maiores que zero (CA05).")
            return

        # 1. Paginando
        self.db.paginate_data(page_size)

        # 2. Construindo Índice
        start_time = time.time()
        self.index.build_index(self.db, fr)
        build_time = time.time() - start_time

        # 3. Calculando Métricas
        nr = len(self.db.records)
        nb = self.index.nb
        colisoes = self.index.total_collisions
        overflows = len(self.index.overflow_buckets)

        taxa_colisao = (colisoes / nr) * 100
        taxa_overflow = (overflows / nb) * 100

        # Mostrando na interface
        self.txt_metrics.delete(1.0, tk.END)
        self.txt_metrics.insert(tk.END, f"--- DADOS DO ARQUIVO E PÁGINAS ---\n")
        self.txt_metrics.insert(tk.END, f"Total de Registros: {nr}\n")
        self.txt_metrics.insert(tk.END, f"Total de Páginas: {self.db.total_pages}\n\n")
        
        # CA07: Exibir primeira e última página (com 5 registros)
        self.txt_metrics.insert(tk.END, f"Primeira Página (ID 0): {self.db.pages[0][:5]}\n")
        self.txt_metrics.insert(tk.END, f"Última Página (ID {self.db.total_pages-1}): {self.db.pages[-1][:5]}\n\n")

        self.txt_metrics.insert(tk.END, f"--- ESTATÍSTICAS DO ÍNDICE HASH ---\n")
        self.txt_metrics.insert(tk.END, f"Tempo de Construção: {build_time:.4f} segundos\n")
        self.txt_metrics.insert(tk.END, f"Total de Buckets (NB): {nb}\n")
        self.txt_metrics.insert(tk.END, f"Taxa de Colisões: {taxa_colisao:.2f}%\n")
        self.txt_metrics.insert(tk.END, f"Taxa de Overflows: {taxa_overflow:.2f}%\n")
        
        messagebox.showinfo("Sucesso", "Páginas e Índice criados com sucesso!")

    def execute_search(self):
        key = self.entry_search.get().strip()
        if not key:
            messagebox.showwarning("Aviso", "Digite uma chave de busca.")
            return
        if not self.db.pages:
            messagebox.showwarning("Aviso", "Construa o índice primeiro.")
            return

        self.txt_results.delete(1.0, tk.END)

        # 1. Busca via Índice Hash
        start_idx = time.perf_counter()
        found_idx, page_id, bucket_addr, cost_idx = self.index.search_index(key)
        time_idx = time.perf_counter() - start_idx

        self.txt_results.insert(tk.END, f"=== PESQUISA POR ÍNDICE ===\n")
        if found_idx:
            self.txt_results.insert(tk.END, f"Status: Encontrada!\n")
            self.txt_results.insert(tk.END, f"Bucket acessado: {bucket_addr}\n")
            self.txt_results.insert(tk.END, f"Página onde o registro está: {page_id}\n")
            self.txt_results.insert(tk.END, f"Custo estimado (leitura de blocos): {cost_idx}\n")
            self.txt_results.insert(tk.END, f"Tempo de busca: {time_idx:.6f} seg\n\n")
        else:
            self.txt_results.insert(tk.END, f"Status: Não encontrada.\n\n")

        # 2. Busca via Table Scan
        start_ts = time.perf_counter()
        found_ts, page_id_ts, cost_ts = self.db.table_scan(key)
        time_ts = time.perf_counter() - start_ts

        self.txt_results.insert(tk.END, f"=== PESQUISA POR TABLE SCAN ===\n")
        if found_ts:
            self.txt_results.insert(tk.END, f"Status: Encontrada!\n")
            self.txt_results.insert(tk.END, f"Página onde o registro está: {page_id_ts}\n")
            self.txt_results.insert(tk.END, f"Custo estimado (páginas lidas): {cost_ts}\n")
            self.txt_results.insert(tk.END, f"Tempo de busca: {time_ts:.6f} seg\n\n")
        else:
            self.txt_results.insert(tk.END, f"Status: Não encontrada.\n\n")

        # 3. Comparação (HU11)
        if found_idx:
            diff_time = time_ts - time_idx
            economia_custo = ((cost_ts - cost_idx) / cost_ts) * 100 if cost_ts > 0 else 0
            
            self.txt_results.insert(tk.END, f"=== COMPARAÇÃO DE DESEMPENHO ===\n")
            self.txt_results.insert(tk.END, f"Diferença de tempo: O índice foi {diff_time:.6f} seg mais rápido.\n")
            self.txt_results.insert(tk.END, f"Economia no Custo (I/O): {economia_custo:.2f}% a menos de leituras no disco.\n")