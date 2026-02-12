# HardCard Integration Guide - Notification System & CI/CD

## Overview

This guide explains how to configure and use the notification system and CI/CD pipeline for the HardCard Continuous Improvement System.

## Table of Contents

1. [Notification System Setup](#notification-system-setup)
2. [CI/CD Pipeline Configuration](#cicd-pipeline-configuration)
3. [Integration with Improvement System](#integration-with-improvement-system)
4. [Troubleshooting](#troubleshooting)
5. [Architecture Overview](#architecture-overview)

## Notification System Setup

### Prerequisites

- Python 3.11 or higher
- Access to Slack workspace (for webhooks)
- Email account with SMTP access

### Configuration Steps

1. **Create Environment Variables**
   
   Copy the configuration template:
   ```bash
   cp notification-config.json.template notification-config.json
   ```

2. **Configure Slack Webhook**
   
   - Go to your Slack workspace settings
   - Create an incoming webhook for the desired channel
   - Add the webhook URL to `notification-config.json`:
   ```json
   {
     "slack": {
       "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
     }
   }
   ```

3. **Configure Email Settings**
   
   Update the email configuration in `notification-config.json`:
   ```json
   {
     "email": {
       "smtp_server": "smtp.gmail.com",
       "smtp_port": 587,
       "sender": "your-email@gmail.com",
       "password": "your-app-password",
       "recipients": ["recipient1@example.com", "recipient2@example.com"]
     }
   }
   ```

4. **Set Notification Preferences**
   
   Customize notification behavior:
   ```json
   {
     "notification_settings": {
       "daily_summary_hour": 9,
       "min_notification_interval": 3600,
       "enable_slack": true,
       "enable_email": true,
       "critical_alerts_only": false
     }
   }
   ```

### Alert Thresholds

The notification system uses the following thresholds:

| Level | Metric | Threshold | Action |
|-------|--------|-----------|--------|
| Critical | Code Completion | < 50% | Immediate Slack alert |
| Critical | Test Coverage | < 60% | Immediate Slack alert |
| Critical | Security Score | < 85% | Immediate Slack alert |
| Critical | Agent Errors | > 3 | Immediate Slack alert |
| Critical | Deployment Blockers | Any | Immediate Slack alert |
| Warning | Code Completion | < 70% | Batched notification |
| Warning | Test Coverage | < 75% | Batched notification |
| Warning | Security Score | < 90% | Batched notification |
| Warning | Execution Time | > 300s | Batched notification |

## CI/CD Pipeline Configuration

### GitHub Actions Setup

1. **Add Secrets to Repository**
   
   Go to Settings → Secrets and variables → Actions, and add:
   - `SLACK_WEBHOOK_URL`: Your Slack webhook URL
   - `DEPLOY_SSH_KEY`: SSH key for deployment servers (if applicable)
   - `PRODUCTION_HOST`: Production server hostname
   - `STAGING_HOST`: Staging server hostname

2. **Branch Protection Rules**
   
   Configure branch protection for `main`:
   - Require pull request reviews before merging
   - Require status checks to pass (code-quality, test-suite, security-scanning)
   - Dismiss stale pull request approvals when new commits are pushed
   - Include administrators

### Pipeline Stages

#### 1. Code Quality Checks
- Python linting with flake8
- TypeScript type checking
- ESLint for JavaScript/TypeScript
- Runs on every push and PR

#### 2. Security Scanning
- Trivy vulnerability scanner for dependencies
- Python Safety check for known vulnerabilities
- Results uploaded to GitHub Security tab

#### 3. Test Suite
- Python unit tests with pytest
- Frontend tests with Jest
- Code coverage reporting with Codecov
- PostgreSQL service for integration tests

#### 4. Performance Analysis
- Frontend bundle size analysis
- Lighthouse CI for performance metrics
- Identifies optimization opportunities

#### 5. Deployment
- **Staging**: Automatic deployment on push to `develop`
- **Production**: Automatic deployment on push to `main`
- Includes smoke tests and rollback capabilities

#### 6. Scheduled Optimization
- Runs daily at 2 AM
- Analyzes codebase for improvements
- Can create automated PRs with optimizations

## Integration with Improvement System

### Connecting Components

1. **Update Simple Improvement System**
   
   The improvement system reads `system-status.json` and triggers notifications:
   ```python
   from notification_system import NotificationSystem
   
   # In your agent logic
   if critical_issue_found:
       notification_system.send_slack_notification(
           message=f"Critical issue in {agent_name}: {issue}",
           level="critical"
       )
   ```

2. **Daily Summary Integration**
   
   The system automatically sends daily summaries based on:
   - Agent performance metrics
   - Goal progress
   - System health status
   - Recent improvements

3. **Automated PR Creation**
   
   When agents identify improvements:
   ```python
   # Agent creates branch and commits changes
   # Then triggers CI/CD pipeline via PR
   ```

### Workflow Example

1. **Agent Detection**: Code quality agent detects inefficient algorithm
2. **Local Fix**: Agent refactors the code locally
3. **Notification**: Sends Slack alert about the improvement
4. **PR Creation**: Creates PR with the fix
5. **CI/CD Trigger**: Pipeline runs all checks
6. **Review**: Team reviews and approves
7. **Deployment**: Automatic deployment to production
8. **Confirmation**: Success notification sent

## Troubleshooting

### Common Issues

#### Slack Notifications Not Working
- Verify webhook URL is correct
- Check `enable_slack` is set to `true`
- Review logs in `/Users/studio/hardcard/logs/notification.log`

#### Email Delivery Failures
- Ensure SMTP credentials are correct
- For Gmail, use app-specific passwords
- Check firewall rules for SMTP ports
- Verify recipient addresses are valid

#### CI/CD Pipeline Failures
- Check GitHub Actions logs for specific errors
- Ensure all secrets are properly configured
- Verify branch protection rules aren't blocking
- Check service dependencies (PostgreSQL, etc.)

#### Agent Integration Issues
- Confirm `notification-system.py` is running
- Check `system-status.json` is being updated
- Verify file permissions for log directory
- Review agent-specific logs

### Debug Mode

Enable debug logging:
```python
# In notification-system.py
logging.basicConfig(level=logging.DEBUG)
```

### Manual Testing

Test notifications manually:
```python
from notification_system import NotificationSystem

# Test Slack
ns = NotificationSystem()
ns.send_slack_notification("Test message", "info")

# Test Email
ns.send_email_notification(
    "Test Subject",
    "<h1>Test Body</h1><p>This is a test.</p>"
)
```

## Architecture Overview

```
┌─────────────────────┐
│ Improvement System  │
│  (Autonomous Agents)│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐     ┌──────────────────┐
│  system-status.json │◄────│ Notification     │
│  (Shared State)     │     │ System           │
└─────────────────────┘     └────────┬─────────┘
                                     │
                            ┌────────┴────────┐
                            ▼                 ▼
                     ┌─────────────┐   ┌─────────────┐
                     │    Slack    │   │    Email    │
                     │  Webhooks   │   │   Reports   │
                     └─────────────┘   └─────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │   GitHub    │
                     │   Actions   │
                     │   CI/CD     │
                     └─────────────┘
```

## Best Practices

1. **Notification Hygiene**
   - Avoid notification spam with proper thresholds
   - Use batching for non-critical alerts
   - Include actionable information in messages

2. **Security**
   - Never commit secrets to version control
   - Use environment variables or secret management
   - Rotate credentials regularly

3. **Monitoring**
   - Review notification logs weekly
   - Adjust thresholds based on false positive rate
   - Track notification delivery success rate

4. **CI/CD Optimization**
   - Use caching to speed up builds
   - Parallelize independent jobs
   - Set appropriate timeouts
   - Monitor pipeline duration trends

## Next Steps

1. Configure your notification channels
2. Set up GitHub repository secrets
3. Deploy the notification system
4. Monitor initial runs and adjust thresholds
5. Train team on responding to automated alerts

For additional support, check the logs in `/Users/studio/hardcard/logs/` or reach out to the development team.