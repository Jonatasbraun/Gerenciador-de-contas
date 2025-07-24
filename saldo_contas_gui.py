"""
ATENÇÃO: Para que o envio de e-mail funcione com Gmail:
1. Ative a verificação em duas etapas na sua conta Google.
2. Gere uma senha de app em https://myaccount.google.com/security > Senhas de app.
3. Use o e-mail e a senha de app nos campos EMAIL_SENDER e EMAIL_SENDER_PASS abaixo.

Se não quiser usar Gmail, configure outro servidor SMTP que aceite autenticação por senha comum.
"""

import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
import json
import hashlib
import smtplib
import random
from email.message import EmailMessage

# Caminho seguro para salvar os arquivos na pasta Documentos do usuário
USER_DOCS = os.path.join(os.path.expanduser('~'), 'Documents')
SALDOS_FILE = os.path.join(USER_DOCS, "saldos.json")
CONTAS_FILE = os.path.join(USER_DOCS, "contas.json")
CHEQUES_FILE = os.path.join(USER_DOCS, "cheques.json")
USERS_FILE = os.path.join(USER_DOCS, "usuarios.json")

EMAIL_SENDER = "seuemail@gmail.com"  # Altere para o e-mail do remetente
EMAIL_SENDER_PASS = "sua_senha"      # Altere para a senha do e-mail do remetente
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Funções para salvar e carregar dados

def carregar_saldos():
    if os.path.exists(SALDOS_FILE):
        with open(SALDOS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "banco_sicoob": 0.0,
        "banco_bradesco": 0.0,
        "dinheiro": 0.0,
        "cheque_a_prazo": 0.0,
        "cheque_a_vista": 0.0
    }

def salvar_saldos(saldos):
    with open(SALDOS_FILE, "w", encoding="utf-8") as f:
        json.dump(saldos, f, ensure_ascii=False, indent=2)


