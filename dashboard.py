import streamlit as st
import requests
import pandas as pd
import altair as alt

API_URL_JOGADOR = "http://127.0.0.1:8000/api/enxadrista/jogador/"
API_URL_TORNEIO = "http://127.0.0.1:8000/api/torneio/"

st.set_page_config(page_title="Torneio de Xadrez", layout="wide")
st.title("Gerenciamento de Torneio de Xadrez")

# ========================
# Estrutura em abas
# ========================
abas = st.tabs(["Geral", "Enxadristas", "Listagens", "Gráficos", "Importar Jogadores"])

# ------------------------
# Aba Geral (dados do torneio)
# ------------------------
with abas[0]:
    st.subheader("Dados do Torneio")
    
    col1, col2 = st.columns(2)
    with col1:
        denominacao = st.text_input("Denominação", "Campeonato de Xadrez 2025")
        organizador = st.text_input("Organizador", "Federação de Xadrez")
        diretor = st.text_input("Diretor do Torneio", "")
        arbitro_principal = st.text_input("Árbitro Principal", "")
        arbitro_assistente = st.text_input("Árbitro Assistente", "")
        fed = st.selectbox("Federação", ["Selecione", "Brasil", "Portugal", "Espanha", "Argentina", "Outro"])
        local = st.text_input("Local", "Campinas - SP")
    
    with col2:
        rodadas = st.number_input("Rodadas", min_value=1, value=9)
        ritmo = st.text_input("Ritmo de Jogo", "90 min + 30 seg por lance")
        categorias = st.text_input("Categorias (ex: U8,U10,U12,U14)")
        data_inicio = st.date_input("Data de início")
        data_fim = st.date_input("Data de término")
        data_corte = st.date_input("Data de corte de rating")
        rating_min = st.number_input("Rating mínimo para média", min_value=0, value=1000)

    st.subheader("Configurações do Torneio")
    col3, col4, col5 = st.columns(3)
    with col3:
        classificar_por = st.radio("Classificar por", [
            "Rating Nacional",
            "Rating Internacional",
            "Rating int. depois do Rating nac.",
            "Elo máximo (nac, int)"
        ])
    with col4:
        cor_jogo = st.radio("Cor no jogo em casa", ["Brancas", "Negras", "Igual a todos"])
        emparceiramento = st.radio("Emparceiramento", ["Pontos do jogo", "2,1,0", "3,1,0"])
    with col5:
        avaliacao_fide = st.radio("Avaliação FIDE", ["Sim", "Não"])
        avaliacao_nacional = st.radio("Avaliação Nacional", ["Sim", "Não"])
        pontos_partida = st.radio("Pontos iniciais para equipe", [3, 2, 1, 0])

    st.subheader("Tipo de Torneio")
    tipo_torneio = st.radio(
        "Sistema de emparceiramento:",
        [
            "Sistema Suíço",
            "Sistema Suíço (desempate por equipes)",
            "Sistema Suíço por equipes",
            "Round Robin",
            "Round Robin por equipes",
            "KO-System",
            "KO-System for Teams"
        ]
    )

    if st.button("Salvar Dados do Torneio"):
        torneio = {
            "denominacao": denominacao,
            "organizador": organizador,
            "diretor": diretor,
            "arbitro_principal": arbitro_principal,
            "arbitro_assistente": arbitro_assistente,
            "federacao": fed,
            "local": local,
            "rodadas": rodadas,
            "ritmo": ritmo,
            "categorias": categorias,
            "data_inicio": str(data_inicio),
            "data_fim": str(data_fim),
            "data_corte": str(data_corte),
            "rating_min": rating_min,
            "classificar_por": classificar_por,
            "cor_jogo": cor_jogo,
            "emparceiramento": emparceiramento,
            "avaliacao_fide": avaliacao_fide,
            "avaliacao_nacional": avaliacao_nacional,
            "pontos_partida": pontos_partida,
            "tipo_torneio": tipo_torneio
        }

        try:
            response = requests.post(API_URL_TORNEIO, json=torneio)
            if response.status_code in (200, 201):
                st.success(f"Torneio salvo com sucesso: {denominacao}")
            else:
                st.error(f"Erro ao salvar: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Erro de conexão com a API: {e}")

