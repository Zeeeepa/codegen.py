# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the Codegen CLI. The CLI's sophisticated error handling system provides detailed feedback, but this guide offers additional context and solutions.

## Quick Diagnostics

### Health Check Command

Run a comprehensive health check to identify common issues:

```bash
codegen status --verbose
```

This command checks:
- Configuration validity
- API connectivity
- Authentication status
- Network connectivity
- Service availability

### Configuration Validation

Validate your configuration setup:

```bash
codegen config validate
```

This will identify:
- Missing required settings
- Invalid configuration values
- Environment variable issues
- Configuration file problems

## Common Error Scenarios

### Authentication Issues

#### Error: "Authentication failed: Invalid API token"

**Symptoms:**
- Exit code: 3
- Cannot access any API endpoints
- "Unauthorized" or "Invalid token" messages

**Diagnosis:**
```bash
# Check current token status
codegen auth status

# Verify token in configuration
codegen config show | grep token

# Test token manually
curl -H "Authorization: Bearer YOUR_TOKEN" https://api.codegen.com/v1/organizations
```

**Solutions:**

1. **Generate a new token:**
   ```bash
   # Visit https://codegen.com/settings to generate a new token
   codegen config set api-token YOUR_NEW_TOKEN
   ```

2. **Check token permissions:**
   - Ensure token has required scopes
   - Verify organization access
   - Check token expiration

3. **Environment variable conflicts:**
   ```bash
   # Check for conflicting environment variables
   env | grep CODEGEN
   
   # Unset conflicting variables
   unset CODEGEN_API_TOKEN
   ```

#### Error: "API token is required"

**Symptoms:**
- Exit code: 2
- No API token found in configuration
- Commands fail immediately

**Solutions:**

1. **Set API token:**
   ```bash
   codegen config set api-token YOUR_TOKEN
   ```

2. **Use environment variable:**
   ```bash
   export CODEGEN_API_TOKEN=your_token_here
   codegen command
   ```

3. **Initialize configuration:**
   ```bash
   codegen config init
   # Follow the interactive setup
   ```

### Network Connectivity Issues

#### Error: "Network error: Connection failed"

**Symptoms:**
- Exit code: 5
- Timeouts or connection refused errors
- DNS resolution failures

**Diagnosis:**
```bash
# Test basic connectivity
ping api.codegen.com

# Test HTTPS connectivity
curl -I https://api.codegen.com

# Check DNS resolution
nslookup api.codegen.com

# Test with verbose output
codegen --verbose command
```

**Solutions:**

1. **Check internet connection:**
   - Verify general internet connectivity
   - Test other HTTPS sites
   - Check network configuration

2. **Firewall and proxy issues:**
   ```bash
   # Check if behind corporate firewall
   curl -v https://api.codegen.com
   
   # Configure proxy if needed
   export HTTPS_PROXY=http://proxy.company.com:8080
   export HTTP_PROXY=http://proxy.company.com:8080
   ```

3. **DNS issues:**
   ```bash
   # Try alternative DNS servers
   echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
   
   # Flush DNS cache (macOS)
   sudo dscacheutil -flushcache
   
   # Flush DNS cache (Linux)
   sudo systemctl restart systemd-resolved
   ```

4. **Custom API endpoint:**
   ```bash
   # If using custom endpoint
   codegen config set api.base-url https://your-custom-api.com
   ```

#### Error: "Request timed out"

**Symptoms:**
- Exit code: 8
- Long delays before failure
- Partial responses

**Solutions:**

1. **Increase timeout:**
   ```bash
   codegen config set api.timeout 60
   # or
   export CODEGEN_API_TIMEOUT=60
   ```

2. **Check network latency:**
   ```bash
   # Test latency to API
   ping -c 5 api.codegen.com
   
   # Test with traceroute
   traceroute api.codegen.com
   ```

3. **Retry with backoff:**
   ```bash
   # The CLI automatically retries, but you can configure it
   codegen config set api.max-retries 5
   codegen config set api.retry-delay 2.0
   ```

### Rate Limiting Issues

#### Error: "Rate limit exceeded"

**Symptoms:**
- Exit code: 6
- "Too many requests" messages
- Temporary blocks on API access

**Understanding Rate Limits:**
- Rate limits protect the API from overuse
- Limits vary by plan and endpoint
- Limits reset after a time period

**Solutions:**

1. **Wait for reset:**
   ```bash
   # The error message includes wait time
   # Wait for the specified period before retrying
   ```

2. **Implement delays:**
   ```bash
   # Add delays between commands
   codegen command1
   sleep 5
   codegen command2
   ```

3. **Upgrade plan:**
   - Visit https://codegen.com/pricing
   - Higher plans have increased rate limits

