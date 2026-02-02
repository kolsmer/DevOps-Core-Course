# Stage 1: Build stage
FROM golang:1.23-alpine AS builder

# Install build dependencies
RUN apk add --no-cache git ca-certificates tzdata

# Set working directory
WORKDIR /build

# Copy go.mod and go.sum first for dependency caching
COPY go.mod ./

# Download dependencies
RUN go mod download

# Copy source code
COPY main.go .

# Build the application
# CGO_ENABLED=0 for static binary (no C dependencies)
# -ldflags="-w -s" strips debug info and symbol table (smaller binary)
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -ldflags="-w -s" \
    -o app \
    main.go

# Stage 2: Runtime stage
FROM alpine:3.19

# Install CA certificates for HTTPS
RUN apk --no-cache add ca-certificates

# Create non-root user
RUN adduser -D -u 1000 appuser

WORKDIR /app

# Copy binary from builder stage
COPY --from=builder /build/app .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1

# Run the application
CMD ["./app"]
