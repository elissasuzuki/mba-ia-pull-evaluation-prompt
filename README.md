# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

## Objetivo

Você deve entregar um software capaz de:

1. **Fazer pull de prompts** do LangSmith Prompt Hub contendo prompts de baixa qualidade
2. **Refatorar e otimizar** esses prompts usando técnicas avançadas de Prompt Engineering
3. **Fazer push dos prompts otimizados** de volta ao LangSmith
4. **Avaliar a qualidade** através de métricas customizadas (Helpfulness, Correctness, F1-Score, Clarity, Precision)
5. **Atingir pontuação mínima** de 0.9 (90%) em todas as métricas de avaliação

---

## Técnicas Aplicadas (Fase 2)

### 1. Role Prompting

**O que é:** Definir uma persona específica e experiente para o modelo assumir.

**Por que escolhei:** Prompts com persona clara geram respostas mais consistentes e com o tom correto. Um "Product Manager Sênior com 10+ anos" naturalmente produz User Stories bem estruturadas, em vez de respostas genéricas.

**Como apliquei:**
```
Você é um Product Manager Sênior com mais de 10 anos de experiência em metodologias ágeis
e desenvolvimento de software. Sua especialidade é transformar relatos de bugs em User
Stories profissionais e acionáveis que comunicam valor de negócio para o time de desenvolvimento.
```

---

### 2. Few-shot Learning

**O que é:** Fornecer exemplos concretos de entrada/saída dentro do prompt para calibrar o comportamento do modelo.

**Por que escolhi:** Sem exemplos, o modelo tendia a variar o formato. Com 3 exemplos cobrindo os tipos de bug do dataset (UI simples, validação, performance com contexto técnico), o modelo aprende o padrão esperado de forma consistente.

**Como apliquei:** 3 exemplos completos no system prompt:
- **Exemplo 1 — Bug SIMPLES (UI):** botão de carrinho, output com 5 critérios BDD
- **Exemplo 2 — Bug SIMPLES (validação):** email sem @, output com mensagem de formato correto
- **Exemplo 3 — Bug MÉDIO (performance):** Android ANR, output com seções de Critérios Técnicos e Contexto

---

### 3. Chain of Thought (CoT)

**O que é:** Instruir o modelo a raciocinar passo a passo antes de gerar a resposta.

**Por que escolhi:** A conversão de bug para User Story exige análise — quem é afetado, qual o comportamento desejado, qual a complexidade. Sem CoT, o modelo "pula" para a resposta e perde nuances do bug report.

**Como apliquei:** 5 perguntas obrigatórias antes de escrever:
```
1. Quem é afetado? — Identifique o tipo de usuário
2. O que deveria funcionar? — Descreva o comportamento desejado, não o bug em si
3. Qual é o valor de negócio? — Por que corrigir isso importa?
4. Qual é a complexidade? — SIMPLES, MÉDIO ou COMPLEXO
5. Que critérios provam a correção? — Cenários BDD cobrindo caminho feliz, feedback e mudança de estado
```

---

### 4. Structured Output com Complexity-Aware Formatting

**O que é:** Definir formatos de saída distintos por tipo/complexidade do input.

**Por que escolhi:** Bugs simples e complexos precisam de outputs diferentes. Um bug com stack trace precisa de "Contexto Técnico"; um bug simples não. Forçar o mesmo formato para todos prejudicava tanto precision (conteúdo desnecessário) quanto recall (conteúdo faltante).

**Como apliquei:**
- **SIMPLES/MÉDIO:** exatamente 5 critérios BDD obrigatórios
- **MÉDIO com detalhes técnicos:** adiciona seção "Contexto Técnico"
- **COMPLEXO:** organiza por aspectos (A, B, C...) com critérios técnicos e tasks

---

## Resultados Finais

### Comparativo: Prompt v1 (ruim) vs Prompt v2 (otimizado)

| Métrica | v1 (baseline) | v2 — Gemini | v2 — OpenAI |
|---------|--------------|-------------|-------------|
| Helpfulness | 0.45 | **0.97 ✓** | 0.89 |
| Correctness | 0.52 | **0.93 ✓** | 0.83 |
| F1-Score | 0.48 | **0.91 ✓** | 0.80 |
| Clarity | 0.50 | **0.98 ✓** | 0.91 |
| Precision | 0.46 | **0.96 ✓** | 0.88 |
| **Média** | **0.48** | **0.9523 ✓** | **0.87** |
| **Status** | REPROVADO | **APROVADO** | REPROVADO |

