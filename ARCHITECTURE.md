# Agent-MAC: Self-Programming Agent Architecture

> **Pesquisa:** [OpenClaw](https://github.com/openclaw/openclaw) — um agente AI open-source com 68k stars que usa Gateway + Runtime + Skills system.
> **Este projeto:** vai além, adicionando um **Motor de Meta-Programação** que permite ao agente escrever seus próprios tools.

---

## Visão Geral

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AGENT-MAC                                    │
│                   Self-Programming Agent                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   User Query                                                        │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────┐    context     ┌─────────────────┐                    │
│  │  Memory │──────────────► │  Agent Runtime  │                    │
│  │ (inject │                │  (agentic loop) │                    │
│  │context) │                └────────┬────────┘                    │
│  └─────────┘                         │                             │
│  ┌──────────────────┐         tool_use│                            │
│  │  Episodic Memory │                 ▼                            │
│  │  (past sessions) │        ┌────────────────┐                    │
│  └──────────────────┘        │    Gateway     │                    │
│  ┌──────────────────┐        │ (control plane)│                    │
│  │  Semantic Memory │        └───────┬────────┘                    │
│  │  (facts/prefs)   │                │                             │
│  └──────────────────┘        dispatch│                             │
│                                      ├──────────────────────┐      │
│                                      ▼                      ▼      │
│                             ┌──────────────┐    ┌──────────────┐   │
│                             │ Built-in     │    │  Dynamic     │   │
│                             │ Skills       │    │  Skills      │   │
│                             │ (web_fetch,  │    │ (synthesized │   │
│                             │  memory,     │    │  at runtime) │   │
│                             │  list_tools) │    └──────┬───────┘   │
│                             └──────────────┘           │           │
│                                      │         gap_detected        │
│                                      │                 │           │
│                                      ▼                 ▼           │
│                             ┌────────────────────────────────┐     │
│                             │     META-PROGRAMMING ENGINE    │     │
│                             │                                │     │
│                             │  1. Receive gap description    │     │
│                             │  2. Claude synthesizes Python  │     │
│                             │  3. AST safety check           │     │
│                             │  4. LLM review                 │     │
│                             │  5. Persist to skills/dynamic/ │     │
│                             │  6. Register with Gateway      │     │
│                             │  7. Agent uses new tool NOW    │     │
│                             └────────────┬───────────────────┘     │
│                                          │                         │
│                                   reflect│(after task)             │
│                                          ▼                         │
│                             ┌────────────────────────┐             │
│                             │       Reflector         │            │
│                             │                         │            │
│                             │  - Lessons learned      │            │
│                             │  - Suggested new skills │            │
│                             │  - Effectiveness score  │            │
│                             └────────────┬────────────┘            │
│                                          │                         │
│                                          ▼                         │
│                             ┌────────────────────────┐             │
│                             │    Episodic Memory      │            │
│                             │  (agent's autobiography)│            │
│                             └─────────────────────────┘            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Comparação com OpenClaw

| Feature | OpenClaw | Agent-MAC |
|---|---|---|
| Skills system | Diretórios com `SKILL.md` | Arquivos Python com metadata + handler |
| Auto-discovery | ClawHub registry | SkillsRegistry (3 camadas) |
| Self-programming | Escreve skills via LLM | Meta-Programmer com avaliação multi-camada |
| Segurança | Básica | AST safety scan + LLM review |
| Memória | Sessão + preferências | Episódica (autobiográfica) + Semântica (fatos) |
| Reflexão | Não | Reflector pós-tarefa com sugestões |
| Evolução | Skills adicionadas manualmente | Auto-síntese baseada em gaps detectados |
| Modelo | Agnóstico | Claude Opus 4.6 com adaptive thinking |

---

## O Loop de Auto-Programação

O diferencial chave: o agente pode **escrever seus próprios tools em runtime**:

```
1. Agente recebe task: "calcule a série de Fibonacci"
2. Não existe tool 'fibonacci'
3. Agente chama: request_skill_synthesis("função que calcula Fibonacci até N")
4. MetaProgrammer pede ao Claude que escreva o código Python
5. Código passa por: AST safety scan → Syntax check → LLM review
6. Novo arquivo criado: skills/dynamic/fibonacci.py
7. Tool registrado no Gateway IMEDIATAMENTE
8. Agente usa o novo tool para completar a tarefa
9. Reflector analisa a sessão
10. EpisodicMemory registra o episódio com lessons learned
11. Na próxima sessão: tool 'fibonacci' já está disponível
```

---

## Estrutura de Arquivos

```
agent-mac/
├── main.py                    # Entrypoint (REPL ou query única)
├── agent.py                   # Orquestrador principal
├── pyproject.toml
│
├── core/
│   ├── config.py              # Configuração centralizada
│   ├── gateway.py             # Control plane: registro e dispatch de tools
│   └── runtime.py             # Execution loop: Claude API + tool use
│
├── meta/
│   ├── programmer.py          # ★ Auto-síntese de código Python
│   └── reflector.py           # ★ Reflexão pós-tarefa
│
├── skills/
│   ├── registry.py            # Auto-discovery (builtin → user → dynamic)
│   ├── builtin/               # Tools enviados com o agente
│   │   ├── web_fetch.py
│   │   ├── memory_store.py
│   │   ├── memory_recall.py
│   │   ├── request_skill_synthesis.py  # ★ Gatilho de auto-programação
│   │   └── list_tools.py
│   ├── user/                  # Skills customizadas pelo usuário
│   └── dynamic/               # ★ Skills sintetizadas em runtime (auto-geradas)
│
└── memory/
    ├── episodic.py            # Histórico de sessões (autobiográfica)
    └── semantic.py            # Fatos e preferências persistentes
```

---

## Uso

```bash
# Instalar dependências
pip install -e .

# REPL interativo
python main.py

# Query única
python main.py "Busque o conteúdo de https://example.com e resuma"

# Demo de capacidades
python main.py --demo
```

---

## Fluxo de Síntese de Skills

Quando `request_skill_synthesis` é chamado:

```python
# O agente pede:
{
  "capability": "calcular média, mediana e moda de uma lista de números",
  "examples": ["[1,2,2,3,4] → mean=2.4, median=2, mode=2"]
}

# MetaProgrammer gera:
{
  "name": "statistics_summary",
  "description": "Calculate mean, median, and mode of a number list",
  "parameters": { "numbers": {"type": "array", "items": {"type": "number"}} },
  "code": "async def run(params):\n    import statistics\n    ..."
}

# Após validação → skills/dynamic/statistics_summary.py
# Gateway.register_tool("statistics_summary", handler, schema)
# Agente usa imediatamente: {"numbers": [1, 2, 2, 3, 4]}
```

---

## Segurança da Auto-Programação

O código gerado passa por **3 camadas** antes de ser executado:

1. **AST Safety Scan**: bloqueia `os`, `subprocess`, `sys`, `socket`, `eval`, `exec`
2. **Syntax Validation**: `ast.parse()` garante código Python válido
3. **LLM Review**: Claude Haiku avalia correção e utilidade (rápido e barato)

Apenas código aprovado nas 3 camadas é registrado.
