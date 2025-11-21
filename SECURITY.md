# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Semantic Foragecast Engine seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Where to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to:
- **Security Team**: [security@semanticintent.com](mailto:security@semanticintent.com)

### What to Include

Please include the following information in your report:

- **Type of vulnerability** (e.g., code injection, path traversal, etc.)
- **Full paths** of source file(s) related to the vulnerability
- **Location** of the affected source code (tag/branch/commit or direct URL)
- **Step-by-step instructions** to reproduce the issue
- **Proof-of-concept or exploit code** (if possible)
- **Impact** of the vulnerability, including how an attacker might exploit it

### Response Timeline

- **Acknowledgment**: Within 48 hours of report
- **Initial Assessment**: Within 5 business days
- **Status Update**: Every 7 days until resolved
- **Resolution**: Varies based on severity (see below)

### Severity Levels

| Severity | Response Time | Example |
|----------|---------------|---------|
| **Critical** | 24-48 hours | Remote code execution, data breach |
| **High** | 1 week | Privilege escalation, authentication bypass |
| **Medium** | 2-4 weeks | Information disclosure, DoS |
| **Low** | 4-8 weeks | Minor information leaks |

### Disclosure Policy

- **Coordinated disclosure**: We follow a coordinated disclosure process
- **Embargo period**: Typically 90 days from initial report
- **Public disclosure**: After fix is released and users have had time to update
- **Credit**: We will credit reporters in security advisories (unless they prefer to remain anonymous)

## Security Best Practices for Users

### Safe Configuration

1. **Validate input files**
   - Only use trusted audio/image files
   - Scan files with antivirus before processing
   - Be cautious with files from unknown sources

2. **Limit file permissions**
   - Run with minimal necessary permissions
   - Avoid running as root/administrator
   - Use dedicated service accounts in production

3. **Network security**
   - This tool does not require internet access
   - Block outbound connections if running in production
   - Use firewall rules to restrict access

### Deployment Security

1. **Docker/Container Security**
   ```bash
   # Use non-root user
   docker run --user 1000:1000 ...

   # Limit resources
   docker run --memory="4g" --cpus="2" ...

   # Read-only root filesystem
   docker run --read-only --tmpfs /tmp ...
   ```

2. **File System Isolation**
   - Mount input directories read-only
   - Use separate output directory
   - Limit directory traversal

3. **Dependency Security**
   ```bash
   # Regularly update dependencies
   pip install --upgrade -r requirements.txt

   # Scan for vulnerabilities
   pip install safety
   safety check
   ```

## Known Security Considerations

### Local File Access

This tool requires:
- **Read access** to input files (audio, images, lyrics)
- **Write access** to output directory
- **Execute access** to Blender and FFmpeg

**Mitigation**: Use appropriate file permissions and run with least privilege.

### Blender Python API

Blender scripts have full Python access:
- Can read/write files
- Can execute system commands
- Can access network (if Blender has access)

**Mitigation**:
- Only run trusted Blender scripts
- Review `blender_script.py` and `grease_pencil.py` before use
- Run in isolated environment (container, VM) for untrusted content

### FFmpeg Processing

FFmpeg processes user-provided media files:
- Potential for malformed file exploits
- Could trigger FFmpeg vulnerabilities

**Mitigation**:
- Keep FFmpeg updated
- Validate file formats before processing
- Run in sandboxed environment

### Audio Analysis Libraries

LibROSA and other audio libraries process untrusted audio:
- Potential for buffer overflows
- Could trigger parser vulnerabilities

**Mitigation**:
- Keep dependencies updated
- Validate audio files
- Use virtual environments

## Security Updates

### How We Handle Security Issues

1. **Investigate** the reported vulnerability
2. **Develop** a fix in a private repository
3. **Test** the fix thoroughly
4. **Release** patch version (e.g., 1.0.1 → 1.0.2)
5. **Publish** security advisory
6. **Notify** users via GitHub Security Advisories
7. **Credit** reporter (with permission)

### Staying Informed

Subscribe to security updates:
- **GitHub Watch**: Click "Watch" → "Custom" → "Security alerts"
- **GitHub Security Advisories**: Automatic for repository watchers
- **Release Notes**: Check CHANGELOG.md for security fixes

## Security Checklist for Contributors

When contributing code, ensure:

- [ ] No hardcoded credentials or secrets
- [ ] Input validation for all user-provided data
- [ ] Proper error handling (no information leakage)
- [ ] Dependencies are up-to-date
- [ ] No use of `eval()`, `exec()`, or similar dangerous functions
- [ ] File paths are validated (no directory traversal)
- [ ] No unnecessary file/network permissions
- [ ] Security implications documented

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [Blender Security](https://www.blender.org/about/security/)

## Contact

- **Security Issues**: [security@semanticintent.com](mailto:security@semanticintent.com)
- **General Support**: [support@semanticintent.com](mailto:support@semanticintent.com)
- **GitHub Issues**: [Report non-security bugs](https://github.com/semanticintent/semantic-foragecast-engine/issues)

---

**Thank you for helping keep Semantic Foragecast Engine and its users safe!**
