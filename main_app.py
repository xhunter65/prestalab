import hashlib
import json
import logging
import os
from datetime import datetime, timezone

import boto3
import psycopg2
from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("prestalab")

AWS_REGION = os.getenv("AWS_REGION", "mx-central-1")
SECRET_NAME = os.getenv("SECRET_NAME", "prestalab/prod/rds-credentials")

app = FastAPI(title="PrestaLab API", version="2.0.0")

secrets_client = boto3.client("secretsmanager", region_name=AWS_REGION)
STARTUP_SECRET_VERSION: str | None = None


def fetch_rds_credentials() -> dict:
    """Obtiene en tiempo de ejecucion las credenciales de RDS desde AWS Secrets Manager."""
    try:
        response = secrets_client.get_secret_value(SecretId=SECRET_NAME)
    except ClientError as exc:
        logger.error("Error obteniendo secreto de Secrets Manager: %s", exc.response["Error"]["Code"])
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo leer el secreto en Secrets Manager: {exc.response['Error']['Code']}",
        ) from exc

    secret_data = json.loads(response["SecretString"])
    password = secret_data.get("password", "")
    fingerprint = hashlib.sha256(password.encode("utf-8")).hexdigest()[:12]

    return {
        "host": secret_data["host"],
        "port": int(secret_data.get("port", 5432)),
        "dbname": secret_data.get("dbname", "prestalab_db"),
        "username": secret_data["username"],
        "password": password,
        "version_id": response.get("VersionId"),
        "password_sha256_prefix": fingerprint,
    }


def check_postgres_tls(creds: dict) -> dict:
    """Verifica conectividad TLS (sslmode=require) contra RDS PostgreSQL usando credenciales de Secrets Manager."""
    conn = None
    try:
        conn = psycopg2.connect(
            host=creds["host"],
            port=creds["port"],
            dbname=creds["dbname"],
            user=creds["username"],
            password=creds["password"],
            sslmode="require",
            connect_timeout=3,
        )
        with conn.cursor() as cur:
            cur.execute("SELECT version(), ssl_is_used();")
            pg_version, ssl_used = cur.fetchone()
        return {
            "status": "connected",
            "tls_mode": "require",
            "ssl_active": bool(ssl_used),
            "engine_version": pg_version,
        }
    except Exception as exc:
        return {
            "status": "unreachable",
            "tls_mode": "require",
            "detail": type(exc).__name__,
        }
    finally:
        if conn is not None:
            conn.close()


@app.on_event("startup")
def on_startup() -> None:
    global STARTUP_SECRET_VERSION
    try:
        creds = fetch_rds_credentials()
        STARTUP_SECRET_VERSION = creds["version_id"]
        logger.info("Secreto cargado al iniciar. VersionId=%s", STARTUP_SECRET_VERSION)
    except Exception as exc:
        logger.warning("No se pudo precargar el secreto al iniciar: %s", exc)


def build_status_payload() -> dict:
    creds = fetch_rds_credentials()
    db_check = check_postgres_tls(creds)
    return {
        "status": "ok",
        "service": "Presta-Lab API",
        "credentials_source": "AWS Secrets Manager (runtime via boto3)",
        "secret_name": SECRET_NAME,
        "aws_region": AWS_REGION,
        "startup_secret_version_id": STARTUP_SECRET_VERSION,
        "current_secret_version_id": creds["version_id"],
        "rotated_since_startup": (
            STARTUP_SECRET_VERSION is not None and creds["version_id"] != STARTUP_SECRET_VERSION
        ),
        "password_sha256_prefix": creds["password_sha256_prefix"],
        "env_has_db_password": "DB_PASSWORD" in os.environ,
        "database": {
            "host": creds["host"],
            "port": creds["port"],
            "dbname": creds["dbname"],
            "user": creds["username"],
            **db_check,
        },
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/")
def read_root():
    return build_status_payload()


@app.get("/api/health")
def health_check():
    return build_status_payload()
