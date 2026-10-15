from datetime import timedelta


def parse_tempo(texto: str) -> timedelta:
    """
    Converte um texto no formato HH:MM:SS para timedelta.
    """

    partes = texto.strip().split(":")

    if len(partes) != 3:
        raise ValueError(
            f"Formato de tempo inválido: {texto}. Use HH:MM:SS."
        )

    horas, minutos, segundos = (int(parte) for parte in partes)

    return timedelta(
        hours=horas,
        minutes=minutos,
        seconds=segundos,
    )


def para_minutos(tempo: timedelta) -> float:
    return tempo.total_seconds() / 60


def para_horas(tempo: timedelta) -> float:
    return tempo.total_seconds() / 3600