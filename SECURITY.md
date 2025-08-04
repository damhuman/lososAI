# 🔐 Security Guidelines

## ⚠️ CRITICAL: Environment Variables

### 🚨 NEVER COMMIT THESE FILES:
- `.env` - Production environment variables
- `.env.prod` - Production environment  
- `.env.local` - Local development
- `cookies*.txt` - Session cookies
- `admin_cookies.txt` - Admin session cookies

### ✅ Setting Up Environment Variables

1. **Copy the template:**
   ```bash
   cp .env.template .env
   ```

2. **Generate secure values:**
   ```bash
   # Generate a secure secret key (32+ characters)
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # Or use openssl
   openssl rand -base64 32
   ```

3. **Update all CHANGE_ME values:**
   - `SECRET_KEY`: Use generated secret key
   - `TELEGRAM_BOT_TOKEN`: Get from @BotFather on Telegram
   - `POSTGRES_PASSWORD`: Use strong password (12+ chars)
   - `ADMIN_PASSWORD`: Use very strong password (16+ chars)
   - `S3_ACCESS_KEY`: Get from DigitalOcean Spaces
   - `S3_SECRET_KEY`: Get from DigitalOcean Spaces

## 🔑 Credential Management

### Telegram Bot Token
1. Message @BotFather on Telegram
2. Use `/newtoken` command
3. Replace the token in `.env`

### DigitalOcean Spaces
1. Go to DigitalOcean Control Panel
2. Navigate to Spaces → Manage Keys
3. Generate new Access Keys
4. Update S3_ACCESS_KEY and S3_SECRET_KEY

### Database Password
1. Connect to your PostgreSQL instance
2. Change the password:
   ```sql
   ALTER USER seafood_user PASSWORD 'your_new_strong_password';
   ```
3. Update POSTGRES_PASSWORD in `.env`

## 🛡️ Security Best Practices

### For Production:
- Use environment variables, never hardcode secrets
- Rotate credentials regularly (monthly)
- Use different passwords for each service
- Enable 2FA where possible
- Monitor access logs

### For Development:
- Never commit `.env` files
- Use different credentials for dev/prod
- Don't share credentials in chat/email
- Use secure password managers

## 🚨 If Credentials Are Compromised

1. **Immediately rotate all credentials:**
   - Generate new bot token
   - Create new S3 keys (delete old ones)
   - Change database password
   - Change admin password

2. **Check access logs:**
   - Review DigitalOcean access logs
   - Check Telegram bot logs
   - Monitor database connections

3. **Update all deployments:**
   - Update production environment
   - Restart all services
   - Verify new credentials work

## ✅ Verification Checklist

Before deploying:
- [ ] No `.env` files in git history
- [ ] All CHANGE_ME values updated
- [ ] Passwords are strong (16+ characters)
- [ ] Bot token is valid and working
- [ ] S3 keys have correct permissions
- [ ] Admin login works
- [ ] Database connection successful

## 📞 Emergency Response

If you suspect a security breach:
1. Immediately rotate all credentials
2. Check for unauthorized access
3. Review recent changes/commits
4. Update all running services
5. Monitor for suspicious activity

---

**Remember**: Security is everyone's responsibility! 🔒