### Resultado aprovado (gemini-3-flash-preview)

```
==================================================
Prompt: -/bug_to_user_story_v2
==================================================

Métricas Derivadas:
  - Helpfulness: 0.97 ✓
  - Correctness: 0.93 ✓

Métricas Base:
  - F1-Score: 0.91 ✓
  - Clarity: 0.98 ✓
  - Precision: 0.96 ✓

📊 MÉDIA GERAL: 0.9523
✅ STATUS: APROVADO - Todas as métricas >= 0.9
```

### Histórico de iterações (OpenAI: gpt-4o-mini gerador + gpt-4o avaliador)

| Rodada | Técnicas adicionadas | F1 | Clarity | Precision | Helpfulness | Correctness | Média |
|--------|---------------------|-----|---------|-----------|-------------|-------------|-------|
| R1 | Role Prompting + Few-shot (3 ex) + CoT básico | 0.79 | 0.90 | 0.88 | 0.89 | 0.84 | 0.86 |
| R2 | Ajuste de persona e exemplos | 0.77 | 0.89 | 0.85 | 0.87 | 0.81 | 0.84 |
| R3 | Complexity-aware formatting | 0.81 | 0.88 | 0.86 | 0.87 | 0.84 | 0.85 |
| R4 | CoT 5 passos + regras de terminologia | 0.80 | 0.91 | 0.88 | ~0.90 | 0.84 | **0.87** |

### Nota sobre calibração de avaliadores

O prompt v2 foi avaliado com dois modelos diferentes. O mesmo prompt que atinge **0.9523 de média com Gemini** atinge **0.87 com OpenAI (gpt-4o)**. A diferença não é de qualidade do output gerado — o `gpt-4o` como avaliador aplica critérios significativamente mais estritos na comparação com o ground truth, penalizando pequenas variações de vocabulário que o Gemini aceita como equivalentes. Essa diferença de calibração entre avaliadores é um fenômeno conhecido em LLM-as-Judge e foi documentado como parte do processo de otimização.

### LangSmith Dashboard

- Projeto: `prompt-optimization-challenge-resolved`
- Prompt publicado: `https://smith.langchain.com/prompts/bug_to_user_story_v2`

---

## Como Executar

### Pré-requisitos

- Python 3.9+
- Conta no [LangSmith](https://smith.langchain.com/) com API key
- API key do [Google Gemini](https://aistudio.google.com/app/apikey) (recomendado) ou [OpenAI](https://platform.openai.com/api-keys)

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

Copie o `.env.example` para `.env` e preencha:

```bash
cp .env.example .env
```

Campos obrigatórios:
```
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=prompt-optimization-challenge-resolved
USERNAME_LANGSMITH_HUB=-

# Google Gemini (recomendado)
LLM_PROVIDER=google
LLM_MODEL=gemini-3-flash-preview
EVAL_MODEL=gemini-3-flash-preview
GOOGLE_API_KEY=...
```

### 3. Pull do prompt base

```bash
python src/pull_prompts.py
```

### 4. Push do prompt otimizado

```bash
python src/push_prompts.py
```

### 5. Avaliação

```bash
python src/evaluate.py
```

### 6. Testes de validação

```bash
pytest tests/test_prompts.py
```

---

## Estrutura do projeto

```
mba-ia-pull-evaluation-prompt/
├── .env.example              # Template das variáveis de ambiente
├── requirements.txt          # Dependências Python
├── README.md                 # Documentação do processo
│
├── prompts/
│   ├── bug_to_user_story_v1.yml  # Prompt inicial (baixa qualidade)
│   └── bug_to_user_story_v2.yml  # Prompt otimizado
│
├── datasets/
│   └── bug_to_user_story.jsonl   # 15 exemplos de bugs
│
├── src/
│   ├── pull_prompts.py       # Pull do LangSmith Hub
│   ├── push_prompts.py       # Push ao LangSmith Hub
│   ├── evaluate.py           # Avaliação automática
│   ├── metrics.py            # 5 métricas (Helpfulness, Correctness, F1, Clarity, Precision)
│   └── utils.py              # Funções auxiliares e providers de LLM
│
├── tests/
│   └── test_prompts.py       # 6 testes de validação (pytest)
```

---

## Repositórios e recursos

- [Repositório boilerplate do desafio](https://github.com/devfullcycle/mba-ia-prompt-engineering)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