def carregar_contas():
    if os.path.exists(CONTAS_FILE):
        with open(CONTAS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_contas(contas):
    with open(CONTAS_FILE, "w", encoding="utf-8") as f:
        json.dump(contas, f, ensure_ascii=False, indent=2)

def carregar_cheques():
    if os.path.exists(CHEQUES_FILE):
        with open(CHEQUES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_cheques(cheques):
    with open(CHEQUES_FILE, "w", encoding="utf-8") as f:
        json.dump(cheques, f, ensure_ascii=False, indent=2)

def carregar_usuarios():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_usuarios(usuarios):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=2)

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def enviar_codigo_email(destino, codigo):
    msg = EmailMessage()
    msg["Subject"] = "Recuperação de senha - Código de segurança"
    msg["From"] = EMAIL_SENDER
    msg["To"] = destino
    msg.set_content(f"Seu código de segurança para recuperação de senha é: {codigo}")
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_SENDER_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print("Erro ao enviar e-mail:", e)
        return False

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Controle de Saldos e Contas a Pagar")
        self.saldos = carregar_saldos()
        self.contas = carregar_contas()
        self.cheques = carregar_cheques()
        self.criar_layout()
        self.atualizar_saldos()
        self.atualizar_contas()
        self.atualizar_cheques()

    def criar_layout(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)
        # Aba Saldos e Contas
        frame_main = tk.Frame(notebook)
        notebook.add(frame_main, text="Saldos e Contas")
        # Saldos
        frame_saldos = tk.LabelFrame(frame_main, text="Saldos", padx=10, pady=10)
        frame_saldos.pack(fill="x", padx=10, pady=5)
        self.labels_saldos = {}
        for tipo in ["banco_sicoob", "banco_bradesco", "dinheiro", "cheque_a_prazo", "cheque_a_vista"]:
            nome = tipo.replace("_", " ").capitalize().replace("banco sicoob", "Banco Sicoob").replace("banco bradesco", "Banco Bradesco").replace("Cheque a prazo", "Cheque a prazo").replace("Cheque a vista", "Cheque à vista")
            lbl = tk.Label(frame_saldos, text=f"{nome}: R$ 0.00", font=("Arial", 12))
            lbl.pack(anchor="w")
            self.labels_saldos[tipo] = lbl
        btn_add_saldo = tk.Button(frame_saldos, text="Adicionar saldo", command=self.adicionar_saldo)
        btn_add_saldo.pack(pady=5)

        # Contas
        frame_contas = tk.LabelFrame(frame_main, text="Contas a Pagar", padx=10, pady=10)
        frame_contas.pack(fill="both", expand=True, padx=10, pady=5)
        # Filtro de contas
        self.filtro_var = tk.StringVar(value="Todas")
        filtro_menu = ttk.Combobox(frame_contas, textvariable=self.filtro_var, values=["Todas", "A pagar", "Pagas"], state="readonly", width=10)
        filtro_menu.pack(pady=2)
        filtro_menu.bind("<<ComboboxSelected>>", lambda e: self.atualizar_contas())
        # Filtro de mês
        self.filtro_mes_var = tk.StringVar(value="Todos")
        meses = ["Todos"] + [f"{str(m).zfill(2)}/{str(a)}" for a in range(2020, 2031) for m in range(1, 13)]
        filtro_mes_menu = ttk.Combobox(frame_contas, textvariable=self.filtro_mes_var, values=meses, state="readonly", width=10)
        filtro_mes_menu.pack(pady=2)
        filtro_mes_menu.bind("<<ComboboxSelected>>", lambda e: self.atualizar_contas())
        self.lista_contas = tk.Listbox(frame_contas, font=("Arial", 11), height=8)
        self.lista_contas.pack(fill="both", expand=True)
        self.total_contas_label = tk.Label(frame_contas, text="Total do mês selecionado: R$ 0.00", font=("Arial", 11, "bold"))
        self.total_contas_label.pack(anchor="e", padx=5, pady=3)
        btn_add_conta = tk.Button(frame_contas, text="Adicionar conta", command=self.adicionar_conta)
        btn_add_conta.pack(side="left", padx=5, pady=5)
        btn_pagar_conta = tk.Button(frame_contas, text="Pagar conta selecionada", command=self.pagar_conta)
        btn_pagar_conta.pack(side="right", padx=5, pady=5)
        btn_excluir_conta = tk.Button(frame_contas, text="Excluir conta selecionada", command=self.excluir_conta)
        btn_excluir_conta.pack(side="right", padx=5, pady=5)

        # Cheques
        frame_cheques = tk.Frame(notebook)
        notebook.add(frame_cheques, text="Cheques")
        self.filtro_cheque_var = tk.StringVar(value="Todos")
        filtro_cheque_menu = ttk.Combobox(frame_cheques, textvariable=self.filtro_cheque_var, values=["Todos", "À vista", "A prazo"], state="readonly", width=10)
        filtro_cheque_menu.pack(pady=2)
        filtro_cheque_menu.bind("<<ComboboxSelected>>", lambda e: self.atualizar_cheques())
        self.lista_cheques = tk.Listbox(frame_cheques, font=("Arial", 11), height=8)
        self.lista_cheques.pack(fill="both", expand=True)
        btn_add_cheque = tk.Button(frame_cheques, text="Registrar cheque", command=self.adicionar_cheque)
        btn_add_cheque.pack(side="left", padx=5, pady=5)
        btn_excluir_cheque = tk.Button(frame_cheques, text="Excluir cheque selecionado", command=self.excluir_cheque)
        btn_excluir_cheque.pack(side="right", padx=5, pady=5)

    def atualizar_saldos(self):
        for tipo, lbl in self.labels_saldos.items():
            lbl.config(text=f"{lbl.cget('text').split(':')[0]}: R$ {self.saldos.get(tipo, 0.0):.2f}")

    
    def atualizar_contas(self):
        self.lista_contas.delete(0, tk.END)
        filtro = self.filtro_var.get()
        filtro_mes = self.filtro_mes_var.get()
        total_mes = 0.0

        for i, conta in enumerate(self.contas):
            status = "PAGA" if conta["paga"] else "ABERTA"
            if filtro == "Pagas" and not conta["paga"]:
                continue
            if filtro == "A pagar" and conta["paga"]:
                continue
            if filtro_mes != "Todos":
                try:
                    mes_ano = conta["vencimento"][3:10]
                except:
                    mes_ano = ""
                if filtro_mes != mes_ano:
                    continue
            self.lista_contas.insert(tk.END, f"{i}: {conta['nome']} - R$ {conta['valor']:.2f} - Venc: {conta['vencimento']} - {status}")
            total_mes += conta["valor"]

        self.total_contas_label.config(text=f"Total do mês selecionado: R$ {total_mes:.2f}")


    def atualizar_cheques(self):
        self.lista_cheques.delete(0, tk.END)
        filtro = self.filtro_cheque_var.get()
        for i, cheque in enumerate(self.cheques):
            tipo = "À vista" if cheque["tipo"] == "avista" else "A prazo"
            if filtro == "À vista" and cheque["tipo"] != "avista":
                continue
            if filtro == "A prazo" and cheque["tipo"] != "aprazo":
                continue
            self.lista_cheques.insert(tk.END, f"{i}: {cheque['cliente']} - Nº {cheque['numero']} - R$ {cheque['valor']:.2f} - Venc: {cheque['vencimento']} - {tipo}")

    def adicionar_saldo(self):
        def confirmar():
            tipo = combo_tipo.get()
            try:
                valor = float(entry_valor.get())
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido.")
                return
            if tipo not in self.saldos:
                messagebox.showerror("Erro", "Tipo de saldo inválido.")
                return
            if tipo == "banco_sicoob" or tipo == "banco_bradesco":
                if var_operacao.get() == "Adicionar":
                    self.saldos[tipo] += valor
                else:
                    if self.saldos[tipo] < valor:
                        messagebox.showerror("Erro", "Saldo insuficiente.")
                        return
                    self.saldos[tipo] -= valor
            else:
                if var_operacao.get() == "Adicionar":
                    self.saldos[tipo] += valor
                else:
                    if self.saldos[tipo] < valor:
                        messagebox.showerror("Erro", "Saldo insuficiente.")
                        return
                    self.saldos[tipo] -= valor
            salvar_saldos(self.saldos)
            self.atualizar_saldos()
            win.destroy()

        win = tk.Toplevel(self.root)
        win.title("Movimentar saldo")
        tk.Label(win, text="Tipo de saldo:").pack(pady=2)
        combo_tipo = ttk.Combobox(win, values=["banco_sicoob", "banco_bradesco", "dinheiro", "cheque_a_prazo", "cheque_a_vista"], state="readonly")
        combo_tipo.pack(pady=2)
        combo_tipo.current(0)
        tk.Label(win, text="Valor:").pack(pady=2)
        entry_valor = tk.Entry(win)
        entry_valor.pack(pady=2)
        var_operacao = tk.StringVar(value="Adicionar")
        frame_ops = tk.Frame(win)
        frame_ops.pack(pady=2)
        tk.Radiobutton(frame_ops, text="Adicionar", variable=var_operacao, value="Adicionar").pack(side="left")
        tk.Radiobutton(frame_ops, text="Retirar", variable=var_operacao, value="Retirar").pack(side="left")
        btn_conf = tk.Button(win, text="Confirmar", command=confirmar)
        btn_conf.pack(pady=5)

    def adicionar_conta(self):
        def confirmar():
            nome = entry_nome.get()
            try:
                valor = float(entry_valor.get())
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido.")
                return
            vencimento = entry_venc.get()
            if not nome or not vencimento:
                messagebox.showerror("Erro", "Preencha todos os campos.")
                return
            self.contas.append({
                "valor": valor,
                "vencimento": vencimento,
                "nome": nome,
                "paga": False
            })
            salvar_contas(self.contas)
            self.atualizar_contas()
            win.destroy()

        win = tk.Toplevel(self.root)
        win.title("Adicionar conta a pagar")
        tk.Label(win, text="Nome do boleto/recebedor:").pack(pady=2)
        entry_nome = tk.Entry(win)
        entry_nome.pack(pady=2)
        tk.Label(win, text="Valor da conta:").pack(pady=2)
        entry_valor = tk.Entry(win)
        entry_valor.pack(pady=2)
        tk.Label(win, text="Vencimento (dd/mm/aaaa):").pack(pady=2)
        entry_venc = tk.Entry(win)
        entry_venc.pack(pady=2)
        btn_conf = tk.Button(win, text="Confirmar", command=confirmar)
        btn_conf.pack(pady=5)

    def adicionar_cheque(self):
        def confirmar():
            cliente = entry_cliente.get()
            numero = entry_numero.get()
            try:
                valor = float(entry_valor.get())
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido.")
                return
            vencimento = entry_venc.get()
            tipo = combo_tipo.get()
            if not cliente or not numero or not vencimento or tipo not in ["À vista", "A prazo"]:
                messagebox.showerror("Erro", "Preencha todos os campos.")
                return
            cheque_tipo = "avista" if tipo == "À vista" else "aprazo"
            self.cheques.append({
                "valor": valor,
                "vencimento": vencimento,
                "cliente": cliente,
                "numero": numero,
                "tipo": cheque_tipo
            })
            salvar_cheques(self.cheques)
            # Atualiza saldo correspondente
            if cheque_tipo == "avista":
                self.saldos["cheque_a_vista"] += valor
            else:
                self.saldos["cheque_a_prazo"] += valor
            salvar_saldos(self.saldos)
            self.atualizar_saldos()
            self.atualizar_cheques()
            win.destroy()

        win = tk.Toplevel(self.root)
        win.title("Registrar cheque")
        tk.Label(win, text="Nome do cliente:").pack(pady=2)
        entry_cliente = tk.Entry(win)
        entry_cliente.pack(pady=2)
        tk.Label(win, text="Número do cheque:").pack(pady=2)
        entry_numero = tk.Entry(win)
        entry_numero.pack(pady=2)
        tk.Label(win, text="Valor do cheque:").pack(pady=2)
        entry_valor = tk.Entry(win)
        entry_valor.pack(pady=2)
        tk.Label(win, text="Vencimento (dd/mm/aaaa):").pack(pady=2)
        entry_venc = tk.Entry(win)
        entry_venc.pack(pady=2)
        tk.Label(win, text="Tipo de cheque:").pack(pady=2)
        combo_tipo = ttk.Combobox(win, values=["À vista", "A prazo"], state="readonly")
        combo_tipo.pack(pady=2)
        combo_tipo.current(0)
        btn_conf = tk.Button(win, text="Confirmar", command=confirmar)
        btn_conf.pack(pady=5)

    def pagar_conta(self):
        sel = self.lista_contas.curselection()
        if not sel:
            messagebox.showinfo("Seleção", "Selecione uma conta para pagar.")
            return
        idx = sel[0]
        conta = self.contas[idx]
        if conta["paga"]:
            messagebox.showinfo("Conta", "Conta já está paga.")
            return
        def confirmar():
            tipo = combo_tipo.get()
            if tipo not in self.saldos:
                messagebox.showerror("Erro", "Tipo de saldo inválido.")
                return
            if self.saldos[tipo] < conta["valor"]:
                messagebox.showerror("Erro", "Saldo insuficiente.")
                return
            self.saldos[tipo] -= conta["valor"]
            conta["paga"] = True
            salvar_saldos(self.saldos)
            salvar_contas(self.contas)
            self.atualizar_saldos()
            self.atualizar_contas()
            messagebox.showinfo("Sucesso", "Conta paga com sucesso!")
            win.destroy()

        win = tk.Toplevel(self.root)
        win.title("Pagar conta")
        tk.Label(win, text=f"Conta: {conta['nome']} - R$ {conta['valor']:.2f}").pack(pady=2)
        tk.Label(win, text=f"Vencimento: {conta['vencimento']}").pack(pady=2)
        tk.Label(win, text="Selecione o saldo para pagar:").pack(pady=2)
        combo_tipo = ttk.Combobox(win, values=list(self.saldos.keys()), state="readonly")
        combo_tipo.pack(pady=2)
        combo_tipo.current(0)
        btn_conf = tk.Button(win, text="Confirmar pagamento", command=confirmar)
        btn_conf.pack(pady=5)

    def excluir_conta(self):
        sel = self.lista_contas.curselection()
        if not sel:
            messagebox.showinfo("Seleção", "Selecione uma conta para excluir.")
            return
        idx = sel[0]
        conta = self.contas[idx]
        resp = messagebox.askyesno("Excluir", f"Deseja realmente excluir a conta '{conta['nome']}'?")
        if resp:
            del self.contas[idx]
            salvar_contas(self.contas)
            self.atualizar_contas()
            messagebox.showinfo("Excluído", "Conta excluída com sucesso!")

    def excluir_cheque(self):
        sel = self.lista_cheques.curselection()
        if not sel:
            messagebox.showinfo("Seleção", "Selecione um cheque para excluir.")
            return
        idx = sel[0]
        cheque = self.cheques[idx]
        resp = messagebox.askyesno("Excluir", f"Deseja realmente excluir o cheque do cliente '{cheque['cliente']}'?")
        if resp:
            # Atualiza saldo do respectivo tipo
            if cheque["tipo"] == "avista":
                self.saldos["cheque_a_vista"] -= cheque["valor"]
            else:
                self.saldos["cheque_a_prazo"] -= cheque["valor"]
            salvar_saldos(self.saldos)
            del self.cheques[idx]
            salvar_cheques(self.cheques)
            self.atualizar_saldos()
            self.atualizar_cheques()
            messagebox.showinfo("Excluído", "Cheque excluído com sucesso!")

class LoginWindow:
    def __init__(self, master, on_success):
        self.master = master
        self.on_success = on_success
        self.usuarios = carregar_usuarios()
        self.usuario_logado = None
        self.frame = tk.Frame(master)
        self.frame.pack(padx=20, pady=20)
        tk.Label(self.frame, text="Login:").pack()
        self.entry_login = tk.Entry(self.frame)
        self.entry_login.pack()
        tk.Label(self.frame, text="Senha:").pack()
        self.entry_senha = tk.Entry(self.frame, show="*")
        self.entry_senha.pack()
        btn_login = tk.Button(self.frame, text="Entrar", command=self.tentar_login)
        btn_login.pack(pady=5)
        btn_admin = tk.Button(self.frame, text="Administração de usuários", command=self.abrir_admin)
        btn_admin.pack(pady=5)
        btn_recuperar = tk.Button(self.frame, text="Esqueci minha senha", command=self.recuperar_senha)
        btn_recuperar.pack(pady=5)
        self.msg = tk.Label(self.frame, text="")
        self.msg.pack()

    def tentar_login(self):
        login = self.entry_login.get()
        senha = self.entry_senha.get()
        if login in self.usuarios and self.usuarios[login]["senha"] == hash_senha(senha):
            self.usuario_logado = login
            self.frame.destroy()
            self.on_success()
        else:
            self.msg.config(text="Login ou senha incorretos.")

    def abrir_admin(self):
        AdminWindow(self.master, self.usuarios, self.atualizar_usuarios, self.usuario_logado)

    def atualizar_usuarios(self, usuarios):
        self.usuarios = usuarios
        salvar_usuarios(usuarios)

    def recuperar_senha(self):
        login = simpledialog.askstring("Recuperação de senha", "Informe seu login:", parent=self.master)
        if not login or login not in self.usuarios:
            messagebox.showerror("Erro", "Login não encontrado.")
            return
        email = self.usuarios[login]["email"]
        codigo = str(random.randint(100000, 999999))
        enviado = enviar_codigo_email(email, codigo)
        if not enviado:
            messagebox.showerror("Erro", "Não foi possível enviar o e-mail. Verifique as configurações.")
            return
        codigo_usuario = simpledialog.askstring("Código de segurança", f"Um código foi enviado para {email}. Digite o código recebido:", parent=self.master)
        if codigo_usuario != codigo:
            messagebox.showerror("Erro", "Código incorreto.")
            return
        nova_senha = simpledialog.askstring("Nova senha", "Digite a nova senha:", parent=self.master, show="*")
        if not nova_senha:
            return
        self.usuarios[login]["senha"] = hash_senha(nova_senha)
        salvar_usuarios(self.usuarios)
        messagebox.showinfo("Sucesso", "Senha redefinida com sucesso!")

class AdminWindow:
    def __init__(self, master, usuarios, on_update, usuario_logado):
        self.master = master
        self.usuarios = usuarios
        self.on_update = on_update
        self.usuario_logado = usuario_logado
        self.win = tk.Toplevel(master)
        self.win.title("Administração de usuários")
        self.win.geometry("350x350")
        self.lista = tk.Listbox(self.win)
        self.lista.pack(fill="both", expand=True)
        self.atualizar_lista()
        btn_add = tk.Button(self.win, text="Criar usuário", command=self.criar_usuario)
        btn_add.pack(pady=2)
        btn_edit = tk.Button(self.win, text="Alterar senha", command=self.alterar_senha)
        btn_edit.pack(pady=2)
        btn_del = tk.Button(self.win, text="Excluir usuário", command=self.excluir_usuario)
        btn_del.pack(pady=2)

    def atualizar_lista(self):
        self.lista.delete(0, tk.END)
        for user in self.usuarios:
            self.lista.insert(tk.END, user)

    def criar_usuario(self):
        login = simpledialog.askstring("Novo usuário", "Login:", parent=self.win)
        if not login or login in self.usuarios:
            messagebox.showerror("Erro", "Login inválido ou já existe.")
            return
        email = simpledialog.askstring("E-mail", "E-mail do usuário:", parent=self.win)
        if not email:
            return
        senha = simpledialog.askstring("Senha", "Senha:", parent=self.win, show="*")
        if not senha:
            return
        self.usuarios[login] = {"senha": hash_senha(senha), "email": email}
        self.on_update(self.usuarios)
        self.atualizar_lista()
        messagebox.showinfo("Sucesso", "Usuário criado.")

    def alterar_senha(self):
        sel = self.lista.curselection()
        if not sel:
            messagebox.showinfo("Seleção", "Selecione um usuário.")
            return
        login = self.lista.get(sel[0])
        senha = simpledialog.askstring("Nova senha", f"Nova senha para {login}:", parent=self.win, show="*")
        if not senha:
            return
        self.usuarios[login]["senha"] = hash_senha(senha)
        self.on_update(self.usuarios)
        messagebox.showinfo("Sucesso", "Senha alterada.")

    def excluir_usuario(self):
        sel = self.lista.curselection()
        if not sel:
            messagebox.showinfo("Seleção", "Selecione um usuário.")
            return
        login = self.lista.get(sel[0])
        # Permite que o usuário 'admin' exclua qualquer usuário, outros só podem excluir a si mesmos
        if self.usuario_logado != "admin" and login != self.usuario_logado:
            messagebox.showerror("Permissão", "Somente o usuário administrador pode excluir outros usuários.")
            return
        if messagebox.askyesno("Excluir", f"Excluir usuário '{login}'?"):
            del self.usuarios[login]
            self.on_update(self.usuarios)
            self.atualizar_lista()
            messagebox.showinfo("Excluído", "Usuário excluído.")

if __name__ == "__main__":
    root = tk.Tk()
    def iniciar_app():
        app = App(root)
        root.mainloop()
    LoginWindow(root, iniciar_app)
    root.mainloop()
