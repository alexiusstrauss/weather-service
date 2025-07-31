# 🧩 Histórias de Usuário e Tarefas

Este documento descreve as histórias e tarefas do projeto **API de Clima**, estruturadas no padrão INVEST (Independente, Negociável, Valiosa, Estimável, Pequena, Testável).

---

## História 1: Consultar clima atual por cidade

**Como** usuário da API, **quero** informar uma cidade e obter o clima atual, **para** tomar decisões baseadas no tempo.

### Tarefas:
- Criar endpoint `GET /weather?city=`
- Integrar com a API OpenWeatherMap
- Retornar dados estruturados (cidade, temperatura, descrição)
- Criar camada de service e usecase
- Testes unitários e de integração

---

## História 2: Aplicar cache de 10 minutos

**Como** desenvolvedor, **quero** cachear as consultas por cidade, **para** reduzir chamadas externas e ganhar performance.

### Tarefas:
- Configurar Redis
- Implementar cache por cidade com timeout de 600s
- Testar fluxo de cache hit e miss
- Adicionar métricas de hit/miss

---

## História 3: Manter histórico das últimas 10 consultas

**Como** mantenedor, **quero** registrar até 10 últimas buscas, **para** gerar histórico útil de uso.

### Tarefas:
- Criar model `WeatherQuery`
- Salvar dados após consulta (cidade, temp, descrição)
- Limitar por cidade/IP a 10 registros (usecase ou celery)
- Endpoint `/weather/history/` (opcional)
- Testes

---

## História 4: Bloquear excesso de requisições por IP (rate limit)

**Como** mantenedor, **quero** limitar a 5 requisições/minuto por IP, **para** evitar abusos.

### Tarefas:
- Criar middleware de rate limit com Redis
- Retornar HTTP 429 em excesso
- Adicionar métrica `rate_limit_blocked`
- Testar com múltiplas chamadas

---

## História 5: Estrutura de projeto profissional

**Como** desenvolvedor, **quero** uma estrutura clara e escalável, **para** facilitar evolução, testes e leitura.

### Tarefas:
- Criar camadas: `views`, `usecases`, `services`, `repositories`
- Separar testes: `unit/`, `usecases/`, `integration/`, `features/`
- Configurar `pyenv`, `poetry`, `Makefile`
- Criar `.editorconfig`, linters e formatter

---

## História 6: Métricas e observabilidade

**Como** mantenedor, **quero** monitorar uso da API, **para** identificar comportamento e problemas em produção.

### Tarefas:
- Adicionar `django-prometheus`
- Expor `/metrics`
- Criar métricas: requisições, tempo, cache, erros
- Subir Prometheus e Grafana com painel automático
- Criar simulação de carga (script ou endpoint)

---

## História 7: Docker e orquestração da stack

**Como** desenvolvedor, **quero** rodar toda a aplicação com um comando, **para** facilitar o setup local.

### Tarefas:
- Criar `Dockerfile` com Poetry
- Criar `docker-compose.yml` com:
  - web, redis, redis-commander, celery, db, prometheus, grafana
- Mapear `.env`
- Comando `make run-metrics` para subir tudo

---

## História 8: Documentação e entrega clara

**Como** revisor, **quero** entender o projeto com facilidade, **para** testar e avaliar rapidamente.

### Tarefas:
- Criar `README.md` com:
  - Visão geral
  - Setup com Docker e local
  - Execução de testes
  - Comandos úteis
  - Link para Grafana
- Documentar APIs com `drf-spectacular` (`/docs/`)

---
