# Environment Configuration Guide

## Overview

The app uses environment-specific configuration files to manage different deployment environments:
- **Development**: Local testing with localhost backend
- **Staging**: Pre-production testing environment
- **Production**: Live production environment

## Environment Files

### `.env` (Default - Development)
```dotenv
API_BASE_URL=http://localhost:8000/api/v1
ENVIRONMENT=development
```

### `.env.dev` (Development)
```dotenv
API_BASE_URL=http://localhost:8000/api/v1
ENVIRONMENT=development
```

### `.env.staging` (Staging - Create this)
```dotenv
API_BASE_URL=https://staging-api.jobsearch.com/api/v1
ENVIRONMENT=staging
```

### `.env.prod` (Production)
```dotenv
API_BASE_URL=https://api.jobsearch.com/api/v1
ENVIRONMENT=production
```

## Usage

### During Development

1. **Default (uses `.env`):**
   ```bash
   flutter run
   ```

2. **Specific environment:**
   ```bash
   # Copy environment file
   Copy-Item .env.dev .env
   flutter run
   ```

### Building for Production

1. **Update `.env.prod` with your production API URL**
2. **Copy to `.env` before building:**
   ```powershell
   Copy-Item .env.prod .env
   ```
3. **Build release:**
   ```bash
   flutter build appbundle --release
   ```

## Automated Environment Switching

Use the provided scripts:

### PowerShell (Windows)
```powershell
.\set_environment.ps1 -Environment production
flutter build appbundle --release
```

### Bash (Linux/Mac)
```bash
./set_environment.sh production
flutter build appbundle --release
```

## Configuration Variables

### Current Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `API_BASE_URL` | Backend API base URL | `https://api.jobsearch.com/api/v1` |
| `ENVIRONMENT` | Current environment name | `production` |

### Adding New Variables

1. **Add to environment files:**
   ```dotenv
   # .env.prod
   API_BASE_URL=https://api.jobsearch.com/api/v1
   ENVIRONMENT=production
   API_TIMEOUT=30000
   ENABLE_ANALYTICS=true
   ```

2. **Update `EnvironmentConfig` class:**
   ```dart
   // lib/core/config/environment_config.dart
   class EnvironmentConfig {
     static String get apiBaseUrl => 
       dotenv.env['API_BASE_URL'] ?? 'http://localhost:8000/api/v1';
     
     static String get environment => 
       dotenv.env['ENVIRONMENT'] ?? 'development';
     
     // Add new config
     static int get apiTimeout => 
       int.parse(dotenv.env['API_TIMEOUT'] ?? '30000');
     
     static bool get enableAnalytics => 
       dotenv.env['ENABLE_ANALYTICS'] == 'true';
   }
   ```

## Security Best Practices

### ⚠️ NEVER commit sensitive data to `.env` files!

For sensitive configuration (API keys, secrets):

1. **Use environment-specific files**
2. **Add to `.gitignore`:**
   ```gitignore
   .env.local
   .env.*.local
   ```
3. **Use secure storage for secrets**
4. **Use CI/CD secret management** for automated builds

### Example with Secrets

Create `.env.prod.local` (not committed):
```dotenv
API_BASE_URL=https://api.jobsearch.com/api/v1
API_KEY=your_secret_api_key_here
SENTRY_DSN=https://your-sentry-dsn
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Flutter
        uses: subosito/flutter-action@v2
        
      - name: Create .env file
        run: |
          echo "API_BASE_URL=${{ secrets.PROD_API_URL }}" > .env
          echo "ENVIRONMENT=production" >> .env
          
      - name: Build
        run: flutter build appbundle --release
```

## Testing Different Environments

### Local Backend (Development)
```bash
API_BASE_URL=http://localhost:8000/api/v1
```

### Network Testing (Development)
Use your machine's IP address:
```bash
# Find your IP: ipconfig (Windows) or ifconfig (Linux/Mac)
API_BASE_URL=http://192.168.1.100:8000/api/v1
```

### Staging Environment
```bash
API_BASE_URL=https://staging-api.jobsearch.com/api/v1
```

### Production Environment
```bash
API_BASE_URL=https://api.jobsearch.com/api/v1
```

## Troubleshooting

### Issue: Changes not reflected
**Solution:** 
1. Stop the app
2. Run `flutter clean`
3. Copy correct .env file
4. Run `flutter pub get`
5. Restart app

### Issue: API not connecting
**Solution:**
1. Verify `API_BASE_URL` is correct
2. Check network connectivity
3. Verify backend is running
4. Check for CORS issues (web)
5. Test API with curl/Postman

### Issue: Wrong environment loaded
**Solution:**
1. Check which `.env` file is being used
2. Verify variable names match exactly
3. Check `EnvironmentConfig` implementation
4. Add debug logging:
   ```dart
   print('Environment: ${EnvironmentConfig.environment}');
   print('API URL: ${EnvironmentConfig.apiBaseUrl}');
   ```

## Environment Checklist

Before deploying to production:

- [ ] `.env.prod` configured with production API URL
- [ ] All API endpoints tested in staging
- [ ] Firebase configured for production project
- [ ] Analytics configured (if used)
- [ ] Error tracking configured (Sentry, etc.)
- [ ] SSL/TLS enabled on backend
- [ ] Rate limiting configured
- [ ] Authentication working correctly
- [ ] All environment variables validated

## Multi-Flavor Setup (Advanced)

For complex apps, consider using Flutter build flavors:

```bash
flutter build appbundle --release --flavor production --dart-define=ENV=prod
```

This requires additional configuration in `build.gradle.kts` and allows multiple app variants installed simultaneously.

## Resources

- [Flutter Environment Variables](https://docs.flutter.dev/deployment/flavors)
- [flutter_dotenv Package](https://pub.dev/packages/flutter_dotenv)
- [12 Factor App Config](https://12factor.net/config)
