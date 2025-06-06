# MCPizza Production Deployment Guide

## 🚀 Production Server Features

The production server (`mcpizza/production_server.py`) includes:

- ✅ **Real Domino's API Integration** - Uses actual pizzapi for live data
- ✅ **Fallback System** - Falls back to mock data if API fails
- ✅ **Environment Configuration** - Easy enable/disable via env vars
- ✅ **Error Handling** - Graceful error handling with detailed logging
- ✅ **Source Tracking** - Tells you if data came from real API or mock

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCPIZZA_REAL_API` | `false` | Set to `true` to enable real Domino's API calls |
| `MCPIZZA_FALLBACK_MOCK` | `true` | Fall back to mock data if real API fails |

### Enable Real API Mode

```bash
# Enable real API calls
export MCPIZZA_REAL_API=true
export MCPIZZA_FALLBACK_MOCK=true

# Run the production server
python mcpizza/production_server.py
```

## 🧪 Testing

### Test with Mock Data (Safe)
```bash
# Test with mock data
python test_production.py --zip 95608

# Expected output:
# 🟡 MOCK mode - uses demo data
```

### Test with Real API (Live Calls)
```bash
# Test with real Domino's API 
python test_production.py --real-api --zip 95608

# ⚠️ This makes actual API calls to Domino's!
```

### mcptools Testing
```bash
# Mock mode
mcp tools python mcpizza/production_server.py

# Real API mode
MCPIZZA_REAL_API=true mcp tools python mcpizza/production_server.py

# Test store lookup with real API
MCPIZZA_REAL_API=true mcp call find_dominos_store --params '{"address":"95608"}' python mcpizza/production_server.py
```

## 📦 Deployment Options

### Option 1: Local Development
```bash
# Clone and setup
git clone <your-repo>
cd MCPIZZA
source .venv/bin/activate

# Mock mode (safe)
python mcpizza/production_server.py

# Real API mode 
MCPIZZA_REAL_API=true python mcpizza/production_server.py
```

### Option 2: Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install pizzapi requests pydantic

# Set environment variables
ENV MCPIZZA_REAL_API=true
ENV MCPIZZA_FALLBACK_MOCK=true

CMD ["python", "mcpizza/production_server.py"]
```

### Option 3: Systemd Service
```ini
[Unit]
Description=MCPizza MCP Server
After=network.target

[Service]
Type=simple
User=mcpizza
WorkingDirectory=/opt/mcpizza
Environment=MCPIZZA_REAL_API=true
Environment=MCPIZZA_FALLBACK_MOCK=true
ExecStart=/usr/bin/python3 mcpizza/production_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🔒 Security Considerations

### Real API Usage
- Real API calls hit Domino's servers directly
- No authentication required for store lookup/menu browsing
- Order placement would require customer data validation
- Rate limiting may apply from Domino's side

### Fallback Safety
- Always enable `MCPIZZA_FALLBACK_MOCK=true` for production
- Server will use mock data if real API fails
- Prevents service interruption due to API issues

## 📊 Monitoring

### Log Messages
```bash
# Real API mode
INFO - 🔴 REAL API MODE ENABLED - Will make actual Domino's API calls
INFO - 🔍 Finding real store near: 95608
INFO - ✅ Found real store: 4521

# Mock mode
INFO - 🟡 MOCK MODE - Using demo data

# Fallback mode
WARNING - No real store found, falling back to mock data
ERROR - Real API failed: connection timeout
```

### Response Source Tracking
All responses include a `source` field:
- `"source": "real_api"` - Data from actual Domino's API
- `"source": "mock"` - Demo/mock data
- `"source": "fallback_mock"` - Real API failed, using mock

## 🎯 Production Checklist

- [ ] Install dependencies: `pizzapi`, `requests`, `pydantic`
- [ ] Test with mock mode first
- [ ] Test with real API mode
- [ ] Configure environment variables
- [ ] Set up logging/monitoring
- [ ] Test fallback behavior
- [ ] Deploy with process manager (systemd, docker, etc.)

## 🚨 Important Notes

### Real API Limitations
- The pizzapi library may have stability issues
- Some menu items cause "PRODUCT NOT FOUND" errors
- Store availability varies by location
- No order placement safety controls (use with caution)

### Recommended Configuration
```bash
# Production settings
export MCPIZZA_REAL_API=true      # Enable real API
export MCPIZZA_FALLBACK_MOCK=true # Enable safety fallback
```

This ensures real data when possible, with graceful fallback to mock data if needed.
