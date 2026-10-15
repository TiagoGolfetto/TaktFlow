import json
from pathlib import Path
from dataclasses import dataclass, field

from src.tempo import parse_tempo, para_minutos, para_horas


@dataclass
class Posto:
    nome: str
    tempo_ciclo: str
    operadores: int
    disponibilidade: float = 1.0
    capacidade_referencia: float | None = None

    @property
    def tempo_ciclo_min(self) -> float:
        return para_minutos(parse_tempo(self.tempo_ciclo))


@dataclass
class Cenario:
    nome: str
    descricao: str
    horas_produtivas: str
    postos_linha: list[Posto] = field(default_factory=list)
    postos_pre: list[Posto] = field(default_factory=list)

    @property
    def horas_produtivas_decimal(self) -> float:
        return para_horas(parse_tempo(self.horas_produtivas))


def calcular_capacidade_posto(posto: Posto, horas_produtivas: float) -> float:
    if posto.capacidade_referencia is not None:
        return posto.capacidade_referencia

    if posto.tempo_ciclo_min <= 0:
        raise ValueError(f"Tempo de ciclo inválido no {posto.nome}.")

    if posto.operadores <= 0:
        raise ValueError(f"Operadores inválidos no {posto.nome}.")

    minutos_disponiveis = horas_produtivas * 60 * posto.disponibilidade

    return minutos_disponiveis * posto.operadores / posto.tempo_ciclo_min


def calcular_takt_time(horas_disponiveis: float, demanda: int) -> float:
    if horas_disponiveis <= 0:
        raise ValueError("As horas disponíveis devem ser maiores que zero.")

    if demanda <= 0:
        raise ValueError("A demanda deve ser maior que zero.")

    return (horas_disponiveis * 60) / demanda


def _analisar_grupo(postos: list[Posto], horas: float) -> dict:
    resultados = [
        {
            "posto": posto.nome,
            "tempo_ciclo": posto.tempo_ciclo,
            "operadores": posto.operadores,
            "capacidade": calcular_capacidade_posto(posto, horas),
        }
        for posto in postos
    ]

    gargalo = min(resultados, key=lambda item: item["capacidade"])

    return {
        "postos": resultados,
        "gargalo": gargalo,
        "capacidade_grupo": gargalo["capacidade"],
    }


def analisar_cenario(cenario: Cenario) -> dict:
    horas = cenario.horas_produtivas_decimal

    analise_linha = _analisar_grupo(cenario.postos_linha, horas)
    analise_pre = _analisar_grupo(cenario.postos_pre, horas)

    return {
        "cenario": cenario.nome,
        "descricao": cenario.descricao,
        "linha": analise_linha,
        "pre_montagem": analise_pre,
    }


def carregar_cenario(nome_cenario: str, caminho: str = "config/cenarios.json") -> Cenario:
    with open(Path(caminho), "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if nome_cenario not in dados:
        raise ValueError(f"Cenário '{nome_cenario}' não encontrado em {caminho}.")

    dados_cenario = dados[nome_cenario]

    def montar_postos(chave: str) -> list[Posto]:
        return [
            Posto(
                nome=posto["nome"],
                tempo_ciclo=posto["tempo_ciclo"],
                operadores=posto["operadores"],
                disponibilidade=dados_cenario["disponibilidade"],
                capacidade_referencia=posto.get("capacidade_referencia"),
            )
            for posto in dados_cenario[chave]
        ]

    return Cenario(
        nome=nome_cenario,
        descricao=dados_cenario["descricao"],
        horas_produtivas=dados_cenario["horas_produtivas"],
        postos_linha=montar_postos("postos_linha"),
        postos_pre=montar_postos("postos_pre"),
    )