4. **Optimize usage:**
   - Batch operations when possible
   - Use pagination efficiently
   - Cache results locally

### Configuration Issues

#### Error: "Configuration validation failed"

**Symptoms:**
- Exit code: 2
- Invalid configuration values
- Missing required settings

**Diagnosis:**
```bash
# Validate configuration
codegen config validate

# Show current configuration
codegen config show

# Show configuration sources
codegen config show --sources
```

**Solutions:**

1. **Fix invalid values:**
   ```bash
   # Fix invalid timeout
   codegen config set api.timeout 30
   
   # Fix invalid output format
   codegen config set output.format table
   
   # Fix invalid log level
   codegen config set log.level INFO
   ```

2. **Reset to defaults:**
   ```bash
   # Reset specific setting
   codegen config unset api.timeout
   
   # Reset all configuration
   rm ~/.codegen/config.yaml
   codegen config init
   ```

3. **Environment variable conflicts:**
   ```bash
   # Check for conflicting environment variables
   env | grep CODEGEN
   
   # Unset problematic variables
   unset CODEGEN_INVALID_SETTING
   ```

#### Error: "Config file not found" or parsing errors

**Symptoms:**
- Cannot read configuration file
- YAML/TOML parsing errors
- Permission denied errors

**Solutions:**

1. **Create configuration file:**
   ```bash
   codegen config init
   ```

2. **Fix file permissions:**
   ```bash
   # Fix permissions on config directory
   chmod 755 ~/.codegen
   chmod 644 ~/.codegen/config.yaml
   ```

3. **Fix syntax errors:**
   ```bash
   # Validate YAML syntax
   python -c "import yaml; yaml.safe_load(open('~/.codegen/config.yaml'))"
   
   # Or recreate the file
   mv ~/.codegen/config.yaml ~/.codegen/config.yaml.backup
   codegen config init
   ```

### Validation Errors

#### Error: "Input validation failed"

**Symptoms:**
- Exit code: 4
- Field-specific error messages
- Invalid parameter values

**Common Validation Issues:**

1. **Invalid agent run parameters:**
   ```bash
   # Error: prompt cannot be empty
   codegen agent run --prompt "Your actual prompt here"
   
   # Error: invalid organization ID
   codegen agent run --org-id valid-org-id --prompt "prompt"
   ```

2. **Invalid pagination parameters:**
   ```bash
   # Error: limit must be between 1 and 100
   codegen agent list --limit 50
   
   # Error: skip must be >= 0
   codegen agent list --skip 0
   ```

3. **Invalid file paths:**
   ```bash
   # Error: file not found
   codegen agent run --file ./existing-file.txt
   ```

**Solutions:**

1. **Check command syntax:**
   ```bash
   codegen command --help
   ```

2. **Validate inputs:**
   - Check file paths exist
   - Verify IDs are correct format
   - Ensure required parameters are provided

3. **Use verbose mode:**
   ```bash
   codegen --verbose command
   ```

## Advanced Troubleshooting

### Debug Mode

Enable comprehensive debugging:

```bash
# Enable debug logging
export CODEGEN_LOG_LEVEL=DEBUG
codegen command

# Or use verbose flag
codegen --verbose command

# Save debug output to file
codegen --verbose command 2> debug.log
```

### Network Debugging

#### Capture Network Traffic

```bash
# Using tcpdump (requires root)
sudo tcpdump -i any -w codegen-traffic.pcap host api.codegen.com

# Using Wireshark
# Start Wireshark and filter by "host api.codegen.com"
```

#### Test with curl

```bash
# Test API endpoint directly
curl -v -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.codegen.com/v1/organizations

# Test with specific timeout
curl --max-time 30 -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.codegen.com/v1/organizations
```

### Configuration Debugging

#### Check Configuration Precedence

```bash
# Show configuration with sources
codegen config show --sources

# Check environment variables
env | grep CODEGEN | sort

# Check configuration file locations
find ~ -name "*codegen*" -type f 2>/dev/null
```

#### Validate Configuration Files

```bash
# Validate YAML
python -c "
import yaml
try:
    with open('~/.codegen/config.yaml') as f:
        yaml.safe_load(f)
    print('YAML is valid')
except Exception as e:
    print(f'YAML error: {e}')
"

# Validate TOML
python -c "
import toml
try:
    with open('~/.codegen/config.toml') as f:
        toml.load(f)
    print('TOML is valid')
except Exception as e:
    print(f'TOML error: {e}')
"
```

### Performance Issues

#### Slow Commands

**Diagnosis:**
```bash
# Time command execution
time codegen command

# Enable verbose output to see timing
codegen --verbose command

# Check network latency
ping -c 10 api.codegen.com
```

