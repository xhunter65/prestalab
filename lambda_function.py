import json
import os
import datetime

def lambda_handler(event, context):
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    response_body = {
        "timestamp": now,
        "region": os.environ.get("AWS_REGION", "us-east-2"),
        "funcion": context.function_name,
        "version": context.function_version,
        "memoria_asignada_mb": context.memory_limit_in_mb,
        "tiempo_restante_ms": context.get_remaining_time_in_millis(),
        "request_id": context.aws_request_id,
        "proyecto": "PrestaLab - Equipo Noble",
        "mensaje": "Reporte generado exitosamente",
        "generado_por": "Lambda - Practica 09"
    }
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(response_body, indent=2)
    }
