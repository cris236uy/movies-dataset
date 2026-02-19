import streamlit as st
import pandas as pd
import json
import os
import hashlib
from datetime import datetime, date, timedelta
import random

# ─────────────────────────────────────────────
#  CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="BarberPro — Sistema para Barbearias",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  ESTILOS GLOBAIS (compatível com Streamlit moderno)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap');

.tag {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: .75rem;
    font-weight: 600;
}
.tag-green { background: #1a3d2b; color: #4caf82; }
.tag-gold  { background: #2d2415; color: #c8a96e; }
.tag-red   { background: #2d1515; color: #e05555; }

.section-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.6rem;
    letter-spacing: 3px;
    color: #c8a96e;
    border-bottom: 1px solid #2a2a2a;
    padding-bottom: .4rem;
    margin-bottom: 1rem;
}

.logo-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3rem;
    letter-spacing: 4px;
    color: #c8a96e;
    text-align: center;
}
.logo-sub {
    text-align: center;
    color: #888;
    font-size: .85rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

.barb-card {
    background: #1f1f1f;
    border: 1px solid #2a2a2a;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: .8rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  BANCO DE DADOS (JSON em memória + arquivo)
# ─────────────────────────────────────────────
DB_FILE = "barberpro_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return _default_db()

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def _default_db():
    return {
        "barbearias": {
            "barberpro_admin": {
                "nome": "BarberPro Admin",
                "email": "admin@barberpro.com",
                "senha_hash": hashlib.sha256("admin123".encode()).hexdigest(),
                "plano": "admin",
                "ativo": True,
                "criado_em": str(date.today()),
            },
            "barbearia_demo": {
                "nome": "Barbearia Demo",
                "email": "demo@barbearia.com",
                "senha_hash": hashlib.sha256("demo123".encode()).hexdigest(),
                "plano": "pro",
                "ativo": True,
                "criado_em": str(date.today()),
            },
        },
        "clientes": {},        # {barbearia_id: [{...}]}
        "barbeiros": {},       # {barbearia_id: [{...}]}
        "agendamentos": {},    # {barbearia_id: [{...}]}
        "financeiro": {},      # {barbearia_id: [{...}]}
        "servicos": {},        # {barbearia_id: [{...}]}
    }

def get_section(db, section, barbearia_id):
    return db[section].get(barbearia_id, [])

def set_section(db, section, barbearia_id, data):
    db[section][barbearia_id] = data
    save_db(db)

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def hash_senha(s): return hashlib.sha256(s.encode()).hexdigest()
def hoje(): return str(date.today())
def uid(): return str(random.randint(100000, 999999))

PLANOS = {
    "basico": {"nome": "Básico", "preco": 49.90, "cor": "tag-gold"},
    "pro":    {"nome": "Pro",    "preco": 99.90, "cor": "tag-green"},
    "premium":{"nome": "Premium","preco": 179.90,"cor": "tag-green"},
    "admin":  {"nome": "Admin",  "preco": 0,     "cor": "tag-red"},
}

SERVICOS_DEFAULT = [
    {"id": uid(), "nome": "Corte Tradicional", "preco": 35.0, "duracao": 30},
    {"id": uid(), "nome": "Corte + Barba",      "preco": 60.0, "duracao": 60},
    {"id": uid(), "nome": "Barba",               "preco": 30.0, "duracao": 30},
    {"id": uid(), "nome": "Relaxamento",         "preco": 80.0, "duracao": 60},
    {"id": uid(), "nome": "Pigmentação",         "preco": 120.0,"duracao": 90},
]

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
if "db" not in st.session_state:
    st.session_state.db = load_db()
if "logado" not in st.session_state:
    st.session_state.logado = False
if "barbearia_id" not in st.session_state:
    st.session_state.barbearia_id = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

db = st.session_state.db

# ─────────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────────
def tela_login():
    st.markdown("""
    <div class='login-box'>
        <div class='logo-title'>✂ BARBERPRO</div>
        <div class='logo-sub'>Sistema de Gestão para Barbearias</div>
    </div>
    """, unsafe_allow_html=True)

    # Centralizar com colunas
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("### Entrar na sua conta")
        email = st.text_input("E-mail", placeholder="seu@email.com")
        senha = st.text_input("Senha", type="password", placeholder="••••••••")
        entrar = st.button("Entrar →", use_container_width=True)

        st.markdown("---")
        st.markdown("<small style='color:#888'>Não tem conta? Entre em contato: **contato@barberpro.com**</small>", unsafe_allow_html=True)
        st.markdown(f"<small style='color:#555'>Demo: `demo@barbearia.com` / `demo123`<br>Admin: `admin@barberpro.com` / `admin123`</small>", unsafe_allow_html=True)

    if entrar:
        for bid, b in db["barbearias"].items():
            if b["email"] == email and b["senha_hash"] == hash_senha(senha):
                if not b["ativo"]:
                    st.error("Conta desativada. Entre em contato com o suporte.")
                    return
                st.session_state.logado = True
                st.session_state.barbearia_id = bid
                st.session_state.is_admin = (b["plano"] == "admin")
                st.rerun()
        st.error("E-mail ou senha incorretos.")

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
def sidebar():
    bid = st.session_state.barbearia_id
    b = db["barbearias"][bid]
    plano = PLANOS[b["plano"]]

    with st.sidebar:
        st.markdown(f"<div style='font-family:Bebas Neue;font-size:1.8rem;color:#c8a96e;letter-spacing:3px;'>✂ BARBERPRO</div>", unsafe_allow_html=True)
        st.markdown(f"**{b['nome']}**")
        st.markdown(f"<span class='tag {plano['cor']}'>{plano['nome']}</span>", unsafe_allow_html=True)
        st.markdown("---")

        if st.session_state.is_admin:
            paginas = ["Dashboard Admin", "Barbearias", "Financeiro Global"]
        else:
            paginas = ["Dashboard", "Agendamentos", "Clientes", "Barbeiros", "Serviços", "Financeiro", "Configurações"]

        page = st.radio("Navegação", paginas, label_visibility="collapsed")

        st.markdown("---")
        if st.button("Sair", use_container_width=True):
            st.session_state.logado = False
            st.session_state.barbearia_id = None
            st.rerun()

    return page

# ═══════════════════════════════════════════════
#  PÁGINAS — BARBEARIA
# ═══════════════════════════════════════════════

def pg_dashboard():
    bid = st.session_state.barbearia_id
    st.markdown("<div class='section-title'>DASHBOARD</div>", unsafe_allow_html=True)

    agendamentos = get_section(db, "agendamentos", bid)
    clientes = get_section(db, "clientes", bid)
    financeiro = get_section(db, "financeiro", bid)
    barbeiros = get_section(db, "barbeiros", bid)

    hoje_str = hoje()
    ag_hoje = [a for a in agendamentos if a.get("data") == hoje_str]
    receita_mes = sum(f["valor"] for f in financeiro if f.get("tipo") == "receita" and f.get("data", "").startswith(hoje_str[:7]))
    despesa_mes = sum(f["valor"] for f in financeiro if f.get("tipo") == "despesa" and f.get("data", "").startswith(hoje_str[:7]))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Agendamentos Hoje", len(ag_hoje))
    with c2:
        st.metric("Total de Clientes", len(clientes))
    with c3:
        st.metric("Receita do Mês", f"R$ {receita_mes:,.2f}")
    with c4:
        st.metric("Barbeiros Ativos", len([b for b in barbeiros if b.get("ativo")]))

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Agendamentos de Hoje")
        if ag_hoje:
            df = pd.DataFrame(ag_hoje)[["hora", "cliente", "servico", "barbeiro", "status"]]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum agendamento para hoje.")

    with col2:
        st.markdown("#### Resumo Financeiro do Mês")
        lucro = receita_mes - despesa_mes
        st.metric("Receita", f"R$ {receita_mes:,.2f}")
        st.metric("Despesas", f"R$ {despesa_mes:,.2f}")
        st.metric("Lucro", f"R$ {lucro:,.2f}", delta=f"R$ {lucro:,.2f}")


def pg_agendamentos():
    bid = st.session_state.barbearia_id
    st.markdown("<div class='section-title'>AGENDAMENTOS</div>", unsafe_allow_html=True)

    agendamentos = get_section(db, "agendamentos", bid)
    clientes = get_section(db, "clientes", bid)
    barbeiros = get_section(db, "barbeiros", bid)
    servicos = get_section(db, "servicos", bid) or SERVICOS_DEFAULT

    tab1, tab2 = st.tabs(["📋 Lista", "➕ Novo Agendamento"])

    with tab1:
        filtro_data = st.date_input("Filtrar por data", value=date.today())
        filtro_str = str(filtro_data)
        ag_filtrado = [a for a in agendamentos if a.get("data") == filtro_str]

        if ag_filtrado:
            df = pd.DataFrame(ag_filtrado)
            cols = [c for c in ["hora", "cliente", "servico", "barbeiro", "status", "valor"] if c in df.columns]
            st.dataframe(df[cols], use_container_width=True, hide_index=True)

            # Alterar status
            st.markdown("#### Atualizar Status")
            ids = [a["id"] for a in ag_filtrado]
            sel_id = st.selectbox("Selecionar agendamento (ID)", ids)
            novo_status = st.selectbox("Novo status", ["agendado", "concluído", "cancelado"])
            if st.button("Atualizar"):
                for a in agendamentos:
                    if a["id"] == sel_id:
                        a["status"] = novo_status
                        # Se concluído, registra receita
                        if novo_status == "concluído":
                            fin = get_section(db, "financeiro", bid)
                            fin.append({
                                "id": uid(),
                                "data": hoje(),
                                "descricao": f"Serviço: {a.get('servico','?')} - {a.get('cliente','?')}",
                                "valor": a.get("valor", 0),
                                "tipo": "receita",
                                "categoria": "serviço",
                            })
                            set_section(db, "financeiro", bid, fin)
                set_section(db, "agendamentos", bid, agendamentos)
                st.success("Status atualizado!")
                st.rerun()
        else:
            st.info("Nenhum agendamento nesta data.")

    with tab2:
        nomes_clientes = [c["nome"] for c in clientes] if clientes else []
        nomes_barbeiros = [b["nome"] for b in barbeiros if b.get("ativo")] if barbeiros else []
        nomes_servicos = [s["nome"] for s in servicos]

        c1, c2 = st.columns(2)
        with c1:
            cliente_nome = st.selectbox("Cliente", ["-- selecione --"] + nomes_clientes)
            servico_nome = st.selectbox("Serviço", ["-- selecione --"] + nomes_servicos)
        with c2:
            barbeiro_nome = st.selectbox("Barbeiro", ["-- selecione --"] + nomes_barbeiros)
            data_ag = st.date_input("Data", value=date.today(), key="data_ag")
            hora_ag = st.time_input("Hora", value=datetime.now().replace(minute=0, second=0, microsecond=0))

        obs = st.text_area("Observações (opcional)", height=80)

        if st.button("Agendar"):
            if cliente_nome == "-- selecione --" or barbeiro_nome == "-- selecione --" or servico_nome == "-- selecione --":
                st.warning("Preencha todos os campos obrigatórios.")
            else:
                serv_obj = next((s for s in servicos if s["nome"] == servico_nome), {})
                novo = {
                    "id": uid(),
                    "data": str(data_ag),
                    "hora": str(hora_ag)[:5],
                    "cliente": cliente_nome,
                    "barbeiro": barbeiro_nome,
                    "servico": servico_nome,
                    "valor": serv_obj.get("preco", 0),
                    "status": "agendado",
                    "obs": obs,
                    "criado_em": hoje(),
                }
                agendamentos.append(novo)
                set_section(db, "agendamentos", bid, agendamentos)
                st.success(f"Agendamento criado para {data_ag} às {str(hora_ag)[:5]}!")
                st.rerun()


def pg_clientes():
    bid = st.session_state.barbearia_id
    st.markdown("<div class='section-title'>CLIENTES</div>", unsafe_allow_html=True)

    clientes = get_section(db, "clientes", bid)
    tab1, tab2 = st.tabs(["👥 Cadastro", "➕ Novo Cliente"])

    with tab1:
        if clientes:
            busca = st.text_input("🔍 Buscar cliente", placeholder="Nome, telefone ou e-mail...")
            filtrado = [c for c in clientes if busca.lower() in c.get("nome","").lower()
                        or busca.lower() in c.get("telefone","").lower()
                        or busca.lower() in c.get("email","").lower()] if busca else clientes
            df = pd.DataFrame(filtrado)
            cols = [c for c in ["nome","telefone","email","nascimento","obs"] if c in df.columns]
            st.dataframe(df[cols] if cols else df, use_container_width=True, hide_index=True)
            st.caption(f"{len(filtrado)} clientes encontrados")
        else:
            st.info("Nenhum cliente cadastrado ainda.")

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome completo *")
            telefone = st.text_input("Telefone", placeholder="(11) 99999-9999")
        with c2:
            email = st.text_input("E-mail")
            nasc = st.date_input("Data de nascimento", value=date(1990, 1, 1))
        obs = st.text_area("Observações", height=80)

        if st.button("Cadastrar Cliente"):
            if not nome:
                st.warning("Nome é obrigatório.")
            else:
                clientes.append({
                    "id": uid(), "nome": nome, "telefone": telefone,
                    "email": email, "nascimento": str(nasc), "obs": obs,
                    "criado_em": hoje(),
                })
                set_section(db, "clientes", bid, clientes)
                st.success(f"Cliente **{nome}** cadastrado!")
                st.rerun()


def pg_barbeiros():
    bid = st.session_state.barbearia_id
    st.markdown("<div class='section-title'>BARBEIROS</div>", unsafe_allow_html=True)

    barbeiros = get_section(db, "barbeiros", bid)
    tab1, tab2 = st.tabs(["✂️ Equipe", "➕ Novo Barbeiro"])

    with tab1:
        if barbeiros:
            for b in barbeiros:
                status = "tag-green" if b.get("ativo") else "tag-red"
                st.markdown(f"""
                <div style='background:#161616;border:1px solid #2a2a2a;border-radius:8px;padding:1rem;margin-bottom:.8rem;'>
                    <strong style='font-size:1.1rem'>{b['nome']}</strong>
                    <span class='tag {status}' style='margin-left:10px'>{'Ativo' if b.get('ativo') else 'Inativo'}</span><br>
                    <small style='color:#888'>Tel: {b.get('telefone','—')} | Especialidade: {b.get('especialidade','—')} | Comissão: {b.get('comissao',0)}%</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhum barbeiro cadastrado.")

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome completo *")
            telefone = st.text_input("Telefone")
        with c2:
            especialidade = st.text_input("Especialidade", placeholder="Ex: Degradê, Barba, Coloração")
            comissao = st.number_input("Comissão (%)", min_value=0, max_value=100, value=40)
        ativo = st.checkbox("Barbeiro ativo", value=True)

        if st.button("Cadastrar Barbeiro"):
            if not nome:
                st.warning("Nome é obrigatório.")
            else:
                barbeiros.append({
                    "id": uid(), "nome": nome, "telefone": telefone,
                    "especialidade": especialidade, "comissao": comissao,
                    "ativo": ativo, "criado_em": hoje(),
                })
                set_section(db, "barbeiros", bid, barbeiros)
                st.success(f"Barbeiro **{nome}** cadastrado!")
                st.rerun()


def pg_servicos():
    bid = st.session_state.barbearia_id
    st.markdown("<div class='section-title'>SERVIÇOS</div>", unsafe_allow_html=True)

    servicos = get_section(db, "servicos", bid)
    if not servicos:
        servicos = SERVICOS_DEFAULT.copy()
        set_section(db, "servicos", bid, servicos)

    tab1, tab2 = st.tabs(["📋 Serviços", "➕ Novo Serviço"])

    with tab1:
        df = pd.DataFrame(servicos)
        cols = [c for c in ["nome","preco","duracao"] if c in df.columns]
        df_show = df[cols].copy() if cols else df
        if "preco" in df_show.columns:
            df_show["preco"] = df_show["preco"].apply(lambda x: f"R$ {x:.2f}")
        if "duracao" in df_show.columns:
            df_show["duracao"] = df_show["duracao"].apply(lambda x: f"{x} min")
        df_show.columns = [c.capitalize() for c in df_show.columns]
        st.dataframe(df_show, use_container_width=True, hide_index=True)

    with tab2:
        c1, c2, c3 = st.columns(3)
        with c1:
            nome = st.text_input("Nome do serviço *")
        with c2:
            preco = st.number_input("Preço (R$)", min_value=0.0, value=50.0, step=5.0)
        with c3:
            duracao = st.number_input("Duração (min)", min_value=15, value=30, step=15)

        if st.button("Adicionar Serviço"):
            if not nome:
                st.warning("Nome é obrigatório.")
            else:
                servicos.append({"id": uid(), "nome": nome, "preco": preco, "duracao": duracao})
                set_section(db, "servicos", bid, servicos)
                st.success(f"Serviço **{nome}** adicionado!")
                st.rerun()


def pg_financeiro():
    bid = st.session_state.barbearia_id
    st.markdown("<div class='section-title'>FINANCEIRO</div>", unsafe_allow_html=True)

    financeiro = get_section(db, "financeiro", bid)
    tab1, tab2, tab3 = st.tabs(["📊 Resumo", "📋 Lançamentos", "➕ Novo Lançamento"])

    with tab1:
        mes_atual = date.today().strftime("%Y-%m")
        rec_mes = sum(f["valor"] for f in financeiro if f.get("tipo") == "receita" and f.get("data","").startswith(mes_atual))
        des_mes = sum(f["valor"] for f in financeiro if f.get("tipo") == "despesa" and f.get("data","").startswith(mes_atual))
        lucro = rec_mes - des_mes

        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Receitas (mês)", f"R$ {rec_mes:,.2f}")
        with c2: st.metric("Despesas (mês)", f"R$ {des_mes:,.2f}")
        with c3: st.metric("Lucro (mês)", f"R$ {lucro:,.2f}", delta=f"R$ {lucro:,.2f}")

        # Gráfico simples
        if financeiro:
            df = pd.DataFrame(financeiro)
            df["data"] = pd.to_da
