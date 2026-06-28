FROM golang:1.22-alpine AS builder

WORKDIR /build
COPY src/platform/gateway/go.mod src/platform/gateway/go.sum* ./
RUN go mod download 2>/dev/null || true
COPY src/platform/gateway/ ./
RUN go mod tidy && CGO_ENABLED=0 go build -o /gateway .

FROM alpine:3.19
RUN addgroup -g 1000 aep && adduser -u 1000 -G aep -D aep
WORKDIR /app
COPY --from=builder /gateway /app/gateway
USER aep
EXPOSE 8080
ENV PORT=8080
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
    CMD wget -qO- http://127.0.0.1:8080/health/live || exit 1
CMD ["/app/gateway"]
