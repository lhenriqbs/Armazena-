import os
import sqlite3
import customtkinter as ctk
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image  # Certifique-se de ter o Pillow instalado: pip install pillow

# ==========================================
# CONFIGURAÇÃO DO DIRETÓRIO BASE
# ==========================================
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))

# ==========================================
# CONFIGURAÇÃO DO BANCO DE DADOS
# ==========================================
BANCO_DADOS = os.path.join(DIRETORIO_ATUAL, "estoque_obra.db")

def inicializar_banco():
    conexao = sqlite3.connect(BANCO_DADOS)
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL,
            quantidade INTEGER DEFAULT 0,
            unidade TEXT,
            status TEXT,
            responsavel TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs_auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            acao TEXT NOT NULL,
            data_hora DATETIME DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conexao.commit()
    conexao.close()

def registrar_log(usuario, acao):
    conexao = sqlite3.connect(BANCO_DADOS)
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO logs_auditoria (usuario, acao) VALUES (?, ?)", (usuario, acao))
    conexao.commit()
    conexao.close()

# ==========================================
# USUÁRIOS (via users.env)
# ==========================================
caminho_config = os.path.join(DIRETORIO_ATUAL, "users.env")
load_dotenv(dotenv_path=caminho_config)

def carregar_usuarios():
    usuarios = {}
    
    u_admin = os.getenv("USUARIO_ADMIN")
    s_admin = os.getenv("SENHA_ADMIN")
    p_admin = os.getenv("PERFIL_ADMIN", "admin")
    if u_admin and s_admin:
        usuarios[u_admin.strip()] = {"senha": s_admin.strip(), "perfil": p_admin.strip()}

    u_compras = os.getenv("USUARIO_COMPRAS")
    s_compras = os.getenv("SENHA_COMPRAS")
    p_compras = os.getenv("PERFIL_COMPRAS", "operario_entrada")
    if u_compras and s_compras:
        usuarios[u_compras.strip()] = {"senha": s_compras.strip(), "perfil": p_compras.strip()}

    u_saida = os.getenv("USUARIO_SAIDA")
    s_saida = os.getenv("SENHA_SAIDA")
    p_saida = os.getenv("PERFIL_SAIDA", "operario_saida")
    if u_saida and s_saida:
        usuarios[u_saida.strip()] = {"senha": s_saida.strip(), "perfil": p_saida.strip()}

    u_fiscal = os.getenv("USUARIO_FISCAL")
    s_fiscal = os.getenv("SENHA_FISCAL")
    p_fiscal = os.getenv("PERFIL_FISCAL", "operario_devolucao")
    if u_fiscal and s_fiscal:
        usuarios[u_fiscal.strip()] = {"senha": s_fiscal.strip(), "perfil": p_fiscal.strip()}

    return usuarios

USUARIOS = carregar_usuarios()

PERFIL_LABELS = {
    "admin":              "Administrador",
    "operario_entrada":   "Entrada de Materiais",
    "operario_saida":     "Saída de Materiais",
    "operario_devolucao": "Fiscalização / Devoluções",
}

# ==========================================
# CORES E TEMA
# ==========================================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COR_AZUL       = "#1d4ed8"
COR_AZUL_ESCURO = "#1e3a5f"
COR_AZUL_HOVER  = "#3b82f6"
COR_FUNDO      = "#e2e8f0"
COR_PAINEL     = "#f1f5f9"
COR_BRANCO     = "#ffffff"
COR_TEXTO      = "#0f172a"
COR_TEXTO_SEC  = "#475569"
COR_BORDA      = "#cbd5e1"
COR_ERRO       = "#b45309"
COR_VERDE      = "#16a34a"
COR_VERMELHO   = "#dc2626"
COR_AMARELO    = "#ca8a04"

FONTE_TITULO  = ("Segoe UI", 22, "bold")
FONTE_SUB     = ("Segoe UI", 13)
FONTE_LABEL   = ("Segoe UI", 12, "bold")
FONTE_INPUT   = ("Segoe UI", 13)
FONTE_TABLE   = ("Segoe UI", 12)
FONTE_SMALL   = ("Segoe UI", 11) 
FONTE_ENTRY   = FONTE_INPUT
FONTE_BTN     = ("Segoe UI", 13, "bold")

