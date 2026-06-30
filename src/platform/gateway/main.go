package main

import (
	"context"
	"fmt"
	"net"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

type config struct {
	ServiceName     string
	ServiceVersion  string
	ContractVersion string
	Environment     string
	Port            string
	PostgresHost    string
	KafkaHost       string
	RedisHost       string
}

func loadConfig() config {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	return config{
		ServiceName:     envOr("SERVICE_NAME", "api-gateway"),
		ServiceVersion:  envOr("SERVICE_VERSION", "0.1.0"),
		ContractVersion: envOr("CONTRACT_VERSION", "1.0.0"),
		Environment:     envOr("ENVIRONMENT", "dev"),
		Port:            port,
		PostgresHost:    envOr("POSTGRES_HOST", "postgres:5432"),
		KafkaHost:       envOr("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
		RedisHost:       envOr("REDIS_HOST", "redis:6379"),
	}
}

func envOr(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

var (
	httpRequestsTotal = prometheus.NewCounterVec(
		prometheus.CounterOpts{Name: "aep_http_requests_total", Help: "Total HTTP requests"},
		[]string{"service", "method", "status"},
	)
	httpRequestDuration = prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "aep_http_request_duration_seconds",
			Help:    "HTTP request duration in seconds",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"service", "method"},
	)
)

func init() {
	prometheus.MustRegister(httpRequestsTotal, httpRequestDuration)
}

func main() {
	cfg := loadConfig()
	e := echo.New()
	e.HideBanner = true
	e.Use(middleware.Recover())
	e.Use(metricsMiddleware(cfg.ServiceName))

	e.GET("/health/live", func(c echo.Context) error {
		return c.JSON(http.StatusOK, map[string]string{"status": "ok"})
	})

	e.GET("/health/ready", func(c echo.Context) error {
		checks := map[string]string{
			"database": tcpCheck(c.Request().Context(), cfg.PostgresHost),
			"kafka":    tcpCheck(c.Request().Context(), cfg.KafkaHost),
			"redis":    tcpCheck(c.Request().Context(), cfg.RedisHost),
		}
		allOK := true
		for _, v := range checks {
			if v != "ok" {
				allOK = false
				break
			}
		}
		body := map[string]any{"status": "ok", "checks": checks}
		if !allOK {
			body["status"] = "degraded"
			return c.JSON(http.StatusServiceUnavailable, body)
		}
		return c.JSON(http.StatusOK, body)
	})

	e.GET("/metrics", echo.WrapHandler(promhttp.Handler()))
	e.GET("/info", func(c echo.Context) error {
		return c.JSON(http.StatusOK, map[string]string{
			"service":          cfg.ServiceName,
			"version":          cfg.ServiceVersion,
			"contract_version": cfg.ContractVersion,
			"environment":      cfg.Environment,
		})
	})

	e.Logger.Fatal(e.Start(":" + cfg.Port))
}

func metricsMiddleware(serviceName string) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			start := time.Now()
			err := next(c)
			status := fmt.Sprintf("%d", c.Response().Status)
			httpRequestsTotal.WithLabelValues(serviceName, c.Request().Method, status).Inc()
			httpRequestDuration.WithLabelValues(serviceName, c.Request().Method).Observe(time.Since(start).Seconds())
			return err
		}
	}
}

func tcpCheck(ctx context.Context, address string) string {
	host := normalizeAddress(address)
	if host == "" {
		return "error"
	}
	dialer := net.Dialer{Timeout: 2 * time.Second}
	conn, err := dialer.DialContext(ctx, "tcp", host)
	if err != nil {
		return "error"
	}
	_ = conn.Close()
	return "ok"
}

func normalizeAddress(raw string) string {
	raw = strings.TrimPrefix(raw, "redis://")
	raw = strings.TrimPrefix(raw, "postgresql://")
	if idx := strings.Index(raw, "@"); idx >= 0 {
		raw = raw[idx+1:]
	}
	if idx := strings.Index(raw, "/"); idx >= 0 {
		raw = raw[:idx]
	}
	if !strings.Contains(raw, ":") {
		return ""
	}
	return raw
}
