# import sqlite3
# from contextlib import contextmanager
# from pathlib import Path

# CAMINHO_BANCO = Path("data/apontamentos.db")


# @contextmanager
# def conectar():
#     conexao = sqlite3.connect(CAMINHO_BANCO)
#     conexao.row_factory = sqlite3.Row
#     try:
#         yield conexao
#         conexao.commit()
#     finally:
#         conexao.close()


# def criar_tabelas():
#     with conectar() as conexao:
#         conexao.execute(
#             """
#             CREATE TABLE IF NOT EXISTS apontamentos (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 posto TEXT NOT NULL,
#                 operador TEXT NOT NULL,
#                 unidade TEXT,
#                 hora_inicio TEXT NOT NULL,
#                 hora_fim TEXT,
#                 tempo_ciclo_esperado_min REAL NOT NULL,
#                 status TEXT NOT NULL DEFAULT 'em_andamento'
#             )
#             """
#         )


# def iniciar_apontamento(posto: str, operador: str, unidade: str, tempo_ciclo_esperado_min: float) -> int:
#     from datetime import datetime

#     with conectar() as conexao:
#         cursor = conexao.execute(
#             """
#             INSERT INTO apontamentos
#                 (posto, operador, unidade, hora_inicio, tempo_ciclo_esperado_min, status)
#             VALUES (?, ?, ?, ?, ?, 'em_andamento')
#             """,
#             (posto, operador, unidade, datetime.now().isoformat(), tempo_ciclo_esperado_min),
#         )
#         return cursor.lastrowid


# def finalizar_apontamento(apontamento_id: int):
#     from datetime import datetime

#     with conectar() as conexao:
#         conexao.execute(
#             """
#             UPDATE apontamentos
#             SET hora_fim = ?, status = 'finalizado'
#             WHERE id = ?
#             """,
#             (datetime.now().isoformat(), apontamento_id),
#         )


# def buscar_apontamento_aberto(posto: str):
#     with conectar() as conexao:
#         cursor = conexao.execute(
#             """
#             SELECT * FROM apontamentos
#             WHERE posto = ? AND status = 'em_andamento'
#             ORDER BY hora_inicio DESC
#             LIMIT 1
#             """,
#             (posto,),
#         )
#         return cursor.fetchone()


# def listar_apontamentos_em_andamento():
#     with conectar() as conexao:
#         cursor = conexao.execute(
#             """
#             SELECT * FROM apontamentos
#             WHERE status = 'em_andamento'
#             ORDER BY hora_inicio ASC
#             """
#         )
#         return cursor.fetchall()


# def listar_historico(limite: int = 20):
#     with conectar() as conexao:
#         cursor = conexao.execute(
#             """
#             SELECT * FROM apontamentos
#             WHERE status = 'finalizado'
#             ORDER BY hora_fim DESC
#             LIMIT ?
#             """,
#             (limite,),
#         )
#         return cursor.fetchall()
        

import sqlite3
from contextlib import contextmanager
from pathlib import Path

CAMINHO_BANCO = Path("data/apontamentos.db")


@contextmanager
def conectar():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    try:
        yield conexao
        conexao.commit()
    finally:
        conexao.close()


def criar_tabelas():
    with conectar() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS apontamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                posto TEXT NOT NULL,
                operador TEXT NOT NULL,
                unidade TEXT,
                hora_inicio TEXT NOT NULL,
                hora_fim TEXT,
                tempo_ciclo_esperado_min REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'em_andamento'
            )
            """
        )


def iniciar_apontamento(posto: str, operador: str, unidade: str, tempo_ciclo_esperado_min: float) -> int:
    from datetime import datetime

    with conectar() as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO apontamentos
                (posto, operador, unidade, hora_inicio, tempo_ciclo_esperado_min, status)
            VALUES (?, ?, ?, ?, ?, 'em_andamento')
            """,
            (posto, operador, unidade, datetime.now().isoformat(), tempo_ciclo_esperado_min),
        )
        return cursor.lastrowid


def finalizar_apontamento(apontamento_id: int):
    from datetime import datetime

    with conectar() as conexao:
        conexao.execute(
            """
            UPDATE apontamentos
            SET hora_fim = ?, status = 'finalizado'
            WHERE id = ?
            """,
            (datetime.now().isoformat(), apontamento_id),
        )


def buscar_apontamento_aberto(posto: str):
    with conectar() as conexao:
        cursor = conexao.execute(
            """
            SELECT * FROM apontamentos
            WHERE posto = ? AND status = 'em_andamento'
            ORDER BY hora_inicio DESC
            LIMIT 1
            """,
            (posto,),
        )
        return cursor.fetchone()


def listar_apontamentos_em_andamento():
    with conectar() as conexao:
        cursor = conexao.execute(
            """
            SELECT * FROM apontamentos
            WHERE status = 'em_andamento'
            ORDER BY hora_inicio ASC
            """
        )
        return cursor.fetchall()


def listar_historico(limite: int = 20):
    with conectar() as conexao:
        cursor = conexao.execute(
            """
            SELECT * FROM apontamentos
            WHERE status = 'finalizado'
            ORDER BY hora_fim DESC
            LIMIT ?
            """,
            (limite,),
        )
        return cursor.fetchall()


def fechar_apontamentos_pendentes():
    """
    Finaliza automaticamente qualquer apontamento que tenha ficado
    'em_andamento' de um ciclo anterior (registro órfão), evitando que
    o painel do gestor mostre postos atrasados indevidamente quando
    uma nova unidade começa a percorrer a linha.
    """
    from datetime import datetime

    with conectar() as conexao:
        conexao.execute(
            """
            UPDATE apontamentos
            SET hora_fim = ?, status = 'finalizado'
            WHERE status = 'em_andamento'
            """,
            (datetime.now().isoformat(),),
        )