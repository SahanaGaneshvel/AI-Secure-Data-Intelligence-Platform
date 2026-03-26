/**
 * Curated demo datasets for reliable live demonstrations
 * Each dataset is designed to showcase specific detection capabilities
 */

export interface DemoDataset {
  name: string;
  description: string;
  inputType: "text" | "log" | "file";
  content: string;
  expectedRisk: "Low" | "Medium" | "High" | "Critical";
  highlights: string[];
}

export const DEMO_DATASETS: DemoDataset[] = [
  {
    name: "Clean Case",
    description: "Low-risk user query with minimal sensitive data",
    inputType: "text",
    expectedRisk: "Low",
    highlights: ["Email detection", "Username field"],
    content: `{
  "user": "john_doe",
  "email": "user@example.com",
  "query": "SELECT name, email FROM users WHERE id = ?",
  "timestamp": "2026-03-24T10:00:00Z"
}`,
  },
  {
    name: "Mixed Risk",
    description: "API payload with PII, credentials, and SQL injection attempt",
    inputType: "text",
    expectedRisk: "Critical",
    highlights: ["GitHub PAT", "SQL Injection", "Email PII"],
    content: `{
  "user": "admin",
  "email": "jdoe@company.com",
  "token": "ghp_abcdefghijklmnopqrstuvwxyz1234567890",
  "query": "SELECT * FROM users WHERE id = 1 OR 1=1;",
  "api_key": "AKIA1234567890ABCDEF"
}`,
  },
  {
    name: "High Risk Logs",
    description: "Server logs with repeated failures, stack traces, and credential leaks",
    inputType: "log",
    expectedRisk: "Critical",
    highlights: [
      "AWS Access Key",
      "Repeated auth failures",
      "Stack trace exposure",
      "Slack webhook leak",
    ],
    content: `2026-03-24 10:15:32 INFO Starting authentication service
2026-03-24 10:15:45 ERROR Authentication failed for user admin
2026-03-24 10:15:50 ERROR Authentication failed for user admin
2026-03-24 10:15:55 ERROR Authentication failed for user admin
2026-03-24 10:16:00 ERROR Authentication failed for user admin
2026-03-24 10:16:05 ERROR Authentication failed for user admin
2026-03-24 10:16:10 ERROR Authentication failed for user root
2026-03-24 10:16:15 ERROR Authentication failed for user root
2026-03-24 10:16:20 WARN Detected brute force attempt from 192.168.1.100
2026-03-24 10:16:25 DEBUG AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
2026-03-24 10:16:30 DEBUG AWS_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
2026-03-24 10:16:35 ERROR Uncaught exception in auth module
Traceback (most recent call last):
  File "/app/auth.py", line 42, in validate_token
    decoded = jwt.decode(token, SECRET_KEY)
  File "/usr/lib/python3.9/jwt/api_jwt.py", line 119, in decode
    raise DecodeError("Invalid token")
jwt.exceptions.DecodeError: Invalid token
2026-03-24 10:16:40 INFO Slack webhook: https://hooks.slack.com/services/TXXXXXXXX/BXXXXXXXX/XXXXXXXXXXXXXXXX
2026-03-24 10:16:45 WARN System entering degraded mode`,
  },
  {
    name: "SQL Injection",
    description: "Multiple SQL injection patterns and malicious queries",
    inputType: "text",
    expectedRisk: "High",
    highlights: ["Union-based injection", "Boolean injection", "Comment injection"],
    content: `-- User input query 1
SELECT * FROM users WHERE username = 'admin' AND password = '' OR '1'='1';

-- User input query 2
SELECT id, name, email FROM customers WHERE id = 1 UNION SELECT username, password, email FROM admin_users;

-- User input query 3
UPDATE products SET price = 0 WHERE id = 5; DROP TABLE orders; --

-- User input query 4
SELECT * FROM accounts WHERE account_id = '1' AND 1=1 AND '1'='1';`,
  },
  {
    name: "Production Log Nightmare",
    description: "Comprehensive log file with multiple critical security issues",
    inputType: "log",
    expectedRisk: "Critical",
    highlights: [
      "Authorization headers leaked",
      "Database credentials in errors",
      "Multiple stack traces",
      "Session tokens exposed",
      "Brute-force detection",
      "SQL errors revealing schema",
    ],
    content: `2026-03-25 08:00:00 INFO [Server] Starting API server on port 8080
2026-03-25 08:00:01 INFO [DB] Connected to postgresql://admin:P@ssw0rd123@db.internal.com:5432/maindb
2026-03-25 08:00:05 INFO [Auth] JWT secret loaded: super_secret_jwt_key_2026_prod
2026-03-25 08:15:23 DEBUG Request headers: Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4ifQ.signature
2026-03-25 08:15:24 DEBUG Cookie: session_id=a7b3c9d1e5f2g8h4i6j0k; auth_token=secure_token_abc123xyz789
2026-03-25 08:20:10 ERROR Authentication failed for user: admin from 203.0.113.45
2026-03-25 08:20:15 ERROR Authentication failed for user: admin from 203.0.113.45
2026-03-25 08:20:20 ERROR Authentication failed for user: root from 203.0.113.45
2026-03-25 08:20:25 ERROR Authentication failed for user: administrator from 203.0.113.45
2026-03-25 08:20:30 ERROR Authentication failed for user: user from 203.0.113.45
2026-03-25 08:20:35 ERROR Authentication failed for user: admin from 203.0.113.46
2026-03-25 08:20:40 ERROR Authentication failed for user: admin from 203.0.113.47
2026-03-25 08:20:45 ERROR Authentication failed for user: admin from 203.0.113.48
2026-03-25 08:20:50 ERROR Authentication failed for user: admin from 203.0.113.49
2026-03-25 08:20:55 ERROR Authentication failed for user: admin from 203.0.113.50
2026-03-25 08:25:00 ERROR [API] Exception in /api/users endpoint
Traceback (most recent call last):
  File "/var/www/app/routes/users.py", line 145, in get_user_data
    user = User.query.filter_by(id=user_id).first()
  File "/usr/local/lib/python3.9/sqlalchemy/orm/query.py", line 2845, in first
    return self.limit(1)._execute_and_instances(context).scalar()
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
2026-03-25 08:30:15 ERROR [Payment] Failed to process payment for user john@company.com with card ending 4532
2026-03-25 08:30:16 ERROR [Payment] Error details: password=EXAMPLE_PASS, api_key=sk_live_EXAMPLE_KEY_FOR_TESTING
2026-03-25 08:35:22 INFO [Cache] Redis connection: redis://:cache_password_xyz@cache.internal:6379/0
2026-03-25 08:40:00 ERROR [DB] SQL Error:
mysql_query(): You have an error in your SQL syntax near 'WHERE user_id = '123' at line 1
Query: SELECT * FROM user_accounts WHERE user_id = '123' AND password = 'plain_password_123'
2026-03-25 08:45:10 DEBUG console.log() called with: {user: 'admin', token: 'secret_admin_token_xyz', role: 'superuser'}
2026-03-25 08:50:00 WARN [Security] Detected XSS attempt: <script>alert('hacked')</script> from IP 198.51.100.23
2026-03-25 08:55:30 ERROR [Email] Failed to send email to user@domain.com - SMTP password: smtp_pass_2026!
2026-03-25 09:00:00 INFO [Integration] GitHub PAT: ghp_1234567890abcdefghijklmnopqrstuvwxyz
2026-03-25 09:05:15 DEBUG [AWS] Accessing S3 bucket with credentials: AKIAIOSFODNN7EXAMPLE
2026-03-25 09:10:00 ERROR [API] Unhandled exception in request handler
Exception: NullPointerException at com.company.api.UserController.getProfile(UserController.java:89)
	at com.company.service.AuthService.validateSession(AuthService.java:234)
	at com.company.filter.SecurityFilter.doFilter(SecurityFilter.java:56)
2026-03-25 09:15:00 INFO [Slack] Notification sent to https://hooks.slack.com/services/TXXXXXXXX/BXXXXXXXX/XXXXXXXXXXXXXXXX
2026-03-25 09:20:30 ERROR Internal server error: Access denied for user 'dbuser'@'localhost' (using password: YES)`,
  },
  {
    name: "Doc Example Log",
    description: "Example from hackathon doc - credentials in logs",
    inputType: "log",
    expectedRisk: "Critical",
    highlights: ["Email", "Password in logs", "API key", "Stack trace"],
    content: `2026-03-10 10:00:01 INFO User login
email=admin@company.com
password=EXAMPLE_PASS
api_key=sk-prod-xyz
ERROR stack trace: NullPointerException at service.java:45`,
  },
  {
    name: "Distributed Attack Pattern",
    description: "Coordinated brute-force from multiple IPs with credential stuffing",
    inputType: "log",
    expectedRisk: "Critical",
    highlights: [
      "Distributed brute-force",
      "Credential stuffing",
      "Geographic anomaly",
      "Rate limit bypass",
    ],
    content: `2026-03-25 14:00:01 INFO [Auth] Login attempt for user: john.smith@corp.com from 45.33.32.156 (US)
2026-03-25 14:00:02 ERROR [Auth] Failed login for john.smith@corp.com - invalid password
2026-03-25 14:00:03 INFO [Auth] Login attempt for user: john.smith@corp.com from 185.220.101.34 (DE)
2026-03-25 14:00:04 ERROR [Auth] Failed login for john.smith@corp.com - invalid password
2026-03-25 14:00:05 INFO [Auth] Login attempt for user: john.smith@corp.com from 91.218.114.77 (RU)
2026-03-25 14:00:06 ERROR [Auth] Failed login for john.smith@corp.com - invalid password
2026-03-25 14:00:07 INFO [Auth] Login attempt for user: john.smith@corp.com from 103.152.220.44 (CN)
2026-03-25 14:00:08 ERROR [Auth] Failed login for john.smith@corp.com - invalid password
2026-03-25 14:00:09 WARN [Security] Distributed attack detected - 4 countries in 8 seconds
2026-03-25 14:00:10 INFO [Auth] Login attempt for user: sarah.jones@corp.com from 45.33.32.156 (US)
2026-03-25 14:00:11 ERROR [Auth] Failed login for sarah.jones@corp.com - invalid password
2026-03-25 14:00:12 INFO [Auth] Login attempt for user: mike.wilson@corp.com from 185.220.101.34 (DE)
2026-03-25 14:00:13 ERROR [Auth] Failed login for mike.wilson@corp.com - invalid password
2026-03-25 14:00:14 CRITICAL [Security] Credential stuffing attack - known breach passwords detected`,
  },
  {
    name: "Database Exfiltration",
    description: "Suspicious database queries indicating data exfiltration attempt",
    inputType: "log",
    expectedRisk: "Critical",
    highlights: [
      "Bulk data export",
      "Privilege escalation",
      "Schema enumeration",
      "Unusual query patterns",
    ],
    content: `2026-03-25 03:15:00 INFO [DB] Query from user analytics_readonly: SELECT table_name FROM information_schema.tables
2026-03-25 03:15:05 INFO [DB] Query from user analytics_readonly: SELECT column_name FROM information_schema.columns WHERE table_name='users'
2026-03-25 03:15:10 WARN [DB] Unusual query pattern detected - schema enumeration
2026-03-25 03:15:15 INFO [DB] Query from user analytics_readonly: SELECT COUNT(*) FROM users -- Result: 2,847,392
2026-03-25 03:15:20 INFO [DB] Query from user analytics_readonly: SELECT * FROM users LIMIT 100000 OFFSET 0
2026-03-25 03:15:45 INFO [DB] Query from user analytics_readonly: SELECT * FROM users LIMIT 100000 OFFSET 100000
2026-03-25 03:16:10 INFO [DB] Query from user analytics_readonly: SELECT * FROM users LIMIT 100000 OFFSET 200000
2026-03-25 03:16:35 ERROR [Security] Data exfiltration alert - 300,000 rows exported in 95 seconds
2026-03-25 03:16:36 INFO [DB] Query from user analytics_readonly: SELECT ssn, credit_card FROM users_pii
2026-03-25 03:16:37 CRITICAL [Security] PII access attempt blocked - user lacks pii_access role
2026-03-25 03:16:38 INFO [Audit] Incident created: INC-2026-0342 - Potential data breach`,
  },
  {
    name: "API Rate Abuse",
    description: "API abuse pattern with token theft and rate limit exploitation",
    inputType: "log",
    expectedRisk: "High",
    highlights: [
      "Rate limit abuse",
      "Token reuse",
      "Endpoint scraping",
      "Bot behavior",
    ],
    content: `2026-03-25 09:00:00 INFO [API] GET /api/v1/products - API Key: ak_live_xxx...789 - 200 OK (45ms)
2026-03-25 09:00:00 INFO [API] GET /api/v1/products - API Key: ak_live_xxx...789 - 200 OK (38ms)
2026-03-25 09:00:00 INFO [API] GET /api/v1/products - API Key: ak_live_xxx...789 - 200 OK (41ms)
2026-03-25 09:00:01 WARN [API] Rate limit warning: ak_live_xxx...789 at 950/1000 requests
2026-03-25 09:00:01 INFO [API] GET /api/v1/products?page=1 - API Key: ak_live_yyy...456 - 200 OK
2026-03-25 09:00:01 INFO [API] GET /api/v1/products?page=2 - API Key: ak_live_yyy...456 - 200 OK
2026-03-25 09:00:02 WARN [Security] Same User-Agent using multiple API keys from 192.168.1.50
2026-03-25 09:00:02 INFO [API] GET /api/v1/pricing - API Key: ak_live_zzz...123 - 200 OK
2026-03-25 09:00:02 INFO [API] GET /api/v1/inventory - API Key: ak_live_zzz...123 - 200 OK
2026-03-25 09:00:03 ERROR [API] Rate limit exceeded: ak_live_xxx...789 - 429 Too Many Requests
2026-03-25 09:00:03 WARN [Security] Bot behavior detected - 150 requests in 3 seconds, rotating keys`,
  },
  {
    name: "Multi-Cloud Secrets",
    description: "Configuration file with exposed cloud credentials",
    inputType: "file",
    expectedRisk: "Critical",
    highlights: [
      "GitHub PAT",
      "AWS keys",
      "GCP service account",
      "Stripe key",
      "Database password",
    ],
    content: `# Application Configuration
# WARNING: DO NOT COMMIT THIS FILE

[github]
token = ghp_abcd1234567890efghijklmnopqrstuv

[aws]
access_key_id = AKIAIOSFODNN7EXAMPLE
secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
region = us-east-1

[gcp]
project_id = my-project-12345
service_account_key = {
  "type": "service_account",
  "project_id": "my-project",
  "private_key_id": "abc123def456",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7...\\n-----END PRIVATE KEY-----\\n",
  "client_email": "service@my-project.iam.gserviceaccount.com"
}

[stripe]
publishable_key = pk_live_EXAMPLE_KEY_FOR_TESTING
secret_key = sk_live_EXAMPLE_KEY_FOR_TESTING

[database]
host = db.production.company.com
port = 5432
username = postgres
password = MyS3cr3tP@ssw0rd!2026
database = production_db

[slack]
webhook_url = https://hooks.slack.com/services/TXXXXXXXX/BXXXXXXXX/XXXXXXXXXXXXXXXX`,
  },
];

/**
 * Get a demo dataset by name
 */
export function getDemoDataset(name: string): DemoDataset | undefined {
  return DEMO_DATASETS.find((dataset) => dataset.name === name);
}

/**
 * Get all demo dataset names for UI display
 */
export function getDemoDatasetNames(): string[] {
  return DEMO_DATASETS.map((dataset) => dataset.name);
}
