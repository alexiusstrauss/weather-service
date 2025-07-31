# 🌤️ Weather Service API

<div align="center">

**Uma API de clima robusta e escalável construída com Django e Django REST Framework**

*Seguindo princípios de Clean Architecture e boas práticas de desenvolvimento*

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://djangoproject.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Tests](https://img.shields.io/badge/Tests-67%25_Coverage-green.svg)](#-testes)

</div>

---

## ✨ Funcionalidades

🌍 **Consulta de clima atual** por cidade via OpenWeatherMap API  
⚡ **Cache inteligente** com Redis (10 minutos de TTL)  
📊 **Histórico de consultas** (últimas 10 por cidade)  
🛡️ **Rate limiting** (5 requisições/minuto por IP)  
📈 **Métricas e monitoramento** com Prometheus e Grafana  
📚 **Documentação automática** com Swagger/ReDoc  
🏗️ **Arquitetura limpa** com separação de responsabilidades  
🧪 **Testes abrangentes** (unitários, integração e BDD)  
🐳 **Docker** para desenvolvimento e produção

## 🏗️ Arquitetura

O projeto segue os princípios de **Clean Architecture**:

```
weather_service/
├── apps/
│   ├── core/           # Funcionalidades centrais
│   │   ├── middleware.py   # Rate limiting
│   │   └── views.py        # Health check
│   └── weather/        # Domínio do clima
│       ├── models.py       # Entidades
│       ├── repositories.py # Acesso a dados
│       ├── services.py     # Integrações externas
│       ├── usecases.py     # Regras de negócio
│       ├── views.py        # Apresentação
│       └── tasks.py        # Tarefas assíncronas
├── settings/           # Configurações por ambiente
├── tests/             # Testes organizados
│   ├── unit/          # Testes unitários
│   ├── integration/   # Testes de integração
│   └── features/      # Testes BDD
└── docker/           # Configurações Docker
```

## 🚀 Instalação e Configuração

### 📋 Pré-requisitos

