# Comparador de Títulos (App Web)

App web local para comparar títulos de diferentes plataformas (ex.: sistema x PDF), ignorando acentos, pontuação e espaços extras.

## Funcionalidades

- Normalização robusta de texto para comparação.
- Três níveis de detalhamento:
  - **Simples**
  - **Primeira diferença**
  - **Completo** (diferenças por palavra)
- Proteções de robustez no app:
  - fallback para detalhamento inválido
  - rota inexistente retorna `404`
  - método HTTP inválido retorna `405`

## Como executar

```bash
python app.py
```

Depois, abra: `http://localhost:8000`

## Rodar testes

```bash
python -m unittest discover -s tests -v
```
