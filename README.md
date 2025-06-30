# Task Donegeon

A gamified task management application that turns your daily tasks and chores into a medieval-themed adventure.

## 🏰 Features

- Medieval-themed UI
- First Run Wizard for admin setup
- File upload system with drag-and-drop
- Secure user authentication
- Docker containerization
- Volume persistence for data
- Health monitoring and metrics
- Audit logging

## 🛠️ Technology Stack

- **Backend:** Python/Flask
- **Database:** SQLite (upgradeable to PostgreSQL)
- **Frontend:** Bootstrap with medieval theme
- **Container:** Docker
- **Monitoring:** Built-in health checks and metrics

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Portainer (optional, for container management)

## 🚀 Getting Started

### Environment Setup

1. Generate environment variables:
```bash
python generate_env.py --print-only
```

2. Set up required directories:
```bash
export BASE_PATH=/your/desired/path
./setup_directories.sh
```

### Configuration

Key environment variables:
- `BASE_PATH`: Root path for all data storage
- `SECRET_KEY`: Application secret key (generate using provided script)
- `LOG_LEVEL`: Logging level (default: INFO)
- `MAX_UPLOAD_SIZE`: Maximum upload file size (default: 16MB)

### Docker Deployment

#### Development
```bash
# Build and start
docker compose build
docker compose up -d

# View logs
docker compose logs -f
```

#### Production
```bash
# Build and start
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# Monitor
curl http://localhost:5485/health
curl http://localhost:5485/metrics
```

### Portainer Deployment

1. Create a new stack
2. Set environment variables:
   - `BASE_PATH`: Your data storage path
   - `SECRET_KEY`: Generated secret key
3. Use `docker-compose.prod.yml` as the compose file
4. Deploy the stack

## 📁 Directory Structure

```
BASE_PATH/
├── config/        # Configuration files and logs
├── data/          # Database and application data
└── uploads/       # User uploaded files
```

## 🔍 Monitoring

### Health Check
```bash
curl http://localhost:5485/health
```

### Metrics
```bash
curl http://localhost:5485/metrics
```

Provides:
- System metrics (CPU, memory, disk)
- Application metrics (requests, errors)
- Volume statistics
- Request tracking

## 📝 Logging

- Application logs: `BASE_PATH/config/app.log`
- Audit logs: `BASE_PATH/config/audit.log`
- Docker logs: Available through `docker compose logs`

## 🔒 Security Features

- Non-root container user
- Secret key management
- File upload validation
- Password complexity requirements
- Audit logging
- Volume permissions management

## 🛟 Backup and Restore

Use the provided management script:
```bash
# Create backup
python manage.py backup

# List backups
python manage.py list_backups

# Restore from backup
python manage.py restore <backup_name>
```

## 🔧 Maintenance

### Volume Management
```bash
# Check volume status
curl http://localhost:5485/health

# View volume metrics
curl http://localhost:5485/metrics
```

### Container Management
```bash
# Restart container
docker compose -f docker-compose.prod.yml restart

# View logs
docker compose -f docker-compose.prod.yml logs -f
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **ModuleNotFoundError**
   ```bash
   docker compose down
   docker compose -f docker-compose.prod.yml build --no-cache
   docker compose -f docker-compose.prod.yml up -d
   ```

2. **Permission Issues**
   ```bash
   # Check directory permissions
   ./setup_directories.sh
   ```

3. **Container Won't Start**
   ```bash
   # Check logs
   docker compose -f docker-compose.prod.yml logs
   ```

### Getting Help

- Check the logs: `docker compose logs`
- Check the health endpoint: `/health`
- Check the metrics endpoint: `/metrics`
- Verify environment variables are set correctly
- Ensure all volumes are properly mounted 