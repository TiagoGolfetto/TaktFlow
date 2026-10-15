from src.calculations import carregar_cenario, analisar_cenario

cenario = carregar_cenario("dia")
resultado = analisar_cenario(cenario)

print("Gargalo linha:", resultado["linha"]["gargalo"]["posto"])
print("Gargalo pré:", resultado["pre_montagem"]["gargalo"]["posto"])