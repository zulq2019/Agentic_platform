FROM python:3.12-slim

RUN groupadd --gid 1000 aep && useradd --uid 1000 --gid aep --create-home aep

WORKDIR /app
COPY src/shared/aep_common /tmp/aep-common
RUN pip install --no-cache-dir "/tmp/aep-common[health]" "fastapi>=0.110.0" "uvicorn[standard]>=0.27.0"

COPY src/platform/services/config-service/src /app/src
ENV PYTHONPATH=/app/src
ENV PORT=8015

USER aep
EXPOSE 8015
HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8015/health/live')" || exit 1
CMD ["uvicorn", "config_service.main:app", "--host", "0.0.0.0", "--port", "8015"]
