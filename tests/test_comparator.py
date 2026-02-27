import unittest

from comparator import comparar_titulos, normalizar_texto_para_comparacao


class ComparatorTests(unittest.TestCase):
    def test_normalizacao_remove_acentos_espacos_e_simbolos(self):
        self.assertEqual(normalizar_texto_para_comparacao("Título: Ação 2024!"), "tituloacao2024")

    def test_comparacao_igual_depois_normalizacao(self):
        r = comparar_titulos("Teste de Título", "teste    de titulo", "completo")
        self.assertTrue(r["iguais"])

    def test_comparacao_diferente_com_primeira_diferenca(self):
        r = comparar_titulos("Projeto X", "Projeto Y", "primeira_diferenca")
        self.assertFalse(r["iguais"])
        self.assertIsNotNone(r["primeira_diferenca"])


if __name__ == "__main__":
    unittest.main()
