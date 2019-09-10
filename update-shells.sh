#!/bin/bash
GOOS=windows go build -o payloads/reverse.go-windows -ldflags="-s -w" shells/reverse.go
GOOS=linux go build -o payloads/reverse.go-linux -ldflags="-s -w" shells/reverse.go
GOOS=darwin go build -o payloads/reverse.go-darwin -ldflags="-s -w" shells/reverse.go