# ==========================================
# TELA DE LOGIN
# ==========================================
class TelaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Armazena+ | Gestão de Estoque")
        self.withdraw()
        self.state("zoomed")
        self.configure(fg_color=COR_FUNDO)
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Return>", lambda e: self.verificar_login())
        self.bind("<KP_Enter>", lambda e: self.verificar_login())
        self._construir_ui()
        self.after(100, self._mostrar)

    def _mostrar(self):
        self.deiconify()
        self.state("zoomed")

    def _construir_ui(self):
        painel = ctk.CTkFrame(self, width=460, height=540,
                              fg_color=COR_PAINEL, corner_radius=20,
                              border_width=1, border_color=COR_BORDA)
        painel.place(relx=0.5, rely=0.5, anchor="center")
        painel.pack_propagate(False)

        caminho_logo = os.path.join(DIRETORIO_ATUAL, "logo.png")
        try:
            imagem_pil = Image.open(caminho_logo)
            self.logo_image = ctk.CTkImage(light_image=imagem_pil, dark_image=imagem_pil, size=(400, 400))
            
            self.label_logo = ctk.CTkLabel(painel, text="", image=self.logo_image)
            self.label_logo.pack(pady=(35, 10))
        except Exception as e:
            print(f"Aviso: Não foi possível carregar a imagem 'logo.png'. Motivo: {e}")
            ctk.CTkLabel(painel, text="🏗 Armazena+", font=FONTE_TITULO, text_color=COR_AZUL_ESCURO).pack(pady=(35, 10))

        ctk.CTkLabel(painel, text="Usuário", font=FONTE_LABEL,
                     text_color=COR_TEXTO_SEC).pack(anchor="w", padx=36, pady=(15, 2))
        self.campo_usuario = ctk.CTkEntry(painel, width=388, height=44,
                                          placeholder_text="Digite seu usuário",
                                          fg_color=COR_BRANCO, border_color=COR_BORDA,
                                          text_color=COR_TEXTO, font=FONTE_INPUT,
                                          corner_radius=10)
        self.campo_usuario.pack(padx=36)

        ctk.CTkLabel(painel, text="Senha", font=FONTE_LABEL,
                     text_color=COR_TEXTO_SEC).pack(anchor="w", padx=36, pady=(12, 2))
        self.campo_senha = ctk.CTkEntry(painel, width=388, height=44,
                                        placeholder_text="••••••",
                                        show="*",
                                        fg_color=COR_BRANCO, border_color=COR_BORDA,
                                        text_color=COR_TEXTO, font=FONTE_ENTRY,
                                        corner_radius=10)
        self.campo_senha.pack(padx=36)

        self.lbl_erro = ctk.CTkLabel(painel, text="", text_color=COR_ERRO,
                                     font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"))
        self.lbl_erro.pack(pady=(8, 0))

        self.btn_login = ctk.CTkButton(painel, width=388, height=48, text="ENTRAR",
                                       font=FONTE_BTN, fg_color=COR_AZUL,
                                       hover_color=COR_AMARELO, text_color=COR_BRANCO,
                                       corner_radius=12, command=self.verificar_login)
        self.btn_login.pack(padx=36, pady=(6, 0))

        ctk.CTkLabel(painel, text="Acesso restrito a usuários autorizados.",
                     font=FONTE_SUB, text_color="#94a3b8").pack(pady=(20, 0))

        self.campo_usuario.focus()

    def verificar_login(self):
        usuario = self.campo_usuario.get().strip()
        senha   = self.campo_senha.get().strip()

        if not usuario or not senha:
            self.lbl_erro.configure(text="⚠ Preencha todos os campos.")
            return

        if usuario in USUARIOS and USUARIOS[usuario]["senha"] == senha:
            perfil = USUARIOS[usuario]["perfil"]
            self.lbl_erro.configure(text="")
            registrar_log(usuario, "Fez login no sistema.")
            self.withdraw()
            self.after(100, lambda: self._abrir_dashboard(usuario, perfil))
        else:
            self.lbl_erro.configure(text="⚠ Dados incorretos. Verifique e tente novamente.")
            self.campo_senha.delete(0, "end")
            self.campo_senha.focus()

    def _abrir_dashboard(self, usuario, perfil):
        dashboard = TelaDashboard(usuario, perfil, self)
        dashboard.mainloop()

# ==========================================
# DASHBOARD PRINCIPAL
# ==========================================
class TelaDashboard(ctk.CTkToplevel):
    def __init__(self, usuario, perfil, login_ref):
        super().__init__()
        self.usuario   = usuario
        self.perfil    = perfil
        self.login_ref = login_ref

        self.title(f"Armazena+ | {PERFIL_LABELS.get(perfil, perfil)}")
        self.state("zoomed")
        self.configure(fg_color=COR_FUNDO)
        self.protocol("WM_DELETE_WINDOW", self._sair)

        self._construir_ui()
        self._mostrar_tab("estoque")

    def _construir_ui(self):
        topbar = ctk.CTkFrame(self, fg_color=COR_AZUL_ESCURO, corner_radius=0, height=56)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        ctk.CTkLabel(topbar, text="🏗  Armazena+",
                     font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
                     text_color=COR_BRANCO).pack(side="left", padx=20, pady=14)

        ctk.CTkLabel(topbar,
                     text=f"  {self.usuario}  ·  {PERFIL_LABELS.get(self.perfil, '')}  ",
                     font=FONTE_SMALL, text_color="#93c5fd",
                     fg_color="#0c2a4a", corner_radius=20).pack(side="left", padx=6, pady=18)

        ctk.CTkButton(topbar, text="Sair", width=70, height=30,
                      fg_color="transparent", border_color="#93c5fd",
                      border_width=1, text_color="#93c5fd", hover_color="#1e3a5f",
                      font=FONTE_SMALL, corner_radius=8,
                      command=self._sair).pack(side="right", padx=20, pady=12)

        corpo = ctk.CTkFrame(self, fg_color=COR_FUNDO, corner_radius=0)
        corpo.pack(fill="both", expand=True)

        self.sidebar = ctk.CTkFrame(corpo, width=200, fg_color=COR_BRANCO,
                                    corner_radius=0, border_width=1, border_color=COR_BORDA)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._construir_sidebar()

        self.area_conteudo = ctk.CTkFrame(corpo, fg_color=COR_FUNDO, corner_radius=0)
        self.area_conteudo.pack(side="left", fill="both", expand=True)

        self.tabs = {}
        self.tabs["estoque"]   = self._criar_tab_estoque()
        self.tabs["cadastrar"] = self._criar_tab_cadastrar()
        self.tabs["entrada"]   = self._criar_tab_entrada()
        self.tabs["saida"]     = self._criar_tab_saida()
        self.tabs["devolucao"] = self._criar_tab_devolucao()
        self.tabs["logs"]      = self._criar_tab_logs()

    def _construir_sidebar(self):
        ctk.CTkLabel(self.sidebar, text="MENU",
                     font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                     text_color="#94a3b8").pack(anchor="w", padx=16, pady=(16, 4))

        self.nav_btns = {}
        menus = [("estoque", "📦  Estoque")]

        # FILTRO CORRIGIDO: Permite que administradores e fiscais visualizem a Auditoria
        if self.perfil == "admin" or self.perfil == "operario_devolucao":
            menus.append(("logs", "📋  Auditoria"))
        if self.perfil == "operario_entrada" or self.perfil == "admin":
            menus += [("cadastrar", "➕  Cadastrar Item"),
                      ("entrada",   "📥  Dar Entrada")]
        if self.perfil == "operario_saida" or self.perfil == "admin":
            menus.append(("saida", "📤  Dar Saída"))
        if self.perfil == "operario_devolucao" or self.perfil == "admin":
            menus.append(("devolucao", "🔄  Devoluções"))

        for key, label in menus:
            btn = ctk.CTkButton(self.sidebar, text=label, anchor="w", width=180, height=40,
                                fg_color="transparent", text_color=COR_TEXTO_SEC,
                                hover_color="#e2e8f0", font=FONTE_LABEL, corner_radius=8,
                                command=lambda k=key: self._mostrar_tab(k))
            btn.pack(anchor="w", padx=10, pady=2)
            self.nav_btns[key] = btn

    def _mostrar_tab(self, key):
        for k, frame in self.tabs.items():
            frame.pack_forget()
        self.tabs[key].pack(fill="both", expand=True, padx=20, pady=20)

        for k, btn in self.nav_btns.items():
            btn.configure(
                fg_color=COR_AZUL if k == key else "transparent",
                text_color=COR_BRANCO if k == key else COR_TEXTO_SEC
            )
        if key == "estoque":
            self._carregar_estoque()
        if key == "logs":
            self._carregar_logs()

    def _card(self, parent, titulo=None):
        frame = ctk.CTkFrame(parent, fg_color=COR_BRANCO, corner_radius=12,
                             border_width=1, border_color=COR_BORDA)
        if titulo:
            ctk.CTkLabel(frame, text=titulo,
                         font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                         text_color=COR_TEXTO).pack(anchor="w", padx=16, pady=(14, 8))
            ctk.CTkFrame(frame, height=1, fg_color=COR_BORDA).pack(fill="x")
        return frame

    def _btn_acao(self, parent, texto, comando, cor=None):
        return ctk.CTkButton(parent, text=texto, height=40, fg_color=cor or COR_AZUL,
                             hover_color=COR_AZUL_HOVER, text_color=COR_BRANCO, 
                             font=FONTE_BTN, corner_radius=10, command=comando)

    def _entry(self, parent, placeholder="", show=None):
        kwargs = dict(placeholder_text=placeholder, fg_color=COR_BRANCO,
                      border_color=COR_BORDA, text_color=COR_TEXTO,
                      font=FONTE_ENTRY, height=40, corner_radius=8)
        if show:
            kwargs["show"] = show
        return ctk.CTkEntry(parent, **kwargs)

    def _feedback(self, label_widget, msg, cor=COR_VERDE):
        label_widget.configure(text=msg, text_color=cor)
        label_widget.after(3000, lambda: label_widget.configure(text=""))

    # ===== ABA ESTOQUE =====
    def _criar_tab_estoque(self):
        frame = ctk.CTkFrame(self.area_conteudo, fg_color="transparent", corner_radius=0)

        resumo = ctk.CTkFrame(frame, fg_color="transparent")
        resumo.pack(fill="x", pady=(0, 16))
        self.stat_frames = {}
        for col, (key, label, icone) in enumerate([
            ("total",      "Total de Itens",  "📦"),
            ("ferramentas","Ferramentas",       "🔧"),
            ("consumiveis","Consumíveis",       "🪣"),
            ("emprestadas","Emprestadas",       "⚠️"),
        ]):
            card = ctk.CTkFrame(resumo, fg_color=COR_BRANCO, corner_radius=10,
                                border_width=1, border_color=COR_BORDA)
            card.grid(row=0, column=col, padx=(0 if col==0 else 10, 0), sticky="nsew")
            resumo.columnconfigure(col, weight=1)
            ctk.CTkLabel(card, text=icone, font=ctk.CTkFont(size=20)).pack(pady=(12,2))
            ctk.CTkLabel(card, text=label, font=FONTE_SMALL,
                         text_color=COR_TEXTO_SEC).pack()
            lbl_val = ctk.CTkLabel(card, text="0",
                                   font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                                   text_color=COR_AZUL)
            lbl_val.pack(pady=(2, 12))
            self.stat_frames[key] = lbl_val

        card_tabela = self._card(frame, "Itens em Estoque")
        card_tabela.pack(fill="both", expand=True)

        cabecalho = ctk.CTkFrame(card_tabela, fg_color="#f8fafc", corner_radius=0)
        cabecalho.pack(fill="x", padx=1)
        for col, (texto, peso) in enumerate([("ID",4),("Nome",30),("Tipo",14),("Qtd / Status",18),("Responsável",18)]):
            ctk.CTkLabel(cabecalho, text=texto, font=FONTE_SMALL, text_color=COR_TEXTO_SEC,
                         anchor="w").grid(row=0, column=col, sticky="w",
                                          padx=(16 if col==0 else 6), pady=8)
            cabecalho.columnconfigure(col, weight=peso)

        self.scroll_estoque = ctk.CTkScrollableFrame(card_tabela, fg_color=COR_BRANCO,
                                                      corner_radius=0)
        self.scroll_estoque.pack(fill="both", expand=True, padx=1, pady=(0,1))
        for col, peso in enumerate([4,30,14,18,18]):
            self.scroll_estoque.columnconfigure(col, weight=peso)

        btn_row = ctk.CTkFrame(card_tabela, fg_color="transparent")
        btn_row.pack(anchor="e", padx=16, pady=8)
        self._btn_acao(btn_row, "↻  Atualizar", self._carregar_estoque,
                       cor="#475569").pack()

        return frame

    def _carregar_estoque(self):
        for widget in self.scroll_estoque.winfo_children():
            widget.destroy()

        conexao = sqlite3.connect(BANCO_DADOS)
        cursor  = conexao.cursor()
        cursor.execute("SELECT id, nome, tipo, quantidade, unidade, status, responsavel FROM estoque")
        linhas  = cursor.fetchall()
        conexao.close()

        total = len(linhas)
        ferramentas  = sum(1 for l in linhas if l[2]=="ferramenta")
        consumiveis  = sum(1 for l in linhas if l[2]=="consumivel")
        emprestadas  = sum(1 for l in linhas if l[2]=="ferramenta" and l[5]=="emprestado")

        self.stat_frames["total"].configure(text=str(total))
        self.stat_frames["ferramentas"].configure(text=str(ferramentas))
        self.stat_frames["consumiveis"].configure(text=str(consumiveis))
        self.stat_frames["emprestadas"].configure(text=str(emprestadas))

        if not linhas:
            ctk.CTkLabel(self.scroll_estoque, text="Estoque vazio. Cadastre itens.",
                         text_color=COR_TEXTO_SEC, font=FONTE_LABEL).grid(
                         row=0, column=0, columnspan=5, pady=30)
            return

        for i, linha in enumerate(linhas):
            id_prod, nome, tipo, qtd, unidade, status, resp = linha
            bg = COR_BRANCO if i % 2 == 0 else "#f8fafc"

            tipo_texto = "Consumível" if tipo == "consumivel" else "Ferramenta"
            if tipo == "consumivel":
                qtd_texto = f"{qtd} {unidade or ''}"
                status_texto = ""
            else:
                qtd_texto = "Disponível" if status == "disponivel" else "Emprestada"
                status_texto = resp or ""

            for col, (val, ancora) in enumerate([
                (str(id_prod), "center"),
                (nome,         "w"),
                (tipo_texto,   "center"),
                (qtd_texto,    "center"),
                (status_texto, "w"),
            ]):
                cor_val = COR_AZUL if col == 0 else (COR_VERMELHO if val == "Emprestada" else COR_TEXTO)
                lbl = ctk.CTkLabel(self.scroll_estoque, text=val, font=FONTE_TABLE,
                                   text_color=cor_val, anchor=ancora,
                                   fg_color=bg, corner_radius=0)
                lbl.grid(row=i, column=col, sticky="ew", padx=(16 if col == 0 else 6), pady=5)

    # ===== ABA CADASTRAR =====
    def _criar_tab_cadastrar(self):
        frame = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        card  = self._card(frame, "Cadastrar Novo Item")
        card.pack(fill="x", pady=(0, 16))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=12)

        ctk.CTkLabel(inner, text="Nome do Material / Ferramenta", font=FONTE_LABEL,
                     text_color=COR_TEXTO_SEC).pack(anchor="w")
        self.cad_nome = self._entry(inner, "Ex: Cimento CP-II, Furadeira...")
        self.cad_nome.pack(fill="x", pady=(4, 10))

        ctk.CTkLabel(inner, text="Tipo", font=FONTE_LABEL, text_color=COR_TEXTO_SEC).pack(anchor="w")
        self.cad_tipo = ctk.CTkOptionMenu(inner, values=["Consumível", "Ferramenta"],
                                          fg_color=COR_BRANCO, button_color=COR_AZUL,
                                          text_color=COR_TEXTO, font=FONTE_ENTRY, command=self._toggle_tipo)
        self.cad_tipo.pack(fill="x", pady=(4, 10))

        self.frame_consumivel = ctk.CTkFrame(inner, fg_color="transparent")
        self.frame_consumivel.pack(fill="x")
        ctk.CTkLabel(self.frame_consumivel, text="Unidade de medida", font=FONTE_LABEL,
                     text_color=COR_TEXTO_SEC).pack(anchor="w")
        self.cad_unidade = self._entry(self.frame_consumivel, "Ex: sacos, un, metros")
        self.cad_unidade.pack(fill="x", pady=(4, 10))
        ctk.CTkLabel(self.frame_consumivel, text="Quantidade inicial", font=FONTE_LABEL,
                     text_color=COR_TEXTO_SEC).pack(anchor="w")
        self.cad_qtd = self._entry(self.frame_consumivel, "Ex: 50")
        self.cad_qtd.pack(fill="x", pady=(4, 10))

        self.lbl_cad_feedback = ctk.CTkLabel(inner, text="", font=FONTE_LABEL)
        self.lbl_cad_feedback.pack(pady=4)

        self._btn_acao(inner, "➕  Cadastrar Item", self._cadastrar_item).pack(fill="x", pady=(4, 0))
        return frame

    def _toggle_tipo(self, valor):
        if valor == "Consumível":
            self.frame_consumivel.pack(fill="x")
        else:
            self.frame_consumivel.pack_forget()

    def _cadastrar_item(self):
        nome = self.cad_nome.get().strip()
        tipo = self.cad_tipo.get()
        if not nome:
            self._feedback(self.lbl_cad_feedback, "⚠ Informe o nome do item.", COR_ERRO)
            return

        conexao = sqlite3.connect(BANCO_DADOS)
        cursor  = conexao.cursor()
        mensagem_log = ""

        if tipo == "Consumível":
            unidade = self.cad_unidade.get().strip() or "un"
            try:
                qtd = int(self.cad_qtd.get())
            except ValueError:
                self._feedback(self.lbl_cad_feedback, "⚠ Quantidade inválida.", COR_ERRO)
                conexao.close()
                return
            
            cursor.execute(
                "INSERT INTO estoque (nome, tipo, quantidade, unidade) VALUES (?, 'consumivel', ?, ?)",
                (nome, qtd, unidade)
            )
            mensagem_log = f"Cadastrou o consumível '{nome}' com {qtd} {unidade}."
        else:
            cursor.execute(
                "INSERT INTO estoque (nome, tipo, status) VALUES (?, 'ferramenta', 'disponivel')",
                (nome,)
            )
            mensagem_log = f"Cadastrou a ferramenta '{nome}' como disponível."

        conexao.commit()
        conexao.close()

        registrar_log(self.usuario, mensagem_log)

        self._feedback(self.lbl_cad_feedback, f"✔ '{nome}' cadastrado com sucesso!")
        self.cad_nome.delete(0, "end")
        self.cad_unidade.delete(0, "end")
        self.cad_qtd.delete(0, "end")

    # ===== ABA ENTRADA =====
    def _criar_tab_entrada(self):
        frame = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        card  = self._card(frame, "Dar Entrada / Reabastecer Estoque")
        card.pack(fill="x")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=12)

        ctk.CTkLabel(inner, text="ID do Produto", font=FONTE_LABEL, text_color=COR_TEXTO_SEC).pack(anchor="w")
        self.ent_id = self._entry(inner, "Ex: 3")
        self.ent_id.pack(fill="x", pady=(4, 10))

        ctk.CTkLabel(inner, text="Quantidade entrando", font=FONTE_LABEL, text_color=COR_TEXTO_SEC).pack(anchor="w")
        self.ent_qtd = self._entry(inner, "Ex: 20")
        self.ent_qtd.pack(fill="x", pady=(4, 10))

        self.lbl_ent_feedback = ctk.CTkLabel(inner, text="", font=FONTE_LABEL)
        self.lbl_ent_feedback.pack(pady=4)

        self._btn_acao(inner, "📥  Registrar Entrada", self._dar_entrada).pack(fill="x")
        return frame

    def _dar_entrada(self):
        try:
            id_prod = int(self.ent_id.get())
            qtd     = int(self.ent_qtd.get())
        except ValueError:
            self._feedback(self.lbl_ent_feedback, "⚠ ID e quantidade devem ser números.", COR_ERRO)
            return

        conexao = sqlite3.connect(BANCO_DADOS)
        cursor  = conexao.cursor()
        cursor.execute("SELECT nome, tipo, quantidade, unidade FROM estoque WHERE id=?", (id_prod,))
        prod = cursor.fetchone()

        if not prod:
            self._feedback(self.lbl_ent_feedback, "⚠ Produto não encontrado.", COR_ERRO)
            conexao.close()
            return
        nome, tipo, qtd_atual, unidade = prod
        if tipo == "ferramenta":
            self._feedback(self.lbl_ent_feedback, "⚠ Ferramentas não têm reabastecimento.", COR_ERRO)
            conexao.close()
            return

        nova_qtd = qtd_atual + qtd
        cursor.execute("UPDATE estoque SET quantidade=? WHERE id=?", (nova_qtd, id_prod))
        
        conexao.commit()
        conexao.close()
        
        registrar_log(self.usuario, f"Deu entrada em {qtd} {unidade} de '{nome}' (ID {id_prod}). Novo saldo: {nova_qtd}.")
        self._feedback(self.lbl_ent_feedback, f"✔ Saldo de '{nome}': {nova_qtd} {unidade}.")
        self.ent_id.delete(0, "end")
        self.ent_qtd.delete(0, "end")

    # ===== ABA SAÍDA =====
    def _criar_tab_saida(self):
        frame = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        card  = self._card(frame, "Dar Saída / Emprestar Ferramenta")
        card.pack(fill="x")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=12)

        ctk.CTkLabel(inner, text="ID do Produto", font=FONTE_LABEL, text_color=COR_TEXTO_SEC).pack(anchor="w")
        self.saida_id = self._entry(inner, "Ex: 1")
        self.saida_id.pack(fill="x", pady=(4, 10))

        ctk.CTkLabel(inner, text="Quantidade (apenas consumíveis)", font=FONTE_LABEL, text_color=COR_TEXTO_SEC).pack(anchor="w")
        self.saida_qtd = self._entry(inner, "Deixe em branco para ferramenta")
        self.saida_qtd.pack(fill="x", pady=(4, 10))

        ctk.CTkLabel(inner, text="Destino / Nome do Operário", font=FONTE_LABEL, text_color=COR_TEXTO_SEC).pack(anchor="w")
        self.saida_dest = self._entry(inner, "Ex: Setor A / João Silva")
        self.saida_dest.pack(fill="x", pady=(4, 10))

        self.lbl_saida_feedback = ctk.CTkLabel(inner, text="", font=FONTE_LABEL)
        self.lbl_saida_feedback.pack(pady=4)

        self._btn_acao(inner, "📤  Registrar Saída", self._dar_saida).pack(fill="x")
        return frame

    def _dar_saida(self):
        try:
            id_prod = int(self.saida_id.get())
        except ValueError:
            self._feedback(self.lbl_saida_feedback, "⚠ ID inválido.", COR_ERRO)
            return
        dest = self.saida_dest.get().strip()
        if not dest:
            self._feedback(self.lbl_saida_feedback, "⚠ Informe o destino/operário.", COR_ERRO)
            return

        conexao = sqlite3.connect(BANCO_DADOS)
        cursor  = conexao.cursor()
        cursor.execute("SELECT nome, tipo, quantidade, status FROM estoque WHERE id=?", (id_prod,))
        prod = cursor.fetchone()

        if not prod:
            self._feedback(self.lbl_saida_feedback, "⚠ Produto não encontrado.", COR_ERRO)
            conexao.close()
            return

        nome, tipo, qtd_atual, status_atual = prod
        mensagem_log = ""
        msg_feedback = ""

        if tipo == "consumivel":
            try:
                qtd = int(self.saida_qtd.get())
            except ValueError:
                self._feedback(self.lbl_saida_feedback, "⚠ Informe a quantidade.", COR_ERRO)
                conexao.close()
                return
            if qtd > qtd_atual:
                self._feedback(self.lbl_saida_feedback, "⚠ Quantidade insuficiente.", COR_ERRO)
                conexao.close()
                return
            
            nova_qtd = qtd_atual - qtd
            cursor.execute("UPDATE estoque SET quantidade=? WHERE id=?", (nova_qtd, id_prod))
            mensagem_log = f"Retirou {qtd} de '{nome}' (ID {id_prod}) para: {dest}."
            msg_feedback = f"✔ Saída de {qtd} '{nome}' registrada."
        else:
            if status_atual == "emprestado":
                self._