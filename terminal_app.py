import streamlit as st
from datetime import datetime

from src.banco import (
    criar_tabelas,
    iniciar_apontamento,
    finalizar_apontamento,
)
from src.calculations import carregar_cenario

criar_tabelas()

st.set_page_config(page_title="TaktFlow - Terminal do Posto", layout="centered")
st.title("TaktFlow — Terminal do Posto")

cenario = carregar_cenario("dia")
sequencia_postos = cenario.postos_linha  # Posto 01 a 06, sem os postos de pré-montagem

# --- Estado inicial da sessão ---
if "indice_posto" not in st.session_state:
    st.session_state.indice_posto = 0

if "fluxo_ativo" not in st.session_state:
    st.session_state.fluxo_ativo = False

if "unidade_atual" not in st.session_state:
    st.session_state.unidade_atual = None

if "apontamento_id_atual" not in st.session_state:
    st.session_state.apontamento_id_atual = None

if "hora_inicio_posto_atual" not in st.session_state:
    st.session_state.hora_inicio_posto_atual = None

if "hora_inicio_sequencia" not in st.session_state:
    st.session_state.hora_inicio_sequencia = None

if "confirmando_avanco" not in st.session_state:
    st.session_state.confirmando_avanco = False

if "aguardando_novo_operador" not in st.session_state:
    st.session_state.aguardando_novo_operador = False

if "mensagem_conclusao" not in st.session_state:
    st.session_state.mensagem_conclusao = None

if "hora_fim_posto_concluido" not in st.session_state:
    st.session_state.hora_fim_posto_concluido = None

if "historico_ciclo" not in st.session_state:
    st.session_state.historico_ciclo = []

if "resumo_conclusao" not in st.session_state:
    st.session_state.resumo_conclusao = None


def posto_atual():
    return sequencia_postos[st.session_state.indice_posto]


def existe_proximo_posto() -> bool:
    return st.session_state.indice_posto < len(sequencia_postos) - 1


def formatar_duracao(segundos_totais: int) -> str:
    horas, resto = divmod(int(segundos_totais), 3600)
    minutos, segundos = divmod(resto, 60)
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"


def registrar_historico(posto, hora_inicio: datetime, hora_fim: datetime):
    duracao_segundos = (hora_fim - hora_inicio).total_seconds()
    esperado_segundos = posto.tempo_ciclo_min * 60
    diferenca_segundos = duracao_segundos - esperado_segundos
    houve_atraso = diferenca_segundos > 0

    st.session_state.historico_ciclo.append(
        {
            "Posto": posto.nome,
            "Início": hora_inicio.strftime("%H:%M:%S"),
            "Fim": hora_fim.strftime("%H:%M:%S"),
            "Duração": formatar_duracao(duracao_segundos),
            "Esperado": formatar_duracao(esperado_segundos),
            "Status": (
                f"Atraso de {formatar_duracao(diferenca_segundos)}"
                if houve_atraso
                else "Dentro do tempo"
            ),
        }
    )


# --- Tela 1: iniciar uma nova unidade na linha ---
if not st.session_state.fluxo_ativo and not st.session_state.aguardando_novo_operador:
    if st.session_state.mensagem_conclusao:
        st.success(st.session_state.mensagem_conclusao)

        if st.session_state.resumo_conclusao:
            st.subheader("Resumo do ciclo")
            st.table(st.session_state.resumo_conclusao)

        st.session_state.mensagem_conclusao = None
        st.session_state.resumo_conclusao = None

    st.subheader("Iniciar nova unidade na linha")

    unidade = st.text_input("Identificação da unidade (chassi, OP, série)")
    operador = st.text_input("Nome do operador (Posto 01)")

    if st.button("Iniciar", type="primary", use_container_width=True):
        if not unidade or not operador:
            st.warning("Preencha a unidade e o operador antes de iniciar.")
        else:
            st.session_state.indice_posto = 0
            st.session_state.historico_ciclo = []
            posto = sequencia_postos[0]
            agora = datetime.now()

            apontamento_id = iniciar_apontamento(
                posto=posto.nome,
                operador=operador,
                unidade=unidade,
                tempo_ciclo_esperado_min=posto.tempo_ciclo_min,
            )

            st.session_state.unidade_atual = unidade
            st.session_state.apontamento_id_atual = apontamento_id
            st.session_state.hora_inicio_posto_atual = agora
            st.session_state.hora_inicio_sequencia = agora
            st.session_state.fluxo_ativo = True
            st.rerun()

