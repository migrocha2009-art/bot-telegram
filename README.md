# Bot do Telegram com IA

Bot de conversa para o Telegram usando inteligência artificial via OpenRouter, com busca na web pelo Tavily.

## Funcionalidades

- Responde mensagens usando IA (modelo configurável via OpenRouter)
- Busca automática na web para perguntas sobre notícias, preços, clima, etc.
- Histórico de conversa por usuário
- Indicador de "digitando" enquanto processa
- Respostas longas divididas automaticamente em partes

## Requisitos

- Python 3.10+
- Conta no [Telegram](https://telegram.org) com um bot criado via [@BotFather](https://t.me/BotFather)
- Chave de API na [OpenRouter](https://openrouter.ai)
- Chave de API no [Tavily](https://tavily.com)

## Instalação

```bash
# Instalar dependências
pip install -r requirements.txt
```

## Configuração

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```
TELEGRAM_TOKEN=seu_token_aqui
OPENROUTER_API_KEY=sua_chave_aqui
TAVILY_API_KEY=sua_chave_aqui
```

## Como rodar

```bash
# Rodar localmente
python telegram_bot.py

# Rodar em background (servidor)
nohup python3 telegram_bot.py &
```

## Trocar o modelo de IA

No arquivo `telegram_bot.py`, altere a linha:

```python
MODEL = "openai/gpt-oss-120b:free"
```

Você pode usar qualquer modelo disponível em [openrouter.ai/models](https://openrouter.ai/models).
