FROM python:3.12-slim AS builder

WORKDIR /build
COPY src/shared/aep_common /build/aep-common
RUN pip install --no-cache-dir --prefix=/install \
    "/build/aep-common[health]" "fastapi>=0.110.0" "uvicorn[standard]>=0.27.0"

FROM python:3.12-slim AS runtime

RUN groupadd --gid 1000 aep && useradd --uid 1000 --gid aep --create-home aep

WORKDIR /app
COPY --from=builder /install /usr/local
COPY src/platform/orchestrator/src /app/src
ENV PYTHONPATH=/app/src
ENV PORT=8003

USER aep
EXPOSE 8003
HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8003/health/live')" || exit 1
CMD ["uvicorn", "orchestrator_service.main:app", "--host", "0.0.0.0", "--port", "8003"]
