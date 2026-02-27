# Comparador de Títulos (App Web)

Transformei seu script em um app web simples (sem dependências externas), com foco em uso prático no trabalho.

## Funcionalidades

- Normaliza e compara títulos ignorando acentos, pontuação e espaços extras.
- Três níveis de detalhamento:
  - **Simples**
  - **Primeira diferença**
  - **Completo** (diferenças por palavra)
- Interface web local para colar os dois títulos e comparar com um clique.

## Como executar

```bash
python app.py
```

Depois, abra: `http://localhost:8000`

## Rodar testes

```bash
python -m unittest discover -s tests -v
```
