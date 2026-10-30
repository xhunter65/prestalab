# Práctica 09 - Serverless API | PrestaLab

## Materia
Cómputo en la Nube | Grupo 503 | Equipo Noble

## Descripción
Función AWS Lambda en Python 3.13 que genera reportes sintéticos
de forma serverless, expuesta mediante API Gateway.

## Configuración Lambda
- **Runtime:** Python 3.13
- **Memoria:** 128 MB
- **Timeout:** 10 segundos
- **Región:** us-east-2 (Ohio)

## Métricas de Cold Start
| Métrica | Cold Start | Warm Start |
|---|---|---|
| Init Duration | 105.50 ms | No aplica |
| Duration | 3.88 ms | 1.72 ms |
| Billed Duration | 110 ms | 2 ms |
| Max Memory Used | 34 MB | 34 MB |

## Endpoint Público
- **API Gateway:** HTTP API
- **Método:** GET
- **URL:** (agregar URL del endpoint aquí)
