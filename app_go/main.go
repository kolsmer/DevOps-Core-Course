package main

import (
	"encoding/json"
	"log"
	"net"
	"net/http"
	"os"
	"runtime"
	"strconv"
	"strings"
	"time"
)

var startTime = time.Now().UTC()

// writeJSON writes JSON response with status code.
func writeJSON(w http.ResponseWriter, status int, payload interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(payload); err != nil {
		log.Printf("failed to write response: %v", err)
	}
}

func uptime() (int64, string) {
	delta := time.Since(startTime)
	seconds := int64(delta.Seconds())
	hours := seconds / 3600
	minutes := (seconds % 3600) / 60
	human := pluralize(hours, "hour") + ", " + pluralize(minutes, "minute")
	return seconds, human
}

func pluralize(value int64, word string) string {
	if value == 1 {
		return "1 " + word
	}
	return fmtInt(value) + " " + word + "s"
}

func fmtInt(value int64) string {
	return strconv.FormatInt(value, 10)
}

func platformVersion() string {
	data, err := os.ReadFile("/etc/os-release")
	if err == nil {
		lines := strings.Split(string(data), "\n")
		for _, line := range lines {
			if strings.HasPrefix(line, "PRETTY_NAME=") {
				return strings.Trim(line[len("PRETTY_NAME="):], "\"")
			}
		}
	}
	return runtime.GOOS + " kernel " + runtime.Version()
}

func clientIP(r *http.Request) string {
	if xff := r.Header.Get("X-Forwarded-For"); xff != "" {
		parts := strings.Split(xff, ",")
		if ip := strings.TrimSpace(parts[0]); ip != "" {
			return ip
		}
	}
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		return r.RemoteAddr
	}
	return host
}

func mainHandler(w http.ResponseWriter, r *http.Request) {
	uptimeSeconds, uptimeHuman := uptime()

	resp := map[string]interface{}{
		"service": map[string]interface{}{
			"name":        "devops-info-service",
			"version":     "1.0.0",
			"description": "DevOps course info service",
			"framework":   "Go net/http",
		},
		"system": map[string]interface{}{
			"hostname":         hostname(),
			"platform":         runtime.GOOS,
			"platform_version": platformVersion(),
			"architecture":     runtime.GOARCH,
			"cpu_count":        runtime.NumCPU(),
			"python_version":   "n/a", // Not applicable in Go build
		},
		"runtime": map[string]interface{}{
			"uptime_seconds": uptimeSeconds,
			"uptime_human":   uptimeHuman,
			"current_time":   time.Now().UTC().Format(time.RFC3339Nano) + "Z",
			"timezone":       "UTC",
		},
		"request": map[string]interface{}{
			"client_ip":  clientIP(r),
			"user_agent": r.UserAgent(),
			"method":     r.Method,
			"path":       r.URL.Path,
		},
		"endpoints": []map[string]string{
			{"path": "/", "method": "GET", "description": "Service information"},
			{"path": "/health", "method": "GET", "description": "Health check"},
		},
	}

	writeJSON(w, http.StatusOK, resp)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	uptimeSeconds, _ := uptime()
	resp := map[string]interface{}{
		"status":         "healthy",
		"timestamp":      time.Now().UTC().Format(time.RFC3339Nano) + "Z",
		"uptime_seconds": uptimeSeconds,
	}
	writeJSON(w, http.StatusOK, resp)
}

func notFoundHandler(w http.ResponseWriter, r *http.Request) {
	resp := map[string]interface{}{
		"error":   "Not Found",
		"message": "Endpoint does not exist",
		"path":    r.URL.Path,
	}
	writeJSON(w, http.StatusNotFound, resp)
}

func hostname() string {
	h, err := os.Hostname()
	if err != nil {
		return "unknown"
	}
	return h
}

func main() {
	host := os.Getenv("HOST")
	if host == "" {
		host = "0.0.0.0"
	}
	port := os.Getenv("PORT")
	if port == "" {
		port = "8000"
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/" {
			mainHandler(w, r)
			return
		}
		notFoundHandler(w, r)
	})
	mux.HandleFunc("/health", healthHandler)

	addr := net.JoinHostPort(host, port)
	log.Printf("Starting Go service on %s", addr)
	if err := http.ListenAndServe(addr, mux); err != nil {
		log.Fatalf("server error: %v", err)
	}
}