- **Python 3.12+** (recomendamos usar [pyenv](https://github.com/pyenv/pyenv))
- **Poetry** para gerenciamento de dependências
- **Docker e Docker Compose** (para execução completa)
- **Conta na OpenWeatherMap API** (opcional - usa mock por padrão)

### 🔧 Configuração Local (Desenvolvimento)

```bash
# Clone o repositório
git clone <repository-url>
cd weather-service

# Crie o ambiente virtual e instale dependências
make create-env

# Configure variáveis de ambiente (opcional)
cp .env.example .env
# Edite o arquivo .env com suas configurações

# Execute migrações e inicie o servidor
poetry run python manage.py migrate
poetry run python manage.py runserver
```

### 🐳 Execução Completa (Docker)

```bash
# Clone o repositório
git clone <repository-url>
cd weather-service

# Execute toda a stack (PostgreSQL, Redis, API, Celery, Grafana, Prometheus)
make run
```

> **💡 Recomendação:** Use `make create-env` para desenvolvimento local ou `make run` para execução completa com Docker.

## 🔧 Comandos Disponíveis

| Comando | Descrição |
|---------|----------|
| `make help` | Mostra todos os comandos disponíveis |
| `make create-env` | Cria ambiente virtual com Python e instala dependências |
| `make build` | Constrói imagens Docker |
| `make devstack` | Inicia stack de desenvolvimento (PostgreSQL, Redis, Grafana, Prometheus) |
| `make run-dev` | Executa API localmente (sem Celery) |
| `make run-worker` | Executa Celery worker e beat scheduler |
| `make run` | **Executa stack completa** (devstack + API + Celery) |
| `make test` | Executa testes unitários |
| `make test-bdd` | Executa testes BDD apenas |
| `make test-bdd-quiet` | Executa testes BDD com saída mínima |
| `make test-bdd-verbose` | Executa testes BDD com nomes dos cenários |
| `make test-all` | **Executa todos os testes** (unitários + integração + BDD) |
| `make format` | Formata código (black, isort, ruff) |
| `make stop` | Para todos os serviços |
| `make clean` | Limpa arquivos temporários e cache |

## 🧪 Testes

### 📈 Cobertura de Testes

- **40 testes unitários/integração** ✅
- **7 cenários BDD** ✅  
- **Cobertura total: 72%** ✅

### 🚀 Executando Testes

```bash
# Todos os testes (unitários + integração + BDD)
make test-all

# Apenas testes unitários
make test

# Apenas testes BDD
make test-bdd

# Testes BDD com saída detalhada
make test-bdd-verbose

# Testes BDD com saída mínima
make test-bdd-quiet
```

### 📋 Estrutura de Testes

- **🧪 Unit Tests**: Testam componentes isolados (services, repositories, use cases)
- **🔗 Integration Tests**: Testam fluxos completos da API
- **🎭 BDD Tests**: Testam cenários de negócio em linguagem natural

### 📊 Cenários BDD Implementados

1. ✅ Consulta de clima para cidade válida
2. ✅ Consulta de clima para cidade inválida  
3. ✅ Requisição sem parâmetro de cidade
4. ✅ Dados de clima em cache
5. ✅ Histórico de consultas salvo
6. ✅ Rate limiting bloqueia requisições excessivas
7. ✅ Invalidação de cache funciona

## 📈 Monitoramento e Métricas

### 📉 Painel do Grafana

**Acesse o dashboard completo em:** http://localhost:3000  
- **Usuário**: `admin`
- **Senha**: `admin`

📈 **Visualizações disponíveis:**
- Gráficos de requisições por endpoint
- Métricas de performance e latencia
- Monitoramento de cache hits/misses
- Análise de rate limiting
- Status dos serviços em tempo real

### 📁 Métricas Coletadas

- 🚀 **Número de requisições HTTP** por endpoint
- ⏱️ **Tempo de resposta** das APIs
- 💾 **Cache hits/misses** do Redis
- 🛡️ **Rate limiting blocks** por IP
- 🌍 **Requisições para APIs externas** (OpenWeatherMap)
- 📊 **Métricas de sistema** (CPU, memória, disco)

### 🔍 Prometheus

**Métricas expostas em:** http://localhost:9090  
**Endpoint de métricas:** http://localhost:8000/metrics

## 🔗 Endpoints da API

### Documentação Interativa

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Schema JSON**: http://localhost:8000/api/schema/

### Principais Endpoints

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/v1/weather/` | GET | Consulta clima atual |
| `/api/v1/weather/history/` | GET | Histórico de consultas |
| `/api/v1/weather/cache/` | DELETE | Invalidar cache (admin) |
| `/health/` | GET | Health check |
| `/metrics` | GET | Métricas Prometheus |

### Exemplos de Uso

```bash
# Consultar clima
curl "http://localhost:8000/api/v1/weather/?city=São Paulo"

# Histórico de consultas
curl "http://localhost:8000/api/v1/weather/history/?city=São Paulo&limit=5"

# Health check
curl "http://localhost:8000/health/"
```

## 🐳 Serviços Docker

A stack completa inclui:

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| **web** | 8000 | API Django |
| **db** | 5432 | PostgreSQL |
| **redis** | 6379 | Cache e broker |
| **redis-commander** | 8081 | Interface Redis |
| **celery** | - | Worker assíncrono |
| **celery-beat** | - | Scheduler |
| **prometheus** | 9090 | Coleta de métricas |
| **grafana** | 3000 | Dashboard de métricas |

## ⚙️ Configuração

### Variáveis de Ambiente Principais

```bash
# API Key da OpenWeatherMap (obrigatória)
OPENWEATHER_API_KEY=your_api_key_here

# Configurações de rate limiting
RATE_LIMIT_REQUESTS=5
RATE_LIMIT_WINDOW=60

# URLs de conexão
DATABASE_URL=postgresql://user:pass@localhost:5432/weather_service
REDIS_URL=redis://localhost:6379/0
```

### Configurações por Ambiente

- **Development**: `weather_service.settings.development`
- **Testing**: `weather_service.settings.test`
- **Production**: `weather_service.settings.production`

## 🔄 Tarefas Assíncronas (Celery)

O projeto inclui tarefas Celery para:

- Limpeza automática de consultas antigas
- Limpeza de cache expirado
- Geração de métricas periódicas

```bash
# Executar worker
poetry run celery -A weather_service worker -l info

# Executar scheduler
poetry run celery -A weather_service beat -l info
```

## 🧹 Qualidade de Código

### Linting e Formatação

```bash
# Formatar código
make format
```

### Ferramentas Utilizadas

- **Black**: Formatação de código
- **isort**: Organização de imports
- **Ruff**: Linting rápido
- **Pylint**: Análise estática avançada

## 📈 Performance e Cache

### Estratégia de Cache

- **TTL**: 10 minutos (600 segundos)
- **Chave**: `weather_cache:{cidade}`
- **Fallback**: Cache em banco de dados
- **Invalidação**: Manual via API

### Rate Limiting

- **Limite**: 5 requisições por minuto por IP
- **Implementação**: Middleware customizado
- **Storage**: Redis
- **Exceções**: Health check e métricas

## 📁 Organização do Projeto

```
weather-service/
├── weather_service/          # Código principal da aplicação
│   ├── apps/                # Apps Django
│   │   ├── core/           # App core (middleware, health checks)
│   │   └── weather/        # App weather (models, views, services)
│   └── settings/           # Configurações por ambiente
├── tests/                   # Testes organizados por tipo
│   ├── unit/               # Testes unitários
│   ├── integration/        # Testes de integração
│   └── features/           # Testes BDD (Behave)
├── docker/                  # Configurações Docker
├── docs/                    # Documentação adicional
└── static/                  # Arquivos estáticos
```

### 🏗️ Arquitetura Clean Code

- **📊 Models**: Entidades de domínio (Django ORM)
- **🔄 Repositories**: Camada de acesso a dados
- **⚙️ Services**: Lógica de integração externa
- **🎯 Use Cases**: Regras de negócio
- **🌐 Views**: Camada de apresentação (API)
- **🧪 Tests**: Testes isolados e independentes

## 🚀 Deploy em Produção

### Usando Docker

```bash
# Build das imagens
make build

# Deploy completo
make run
```

## 🖼️ Capturas de Tela

### 📚 Documentação da API (Swagger)
![Swagger UI](docs/evidencias/swagger.png)
*Interface interativa da API com todos os endpoints documentados*

### 🧪 Execução dos Testes
![Testes Unitários](docs/evidencias/Make%20test.png)
*Execução dos 40 testes unitários e de integração com 72% de cobertura*

![Testes BDD](docs/evidencias/Make%20BDD.png)
*Execução dos 7 cenários BDD com 100% de sucesso*

![Cenários BDD](docs/evidencias/Cenarios%20BDD.png)
*Detalhamento dos cenários BDD implementados*

### 📊 Monitoramento e Métricas
![Dashboard Grafana](docs/evidencias/Dashboard%20Grafana.png)
*Painel principal do Grafana com métricas de performance*

![Gráfico por Cidade](docs/evidencias/Grafico%20Request%20by%20City.png)
*Métricas detalhadas de requisições por cidade*

### 🔧 Comandos e Deploy
![Make Help](docs/evidencias/Make%20help.png)
*Lista completa de comandos disponíveis no Makefile*

![Make Run](docs/evidencias/make-run.png)
*Deploy completo da stack com Docker Compose*

## 📝 Histórias de Usuário Implementadas

✅ **US1:** Consultar clima atual por cidade  
✅ **US2:** Cache inteligente de 10 minutos para performance  
✅ **US3:** Histórico das últimas 10 consultas por cidade  
✅ **US4:** Rate limiting (5 requisições/minuto por IP)  
✅ **US5:** Estrutura profissional com Clean Architecture  
✅ **US6:** Métricas e observabilidade com Grafana/Prometheus  
✅ **US7:** Docker e orquestração de serviços  
✅ **US8:** Documentação completa e testes abrangentes

## 📞 Endpoints Principais

| Endpoint | Método | Descrição |
|----------|---------|------------|
| `/api/v1/weather/` | GET | Consulta clima por cidade |
| `/api/v1/weather/history/` | GET | Histórico de consultas |
| `/api/v1/weather/cache/` | DELETE | Invalida cache (admin) |
| `/health/` | GET | Health check dos serviços |
| `/api/docs/` | GET | Documentação Swagger |
| `/metrics` | GET | Métricas Prometheus |

## 🆘 Suporte e Troubleshooting

📆 **Documentação da API:** http://localhost:8000/api/docs/  
🔍 **Health Check:** http://localhost:8000/health/  
📈 **Métricas:** http://localhost:8000/metrics  
📉 **Grafana:** http://localhost:3000 (admin/admin)

---

<div align="center">

## 📄 Licença

**Distribuído sob termos não comerciais** com base na GNU GPL  
*Uso exclusivo para testes técnicos e estudos*

Consulte o arquivo [LICENSE](./LICENSE) para detalhes completos

---

**Desenvolvido com ❤️ usando Django, Clean Architecture e boas práticas**

*Weather Service API - 2025*

</div>
