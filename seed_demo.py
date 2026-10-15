from datetime import datetime, timedelta

from src.banco import criar_tabelas, conectar

criar_tabelas()

agora = datetime.now()

registros_em_andamento = [
    # posto, operador, unidade, segundos_atras, tempo_esperado_min
    ("Posto 01", "Aluno A", "UND-001", 10, 0.25),
    ("Posto 03", "Aluno B", "UND-002", 25, 0.33),
    ("Posto 05", "Aluno C", "UND-003", 8, 0.23),
]

with conectar() as conexao:
    for posto, operador, unidade, segundos_atras, tempo_esperado in registros_em_andamento:
        inicio = agora - timedelta(seconds=segundos_atras)
        conexao.execute(
            """
            INSERT INTO apontamentos
                (posto, operador, unidade, hora_inicio, tempo_ciclo_esperado_min, status)
            VALUES (?, ?, ?, ?, ?, 'em_andamento')
            """,
            (posto, operador, unidade, inicio.isoformat(), tempo_esperado),
        )

    for i in range(5):
        inicio = agora - timedelta(minutes=3 + i)
        fim = inicio + timedelta(seconds=18)
        conexao.execute(
            """
            INSERT INTO apontamentos
                (posto, operador, unidade, hora_inicio, hora_fim, tempo_ciclo_esperado_min, status)
            VALUES (?, ?, ?, ?, ?, ?, 'finalizado')
            """,
            ("Posto 02", "Turno Demo", f"UND-{100+i}", inicio.isoformat(), fim.isoformat(), 0.25),
        )

print("Banco de demonstração pré-carregado com sucesso.")