# --- Tela 2: confirmar início do próximo posto (troca de operador) ---
elif st.session_state.aguardando_novo_operador:
    posto = posto_atual()

    st.subheader(f"Confirmar início — {posto.nome}")
    st.caption(f"Unidade: {st.session_state.unidade_atual}")

    if st.session_state.hora_fim_posto_concluido:
        st.info(
            f"Posto anterior finalizado às "
            f"{st.session_state.hora_fim_posto_concluido.strftime('%H:%M:%S')}"
        )

    operador = st.text_input(f"Nome do operador ({posto.nome})")

    if st.button("Confirmar início", type="primary", use_container_width=True):
        if not operador:
            st.warning("Informe o operador antes de confirmar.")
        else:
            agora = datetime.now()

            apontamento_id = iniciar_apontamento(
                posto=posto.nome,
                operador=operador,
                unidade=st.session_state.unidade_atual,
                tempo_ciclo_esperado_min=posto.tempo_ciclo_min,
            )

            st.session_state.apontamento_id_atual = apontamento_id
            st.session_state.hora_inicio_posto_atual = agora
            st.session_state.aguardando_novo_operador = False
            st.session_state.fluxo_ativo = True
            st.rerun()

# --- Tela 3: posto em andamento ---
else:
    posto = posto_atual()

    st.subheader(f"Em andamento — {posto.nome}")
    st.write(f"**Unidade:** {st.session_state.unidade_atual}")
    st.write(
        f"**Início:** {st.session_state.hora_inicio_posto_atual.strftime('%H:%M:%S')}"
    )

    if not st.session_state.confirmando_avanco:
        if st.button("Finalizar posto", type="primary", use_container_width=True):
            st.session_state.confirmando_avanco = True
            st.rerun()

    else:
        agora = datetime.now()
        duracao_segundos = (agora - st.session_state.hora_inicio_posto_atual).total_seconds()

        st.write(f"**Fim:** {agora.strftime('%H:%M:%S')}")
        st.write(f"**Tempo decorrido no posto:** {formatar_duracao(duracao_segundos)}")

        if existe_proximo_posto():
            proximo = sequencia_postos[st.session_state.indice_posto + 1]
            st.warning(
                f"Confirma que todos os processos do {posto.nome} foram finalizados "
                f"e deseja encaminhar a unidade para o {proximo.nome}?"
            )
        else:
            st.warning(
                f"Confirma que todos os processos do {posto.nome} foram finalizados? "
                f"Esta é a última etapa da linha."
            )

        col_sim, col_nao = st.columns(2)

        with col_sim:
            if st.button("Sim, confirmar", type="primary", use_container_width=True):
                finalizar_apontamento(st.session_state.apontamento_id_atual)

                registrar_historico(
                    posto,
                    st.session_state.hora_inicio_posto_atual,
                    agora,
                )

                st.session_state.confirmando_avanco = False
                st.session_state.fluxo_ativo = False
                st.session_state.apontamento_id_atual = None
                st.session_state.hora_fim_posto_concluido = agora

                if existe_proximo_posto():
                    st.session_state.indice_posto += 1
                    st.session_state.aguardando_novo_operador = True
                else:
                    st.session_state.mensagem_conclusao = (
                        f"Unidade {st.session_state.unidade_atual} concluiu "
                        f"todos os postos da linha."
                    )
                    st.session_state.resumo_conclusao = list(
                        st.session_state.historico_ciclo
                    )
                    st.session_state.indice_posto = 0
                    st.session_state.unidade_atual = None
                    st.session_state.hora_inicio_sequencia = None
                    st.session_state.hora_fim_posto_concluido = None

                st.rerun()

        with col_nao:
            if st.button("Cancelar", use_container_width=True):
                st.session_state.confirmando_avanco = False
                st.rerun()