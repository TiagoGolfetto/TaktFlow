import streamlit as st
from datetime import datetime

from src.banco import criar_tabelas, listar_apontamentos_em_andamento, listar_historico
from src.calculations import carregar_cenario

criar_tabelas()

st.set_page_config(page_title="TaktFlow - Painel do Gestor", layout="wide")

# Recarrega a página sozinha a cada 60 segundos, para o painel ficar "vivo"
st.markdown("<meta http-equiv='refresh' content='1000'>", unsafe_allow_html=True)

st.title("TaktFlow — Painel do Gestor")

cenario = carregar_cenario("dia")

apontamentos_abertos = listar_apontamentos_em_andamento()
mapa_apontamentos = {registro["posto"]: registro for registro in apontamentos_abertos}

# Último apontamento finalizado de cada posto, para exibir como "Concluído"
historico_status = listar_historico(limite=100)
mapa_finalizados = {}
for registro in historico_status:
    if registro["posto"] not in mapa_finalizados:
        mapa_finalizados[registro["posto"]] = registro

CORES_STATUS = {
    "ocioso": "#BDBDBD",
    "no_prazo": "#7CB342",
    "atencao": "#F7941D",
    "atrasado": "#E53935",
    "concluido": "#C8E6C9",
}

TEXTO_STATUS = {
    "ocioso": "Ocioso",
    "no_prazo": "Dentro do tempo",
    "atencao": "Atenção",
    "atrasado": "Atrasado",
    "concluido": "Concluído",
}

COR_TEXTO_STATUS = {
    "ocioso": "white",
    "no_prazo": "white",
    "atencao": "white",
    "atrasado": "white",
    "concluido": "#33691E",
}


def calcular_status(posto, apontamento, finalizado):
    if apontamento is not None:
        hora_inicio = datetime.fromisoformat(apontamento["hora_inicio"])
        decorrido_segundos = (datetime.now() - hora_inicio).total_seconds()
        esperado_segundos = posto.tempo_ciclo_min * 60

        if decorrido_segundos <= esperado_segundos:
            status = "no_prazo"
        elif decorrido_segundos <= esperado_segundos * 1.2:
            status = "atencao"
        else:
            status = "atrasado"

        return status, decorrido_segundos, esperado_segundos

    if finalizado is not None:
        hora_inicio = datetime.fromisoformat(finalizado["hora_inicio"])
        hora_fim = datetime.fromisoformat(finalizado["hora_fim"])
        duracao_segundos = (hora_fim - hora_inicio).total_seconds()
        esperado_segundos = posto.tempo_ciclo_min * 60
        return "concluido", duracao_segundos, esperado_segundos

    return "ocioso", None, None


def formatar_duracao(segundos: float) -> str:
    minutos, segundos = divmod(int(segundos), 60)
    return f"{minutos:02d}:{segundos:02d}"


def renderizar_cards(postos):
    colunas = st.columns(len(postos))

    for coluna, posto in zip(colunas, postos):
        apontamento = mapa_apontamentos.get(posto.nome)
        finalizado = mapa_finalizados.get(posto.nome)
        status, decorrido, esperado = calcular_status(posto, apontamento, finalizado)
        cor = CORES_STATUS[status]
        cor_texto = COR_TEXTO_STATUS[status]

        with coluna:
            st.markdown(
                f"""
                <div style="background-color:{cor}; border-radius:12px;
                            padding:16px; text-align:center; color:{cor_texto};">
                    <div style="font-size:1rem; font-weight:bold;">{posto.nome}</div>
                    <div style="font-size:0.85rem; margin-top:4px;">
                        {TEXTO_STATUS[status]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if apontamento:
                st.caption(f"Operador: {apontamento['operador']}")
                st.caption(f"Unidade: {apontamento['unidade']}")
                st.caption(
                    f"Decorrido: {formatar_duracao(decorrido)} "
                    f"/ Esperado: {formatar_duracao(esperado)}"
                )
            elif finalizado:
                st.caption(f"Operador: {finalizado['operador']}")
                st.caption(f"Unidade: {finalizado['unidade']}")
                st.caption(
                    f"Duração: {formatar_duracao(decorrido)} "
                    f"/ Esperado: {formatar_duracao(esperado)}"
                )
            else:
                st.caption("Sem apontamento em andamento")


st.subheader("Linha de Montagem")
renderizar_cards(cenario.postos_linha)

st.divider()

st.subheader("Histórico recente")
historico = listar_historico(limite=10)

if historico:
    linhas_tabela = [
        {
            "Posto": registro["posto"],
            "Operador": registro["operador"],
            "Unidade": registro["unidade"],
            "Início": registro["hora_inicio"],
            "Fim": registro["hora_fim"],
        }
        for registro in historico
    ]
    st.table(linhas_tabela)
else:
    st.caption("Nenhum apontamento finalizado ainda.")