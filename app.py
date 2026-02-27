from html import escape
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from comparator import comparar_titulos

DETALHAMENTOS_VALIDOS = {"simples", "primeira_diferenca", "completo"}


def normalizar_detalhamento(valor: str) -> str:
    return valor if valor in DETALHAMENTOS_VALIDOS else "completo"


def render_page(
    titulo_sistema: str = "",
    titulo_pdf: str = "",
    detalhamento: str = "completo",
    resultado: dict | None = None,
) -> bytes:
    detalhamento = normalizar_detalhamento(detalhamento)
    options = {opcao: "selected" if opcao == detalhamento else "" for opcao in DETALHAMENTOS_VALIDOS}

    resultado_html = ""
    if resultado is not None:
        status = (
            '<p style="color:#0a7a30;font-weight:bold;">✅ STATUS: Títulos iguais após normalização.</p>'
            if resultado["iguais"]
            else '<p style="color:#b24a00;font-weight:bold;">⚠️ STATUS: Títulos diferentes.</p>'
        )

        primeira = ""
        if resultado.get("primeira_diferenca"):
            p = resultado["primeira_diferenca"]
            primeira = f"""
            <h3>Primeira diferença</h3>
            <p>Índice: {p['indice']}</p>
            <p><strong>Sistema:</strong> <code>{escape(p['contexto_sistema'])}</code></p>
            <p><strong>PDF:</strong> <code>{escape(p['contexto_pdf'])}</code></p>
            """

        diffs = ""
        if resultado.get("diferencas"):
            items = []
            for d in resultado["diferencas"]:
                pos_sistema = f" (posições {d.pos_sistema[0]}-{d.pos_sistema[1]})" if d.pos_sistema else ""
                pos_pdf = f" (posições {d.pos_pdf[0]}-{d.pos_pdf[1]})" if d.pos_pdf else ""
                sistema_txt = ", ".join(d.sistema) if d.sistema else "[vazio]"
                pdf_txt = ", ".join(d.pdf) if d.pdf else "[vazio]"
                items.append(
                    f"<li><strong>{escape(d.tipo)}</strong><br/>"
                    f"Sistema{escape(pos_sistema)}: {escape(sistema_txt)}<br/>"
                    f"PDF{escape(pos_pdf)}: {escape(pdf_txt)}</li>"
                )
            diffs = f"<h3>Divergências por palavra</h3><ul>{''.join(items)}</ul>"

        resultado_html = f"""
        <div class="card">
            {status}
            <h3>Versão compactada para comparação</h3>
            <p><strong>Sistema:</strong> <code>{escape(resultado['sistema_compactado'])}</code></p>
            <p><strong>PDF:</strong> <code>{escape(resultado['pdf_compactado'])}</code></p>
            {primeira}
            {diffs}
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>Comparador de Títulos</title>
      <style>
        body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; }}
        textarea {{ width: 100%; min-height: 90px; margin-bottom: 1rem; }}
        .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 1rem; margin-top: 1rem; }}
        code {{ background: #f5f5f5; padding: 0.2rem 0.4rem; border-radius: 4px; display:block; }}
      </style>
    </head>
    <body>
      <h1>Comparador de Títulos</h1>
      <p>Compare títulos do sistema e do PDF ignorando acentos, pontuação e espaços extras.</p>

      <form method="post">
        <label for="titulo_sistema">Título do Sistema</label>
        <textarea id="titulo_sistema" name="titulo_sistema" required>{escape(titulo_sistema)}</textarea>

        <label for="titulo_pdf">Título do PDF</label>
        <textarea id="titulo_pdf" name="titulo_pdf" required>{escape(titulo_pdf)}</textarea>

        <label for="detalhamento">Nível de detalhamento</label>
        <select id="detalhamento" name="detalhamento">
          <option value="simples" {options['simples']}>Simples</option>
          <option value="primeira_diferenca" {options['primeira_diferenca']}>Primeira diferença</option>
          <option value="completo" {options['completo']}>Completo</option>
        </select>

        <div style="margin-top: 1rem"><button type="submit">Comparar</button></div>
      </form>
      {resultado_html}
    </body>
    </html>
    """
    return html.encode("utf-8")


def _ler_body(environ: dict) -> str:
    try:
        size = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        size = 0
    return environ["wsgi.input"].read(size).decode("utf-8", errors="replace")


def application(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET")
    path = environ.get("PATH_INFO", "/")

    if path != "/":
        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"Not Found"]

    if method == "POST":
        body = _ler_body(environ)
        form = parse_qs(body)

        titulo_sistema = form.get("titulo_sistema", [""])[0]
        titulo_pdf = form.get("titulo_pdf", [""])[0]
        detalhamento = normalizar_detalhamento(form.get("detalhamento", ["completo"])[0])

        resultado = comparar_titulos(titulo_sistema, titulo_pdf, detalhamento)
        payload = render_page(titulo_sistema, titulo_pdf, detalhamento, resultado)
        start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
        return [payload]

    if method == "GET":
        payload = render_page()
        start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
        return [payload]

    start_response("405 Method Not Allowed", [("Content-Type", "text/plain; charset=utf-8")])
    return [b"Method Not Allowed"]


if __name__ == "__main__":
    with make_server("0.0.0.0", 8000, application) as httpd:
        print("Servidor rodando em http://localhost:8000")
        httpd.serve_forever()