**Solutions:**

1. **Optimize network settings:**
   ```bash
   # Reduce timeout for faster failures
   codegen config set api.timeout 15
   
   # Increase retries for reliability
   codegen config set api.max-retries 5
   ```

2. **Use pagination:**
   ```bash
   # Instead of fetching all results
   codegen agent list --limit 20
   ```

3. **Cache results:**
   ```bash
   # Save results to file for reuse
   codegen agent list --output json > agents.json
   ```

#### Memory Issues

**Symptoms:**
- Out of memory errors
- Slow performance with large datasets
- System becomes unresponsive

**Solutions:**

1. **Use pagination:**
   ```bash
   # Process data in chunks
   codegen agent list --limit 50 --skip 0
   codegen agent list --limit 50 --skip 50
   ```

2. **Stream processing:**
   ```bash
   # Use JSON output and process with jq
   codegen agent list --output json | jq '.items[] | .id'
   ```

## Error Code Reference

| Exit Code | Error Type | Description | Common Causes |
|-----------|------------|-------------|---------------|
| 0 | Success | Command completed successfully | - |
| 1 | General Error | Unexpected error occurred | Programming errors, system issues |
| 2 | Configuration Error | Configuration problem | Missing config, invalid values |
| 3 | Authentication Error | Authentication failed | Invalid token, expired credentials |
| 4 | Validation Error | Input validation failed | Invalid parameters, malformed input |
| 5 | Network Error | Network connectivity issue | No internet, DNS problems, firewall |
| 6 | Rate Limit Error | Rate limit exceeded | Too many requests |
| 7 | Not Found Error | Resource not found | Invalid ID, insufficient permissions |
| 8 | Timeout Error | Request timed out | Slow network, server overload |
| 9 | Server Error | Server-side error | API issues, maintenance |
| 10 | API Error | Generic API error | Various API-related issues |
| 130 | Interrupted | User interrupted (Ctrl+C) | User cancellation |

## Getting Help

### Built-in Help

```bash
# General help
codegen --help

# Command-specific help
codegen command --help

# Subcommand help
codegen command subcommand --help
```

### Verbose Output

```bash
# Enable verbose output for any command
codegen --verbose command

# Combine with other debugging
codegen --verbose --output json command
```

### Log Files

```bash
# Enable logging to file
export CODEGEN_LOG_FILE=/tmp/codegen.log
codegen command

# Or configure in config file
codegen config set log.file /tmp/codegen.log
```

### Support Resources

1. **Documentation**: https://docs.codegen.com
2. **GitHub Issues**: https://github.com/Zeeeepa/codegen.py/issues
3. **Community Forum**: https://community.codegen.com
4. **Support Email**: support@codegen.com

### Reporting Issues

When reporting issues, include:

1. **Command that failed:**
   ```bash
   codegen agent run --prompt "test"
   ```

2. **Error message and exit code:**
   ```
   Error: Authentication failed: Invalid API token
   Exit code: 3
   ```

3. **Configuration (sanitized):**
   ```bash
   codegen config show | sed 's/token.*/token: [REDACTED]/'
   ```

4. **Environment information:**
   ```bash
   # System information
   uname -a
   python --version
   
   # CLI version
   codegen --version
   
   # Environment variables (sanitized)
   env | grep CODEGEN | sed 's/TOKEN.*/TOKEN=[REDACTED]/'
   ```

5. **Debug output:**
   ```bash
   codegen --verbose command 2> debug.log
   # Attach debug.log (remove sensitive information)
   ```

## Prevention Tips

### Regular Maintenance

1. **Update regularly:**
   ```bash
   pip install --upgrade codegen-py
   ```

2. **Validate configuration periodically:**
   ```bash
   codegen config validate
   ```

3. **Monitor rate limits:**
   - Track API usage
   - Implement proper delays
   - Consider upgrading plan if needed

### Best Practices

1. **Use configuration files:**
   - Avoid hardcoding tokens in scripts
   - Use environment-specific configs
   - Keep sensitive data secure

2. **Implement error handling:**
   ```bash
   #!/bin/bash
   if ! codegen command; then
     echo "Command failed with exit code $?"
     exit 1
   fi
   ```

3. **Monitor and log:**
   - Enable logging for production use
   - Monitor error patterns
   - Set up alerts for critical failures

4. **Test in development:**
   - Validate commands in dev environment
   - Test error scenarios
   - Verify configuration before deployment

---

For more information, see:
- [Error Handling Guide](error_handling.md)
- [Configuration Guide](configuration.md)
- [Developer Guide](developer_guide.md)

