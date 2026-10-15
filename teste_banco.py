from src.banco import (
    criar_tabelas,
    iniciar_apontamento,
    finalizar_apontamento,
    buscar_apontamento_aberto,
    listar_apontamentos_em_andamento,
    listar_historico,
)

criar_tabelas()

id_apontamento = iniciar_apontamento(
    posto="Posto 03",
    operador="Aluno Teste",
    unidade="UND-TESTE-001",
    tempo_ciclo_esperado_min=81.95,
)

print("Apontamento iniciado, id:", id_apontamento)


print("Em andamento agora:")
for linha in listar_apontamentos_em_andamento():
    print(dict(linha))


finalizar_apontamento(id_apontamento)

print("Histórico após finalizar:", listar_historico())