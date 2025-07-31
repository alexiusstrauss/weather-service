# 🌤️ Weather Service API

Uma API de clima robusta e escalável construída com Django e Django REST Framework, seguindo princípios de arquitetura limpa.

## 📋 Funcionalidades

- ✅ **Consulta de clima atual** por cidade via OpenWeatherMap API
- ✅ **Cache inteligente** com Redis (10 minutos de TTL)
- ✅ **Histórico de consultas** (últimas 10 por cidade/IP)
- ✅ **Rate limiting** (5 requisições/minuto por IP)
- ✅ **Métricas e monitoramento** com Prometheus e Grafana
- ✅ **Documentação automática** com Swagger/ReDoc
- ✅ **Arquitetura limpa** com separação de responsabilidades
- ✅ **Testes abrangentes** (unitários, integração e BDD)
- ✅ **Docker** para desenvolvimento e produção

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

### Pré-requisitos

- Python 3.11+
- Poetry
- Docker e Docker Compose (opcional)
- Conta na OpenWeatherMap API

### 1. Instalação Local com Poetry

```bash
# Clone o repositório
git clone <repository-url>
cd weather-service

# Crie o ambiente virtual e instale dependências
make create-env

# Copie e configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# Execute as migrações
poetry run python manage.py migrate

# Crie um superusuário (opcional)
poetry run python manage.py createsuperuser

# Execute o servidor de desenvolvimento
make run
```

### 2. Instalação com Docker

```bash
# Clone o repositório
git clone <repository-url>
cd weather-service

# Copie e configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# Execute toda a stack
make run-metrics
```

## 🔧 Comandos do Makefile

| Comando | Descrição |
|---------|-----------|
| `make create-env` | Cria ambiente virtual e instala dependências |
| `make run` | Executa servidor de desenvolvimento |
| `make test` | Executa testes unitários e de integração |
| `make bdd` | Executa testes BDD com behave |
| `make lint` | Executa linting (ruff, pylint) |
| `make format` | Formata código (black, isort) |
| `make monitor` | Inicia stack de monitoramento |
| `make run-metrics` | Inicia stack completa com métricas |
| `make docker-build` | Constrói imagens Docker |
| `make docker-up` | Inicia todos os serviços |
| `make docker-down` | Para todos os serviços |

## 🧪 Executando Testes

### Testes Unitários e de Integração

```bash
# Todos os testes
make test

# Apenas testes unitários
make test-unit

# Apenas testes de integração
make test-integration

# Com relatório de cobertura
make test-coverage
```

### Testes BDD (Behavior Driven Development)

```bash
# Executar testes BDD
make bdd

# Ou diretamente
poetry run python manage.py behave
```

### Estrutura de Testes

- **Unit Tests**: Testam componentes isolados (services, repositories, use cases)
- **Integration Tests**: Testam fluxos completos da API
- **BDD Tests**: Testam cenários de negócio em linguagem natural

## 📊 Monitoramento e Métricas

### Grafana Dashboard

Acesse o dashboard em: http://localhost:3000
- **Usuário**: admin
- **Senha**: admin

### Métricas Disponíveis

- Número de requisições HTTP
- Tempo de resposta das APIs
- Cache hits/misses
- Rate limiting blocks
- Requisições para APIs externas

### Prometheus

Métricas expostas em: http://localhost:9090
- Endpoint de métricas: http://localhost:8000/metrics

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
# Verificar código
make lint

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

## 🚀 Deploy em Produção

### Usando Docker

```bash
# Build das imagens
make docker-build

# Deploy completo
make run-metrics
```

### Configurações de Produção

1. Configure `SECRET_KEY` segura
2. Defina `DEBUG=False`
3. Configure `ALLOWED_HOSTS`
4. Use banco PostgreSQL
5. Configure SSL/HTTPS
6. Configure logs centralizados

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Execute os testes: `make test`
5. Execute o linting: `make lint`
6. Abra um Pull Request

## 📝 Histórias de Usuário

O projeto implementa as seguintes histórias:

1. ✅ **Consultar clima atual** por cidade
2. ✅ **Cache de 10 minutos** para performance
3. ✅ **Histórico das últimas 10 consultas**
4. ✅ **Rate limiting** (5 req/min por IP)
5. ✅ **Estrutura profissional** com arquitetura limpa
6. ✅ **Métricas e observabilidade**
7. ✅ **Docker e orquestração**
8. ✅ **Documentação completa**

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🆘 Suporte

Para dúvidas ou problemas:

1. Verifique a documentação da API em `/api/docs/`
2. Consulte os logs da aplicação
3. Verifique o health check em `/health/`
4. Abra uma issue no repositório

---

**Desenvolvido com ❤️ usando Django, DRF e Clean Architecture**
