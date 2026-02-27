import difflib
import re
import unicodedata
from dataclasses import dataclass
from typing import Any


@dataclass
class DiffItem:
    tipo: str
    sistema: list[str]
    pdf: list[str]
    pos_sistema: tuple[int, int] | None = None
    pos_pdf: tuple[int, int] | None = None


def normalizar_texto_para_comparacao(texto: str) -> str:
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode("utf-8")
    texto = re.sub(r"[^a-z0-9]", "", texto)
    return texto


def normalizar_texto_para_exibicao_com_espacos(texto: str) -> str:
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode("utf-8")
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def primeira_diferenca(titulo_sistema: str, titulo_pdf: str) -> dict[str, Any] | None:
    s_comp = normalizar_texto_para_comparacao(titulo_sistema)
    p_comp = normalizar_texto_para_comparacao(titulo_pdf)

    min_len = min(len(s_comp), len(p_comp))
    idx = -1
    for i in range(min_len):
        if s_comp[i] != p_comp[i]:
            idx = i
            break

    if idx == -1 and len(s_comp) != len(p_comp):
        idx = min_len

    if idx == -1:
        return None

    contexto_antes = 15
    contexto_depois = 15
    ini = max(0, idx - contexto_antes)
    fim_s = min(len(s_comp), idx + contexto_depois)
    fim_p = min(len(p_comp), idx + contexto_depois)

    return {
        "indice": idx,
        "char_sistema": s_comp[idx] if idx < len(s_comp) else "",
        "char_pdf": p_comp[idx] if idx < len(p_comp) else "",
        "contexto_sistema": f"...{s_comp[ini:idx]}[{s_comp[idx] if idx < len(s_comp) else ''}]{s_comp[idx+1:fim_s]}...",
        "contexto_pdf": f"...{p_comp[ini:idx]}[{p_comp[idx] if idx < len(p_comp) else ''}]{p_comp[idx+1:fim_p]}...",
    }


def diferencas_por_palavra(titulo_sistema: str, titulo_pdf: str) -> list[DiffItem]:
    sistema_exib = normalizar_texto_para_exibicao_com_espacos(titulo_sistema)
    pdf_exib = normalizar_texto_para_exibicao_com_espacos(titulo_pdf)

    palavras_sistema = sistema_exib.split(" ") if sistema_exib else []
    palavras_pdf = pdf_exib.split(" ") if pdf_exib else []

    matcher = difflib.SequenceMatcher(None, palavras_sistema, palavras_pdf)
    itens: list[DiffItem] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue

        tipo_map = {
            "replace": "substituicao",
            "delete": "remocao_no_pdf",
            "insert": "adicao_no_pdf",
        }
        itens.append(
            DiffItem(
                tipo=tipo_map[tag],
                sistema=palavras_sistema[i1:i2],
                pdf=palavras_pdf[j1:j2],
                pos_sistema=(i1 + 1, i2) if i1 != i2 else None,
                pos_pdf=(j1 + 1, j2) if j1 != j2 else None,
            )
        )

    return itens


def comparar_titulos(titulo_sistema: str, titulo_pdf: str, detalhamento: str = "completo") -> dict[str, Any]:
    sistema_comp = normalizar_texto_para_comparacao(titulo_sistema)
    pdf_comp = normalizar_texto_para_comparacao(titulo_pdf)
    iguais = sistema_comp == pdf_comp

    resultado: dict[str, Any] = {
        "iguais": iguais,
        "sistema_compactado": sistema_comp,
        "pdf_compactado": pdf_comp,
        "detalhamento": detalhamento,
        "primeira_diferenca": None,
        "diferencas": [],
    }

    if iguais or detalhamento == "simples":
        return resultado

    if detalhamento in ["primeira_diferenca", "completo"]:
        resultado["primeira_diferenca"] = primeira_diferenca(titulo_sistema, titulo_pdf)

    if detalhamento == "completo":
        resultado["diferencas"] = diferencas_por_palavra(titulo_sistema, titulo_pdf)

    return resultado