# ------------------------
# Aba Enxadristas
# ------------------------
with abas[1]:
    st.subheader("Cadastrar Enxadrista")
    with st.form("cadastro_form"):
        nome = st.text_input("Nome")
        categoria = st.text_input("Categoria")
        rating = st.number_input("Rating", min_value=0, value=1200)

        submitted = st.form_submit_button("Cadastrar")
        if submitted:
            novo_enxadrista = {"id": 0, "nome": nome, "categoria": categoria, "rating": rating}
            try:
                response = requests.post(API_URL_JOGADOR, json=novo_enxadrista)
                if response.status_code in (200, 201):
                    st.success("Enxadrista cadastrado com sucesso!")
                else:
                    st.error(f"Erro ao cadastrar: {response.status_code}")
            except Exception as e:
                st.error(f"Erro de conexão: {e}")

    st.subheader("Deletar Enxadrista")
    try:
        response = requests.get(API_URL_JOGADOR)
        if response.status_code == 200:
            enxadristas = response.json()
            if enxadristas:
                nomes = {f"{e['id']} - {e['nome']}": e['id'] for e in enxadristas}
                escolhido = st.selectbox("Selecione para deletar", list(nomes.keys()))
                if st.button("Deletar"):
                    delete_url = f"{API_URL_JOGADOR}{nomes[escolhido]}"
                    delete_response = requests.delete(delete_url)
                    if delete_response.status_code in (200, 204):
                        st.success("Enxadrista deletado!")
                    else:
                        st.error(f"Erro: {delete_response.status_code}")
            else:
                st.info("Nenhum enxadrista cadastrado")
    except Exception as e:
        st.error(f"Erro ao buscar enxadristas: {e}")

# ------------------------
# Aba Listagens
# ------------------------
with abas[2]:
    st.subheader("Lista de Enxadristas")
    try:
        response = requests.get(API_URL_JOGADOR)
        enxadristas = response.json()
        df = pd.DataFrame(enxadristas)
        st.dataframe(df, use_container_width=True)
    except:
        st.warning("Não foi possível carregar os enxadristas.")

# ------------------------
# Aba Gráficos
# ------------------------
with abas[3]:
    st.subheader("Análises do Torneio")
    try:
        response = requests.get(API_URL_JOGADOR)
        enxadristas = response.json()
        df = pd.DataFrame(enxadristas)
        if not df.empty:
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X("rating", bin=alt.Bin(maxbins=20)),
                y='count()'
            )
            st.altair_chart(chart, use_container_width=True)

            chart_cat = alt.Chart(df).mark_bar().encode(
                x='categoria',
                y='count()'
            )
            st.altair_chart(chart_cat, use_container_width=True)
    except:
        st.warning("Sem dados para exibir gráficos.")

# ------------------------
# Aba Importar Jogadores
# ------------------------
with abas[4]:
    st.subheader("Importar Jogadores a partir de Lista")

    origem = st.radio("Origem da lista:", ["Arquivo CSV", "Base FIDE (simulado)", "Outro"])

    if origem == "Arquivo CSV":
        arquivo = st.file_uploader("Selecione o arquivo CSV com jogadores", type=["csv"])
        if arquivo:
            df_import = pd.read_csv(arquivo)
            st.dataframe(df_import, use_container_width=True)

            if st.button("Importar Jogadores do CSV"):
                for _, row in df_import.iterrows():
                    jogador = {
                        "id": 0,
                        "nome": row.get("nome", ""),
                        "categoria": row.get("categoria", ""),
                        "rating": int(row.get("rating", 0))
                    }
                    try:
                        response = requests.post(API_URL_JOGADOR, json=jogador)
                    except:
                        st.error("Erro ao enviar jogador para API.")
                st.success("Jogadores importados com sucesso!")

    elif origem == "Base FIDE (simulado)":
        st.info("Integração real com FIDE ainda não implementada. Aqui poderíamos puxar por API.")

    elif origem == "Outro":
        st.text_input("Especifique a origem")
