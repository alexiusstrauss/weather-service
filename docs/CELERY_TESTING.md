# 🚀 Guia de Teste do Celery

Este guia mostra como testar o Celery e a tarefa de limpeza de histórico.

## 📋 **Resumo da Implementação**

### ✅ **Tarefa Implementada:**
- **`cleanup_weather_history_minutely`**: Roda a cada 1 minuto
- **Função**: Mantém apenas os 10 registros mais recentes por cidade
- **Performance**: Usa SQL otimizado para deletar registros antigos

### ✅ **Configuração do Celery Beat:**
```python
'cleanup-weather-history-minutely': {
    'task': 'weather_service.apps.weather.tasks.cleanup_weather_history_minutely',
    'schedule': 60.0,  # Run every 60 seconds (1 minute)
    'options': {'queue': 'default'}
},
```

## 🧪 **Métodos de Teste**

### **1. Teste Local (Desenvolvimento)**

#### Passo 1: Criar dados de teste
```bash
make shell
```

```python
from weather_service.apps.weather.models import WeatherQuery
from django.utils import timezone

# Criar 15 registros para London (deve manter apenas 10)
for i in range(15):
    WeatherQuery.objects.create(
        city='London',
        ip_address='127.0.0.1',
        temperature=20.0 + i,
        description=f'Test weather {i}',
        created_at=timezone.now()
    )

# Verificar dados criados
print(f'London queries: {WeatherQuery.objects.filter(city="London").count()}')
```

#### Passo 2: Testar a tarefa diretamente
```bash
make celery-test-task
```

#### Passo 3: Executar Celery Worker (Terminal 1)
```bash
make celery-worker
```

#### Passo 4: Executar Celery Beat (Terminal 2)
```bash
make celery-beat
```

#### Passo 5: Monitorar logs
```bash
# Ver status do Celery
make celery-status

# Ver logs em tempo real (se usando Docker)
make celery-logs
```

### **2. Teste com Docker (Produção)**

#### Passo 1: Subir todos os serviços
```bash
make docker-up
```

#### Passo 2: Criar dados de teste
```bash
docker-compose -f docker/docker-compose.yml exec api poetry run python manage.py shell -c "
from weather_service.apps.weather.models import WeatherQuery
from django.utils import timezone

# Criar dados de teste
for i in range(20):
    WeatherQuery.objects.create(
        city='TestCity',
        ip_address='127.0.0.1',
        temperature=20.0 + i,
        description=f'Test weather {i}',
        created_at=timezone.now()
    )

print(f'Created {WeatherQuery.objects.filter(city=\"TestCity\").count()} test records')
"
```

#### Passo 3: Monitorar logs do Celery
```bash
# Ver logs do worker
docker-compose -f docker/docker-compose.yml logs -f celery

# Ver logs do beat scheduler
docker-compose -f docker/docker-compose.yml logs -f celery-beat

# Ver ambos
make celery-logs
```

#### Passo 4: Verificar execução da tarefa
```bash
# Aguardar 1 minuto e verificar se os registros foram limpos
docker-compose -f docker/docker-compose.yml exec api poetry run python manage.py shell -c "
from weather_service.apps.weather.models import WeatherQuery
print(f'TestCity queries after cleanup: {WeatherQuery.objects.filter(city=\"TestCity\").count()}')
"
```

### **3. Teste Manual da Tarefa**

#### Executar tarefa imediatamente:
```bash
poetry run python manage.py shell -c "
from weather_service.apps.weather.tasks import cleanup_weather_history_minutely
result = cleanup_weather_history_minutely()
print(f'Result: {result}')
"
```

#### Executar tarefa assíncrona:
```bash
poetry run python manage.py shell -c "
from weather_service.apps.weather.tasks import cleanup_weather_history_minutely
result = cleanup_weather_history_minutely.delay()
print(f'Task ID: {result.id}')
print('Check worker logs for execution')
"
```

## 🔍 **Verificações de Funcionamento**

### **1. Verificar Schedule do Beat**
```bash
docker-compose -f docker/docker-compose.yml logs celery-beat | grep "cleanup-weather-history-minutely"
```

**Saída esperada:**
```
[2025-07-30 23:40:00,123: INFO/MainProcess] Scheduler: Sending due task cleanup-weather-history-minutely
```

### **2. Verificar Execução da Tarefa**
```bash
docker-compose -f docker/docker-compose.yml logs celery | grep "cleanup_weather_history_minutely"
```

**Saída esperada:**
```
[2025-07-30 23:40:00,456: INFO/MainProcess] Task weather_service.apps.weather.tasks.cleanup_weather_history_minutely[abc-123] succeeded in 0.123s: 'Deleted 5 old queries'
```

### **3. Verificar Logs da Aplicação**
```bash
docker-compose -f docker/docker-compose.yml logs celery | grep "Minutely cleanup completed"
```

**Saída esperada:**
```
2025-07-30 23:40:00.789 | INFO | weather_service.apps.weather.tasks:cleanup_weather_history_minutely:51 - Minutely cleanup completed. Total deleted: 5 queries
```

## 🚨 **Troubleshooting**

### **Problema: Celery Worker não conecta**
```bash
# Verificar se Redis está rodando
docker-compose -f docker/docker-compose.yml ps redis

# Verificar logs do Redis
docker-compose -f docker/docker-compose.yml logs redis
```

### **Problema: Tarefa não executa**
```bash
# Verificar se o Beat está rodando
docker-compose -f docker/docker-compose.yml ps celery-beat

# Verificar configuração do schedule
docker-compose -f docker/docker-compose.yml exec celery-beat poetry run python -c "
from weather_service.celery import app
print(app.conf.beat_schedule)
"
```

### **Problema: Banco de dados não acessível**
```bash
# Verificar se PostgreSQL está rodando
docker-compose -f docker/docker-compose.yml ps db

# Testar conexão
docker-compose -f docker/docker-compose.yml exec api poetry run python manage.py dbshell
```

## 📊 **Comandos Úteis do Makefile**

```bash
# Celery Worker
make celery-worker

# Celery Beat Scheduler  
make celery-beat

# Celery Status
make celery-status

# Testar tarefa
make celery-test-task

# Ver logs (Docker)
make celery-logs

# Limpar fila de tarefas
make celery-purge
```

## ✅ **Critérios de Sucesso**

1. **✅ Worker conectado**: `make celery-status` mostra workers online
2. **✅ Beat funcionando**: Logs mostram tarefas sendo agendadas a cada minuto
3. **✅ Tarefa executando**: Logs mostram execução bem-sucedida
4. **✅ Limpeza funcionando**: Registros antigos são removidos, mantendo apenas 10 por cidade
5. **✅ Performance**: Tarefa executa em menos de 1 segundo
6. **✅ Logs claros**: Informações detalhadas sobre quantos registros foram removidos

## 🎯 **Resultado Esperado**

- Tarefa roda automaticamente a cada 1 minuto
- Mantém apenas os 10 registros mais recentes por cidade
- Logs claros e informativos
- Performance otimizada com SQL direto
- Zero downtime na aplicação principal
