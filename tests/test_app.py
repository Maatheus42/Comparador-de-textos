import io
import unittest

from app import application, normalizar_detalhamento, render_page


class AppTests(unittest.TestCase):
    def _call_app(self, method="GET", path="/", body="", content_length=None):
        captured = {}

        def start_response(status, headers):
            captured["status"] = status
            captured["headers"] = headers

        environ = {
            "REQUEST_METHOD": method,
            "PATH_INFO": path,
            "CONTENT_LENGTH": str(content_length if content_length is not None else len(body)),
            "wsgi.input": io.BytesIO(body.encode("utf-8")),
        }
        response = b"".join(application(environ, start_response)).decode("utf-8", errors="replace")
        return captured["status"], response

    def test_normalizar_detalhamento_fallback(self):
        self.assertEqual(normalizar_detalhamento("invalido"), "completo")

    def test_render_page_nao_quebra_com_detalhamento_invalido(self):
        html = render_page(detalhamento="qqcoisa").decode("utf-8")
        self.assertIn("Comparador de Títulos", html)

    def test_get_root_retorna_200(self):
        status, body = self._call_app(method="GET", path="/")
        self.assertEqual(status, "200 OK")
        self.assertIn("<form method=\"post\">", body)

    def test_get_rota_inexistente_retorna_404(self):
        status, body = self._call_app(method="GET", path="/nao-existe")
        self.assertEqual(status, "404 Not Found")
        self.assertEqual(body, "Not Found")

    def test_method_nao_permitido_retorna_405(self):
        status, body = self._call_app(method="PUT", path="/")
        self.assertEqual(status, "405 Method Not Allowed")
        self.assertEqual(body, "Method Not Allowed")


if __name__ == "__main__":
    unittest.main()
