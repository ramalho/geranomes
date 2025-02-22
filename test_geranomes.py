from geranomes import extrair_juniores


def test_extrair_juniores():
    with open("amostras/convocacao_fuvest.txt") as f:
        nomes = f.readlines()
    juniores = sorted(extrair_juniores(nomes))
    assert len(juniores) == 28
    assert juniores[:3] == ["Alexandre", "Andre", "Antonio"]
    assert juniores[-3:] == ["Robinson", "Sergio", "Vagner"]
