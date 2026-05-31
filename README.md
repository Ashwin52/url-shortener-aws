# URL Shortener with Real-time Analytics 🔗

A production-inspired URL shortener built on AWS — designed with system design principles including hashing, collision handling, caching, and event-driven analytics.

---

## Architecture

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | Python + FastAPI |
| Database | AWS DynamoDB |
| Analytics Queue | AWS SQS |
| Data Lake | AWS S3 + Athena |
| CDN | AWS CloudFront |
| CI/CD | GitHub Actions |
| Frontend | React |

## Features (Progressive Build)

- [x] POST /shorten — Generate short code with Base62 encoding
- [x] GET /{code} — Redirect to original URL
- [x] Collision handling via DynamoDB conditional writes
- [ ] TTL-based caching layer
- [ ] Rate limiting middleware
- [ ] Link expiry support
- [ ] Real-time click analytics via SQS
- [ ] React analytics dashboard
- [ ] GitHub Actions CI/CD pipeline

---

## System Design Concepts Covered

- **Hashing + Encoding** — Base62 over MD5/UUID, 56B+ combinations
- **Collision Handling** — Conditional write + retry pattern
- **Caching Strategy** — TTL-based cache, cache-aside pattern
- **Rate Limiting** — Token bucket algorithm
- **Event-driven Architecture** — Async analytics via SQS
- **Data Partitioning** — DynamoDB partition key design
- **CDN + Edge Caching** — CloudFront for low latency redirects

---

## Local Setup

```bash
# Clone repo
git clone https://github.com/Ashwin52/url-shortener-aws.git
cd url-shortener-aws

# Install dependencies
pip3 install fastapi uvicorn boto3 python-jose --break-system-packages

# Configure AWS
aws configure

# Run locally
python3 -m uvicorn backend.main:app --reload
```

## API Testing

```bash
# Shorten a URL
curl -X POST "http://localhost:8000/shorten" \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://www.google.com"}'

# Redirect
curl "http://localhost:8000/{short_code}"
```

---

## AWS Services Used

- **DynamoDB** — Primary store, PAY_PER_REQUEST billing
- **SQS** — Click event queue (replaces Kinesis, cost-effective)
- **S3** — Analytics data lake
- **Athena** — Serverless SQL on S3
- **CloudFront** — CDN for low latency
- **Lambda** — Serverless compute
- **API Gateway** — HTTP API layer

---

## Author

**Ashwin** — ECE Student | Aspiring Cloud & DevOps Engineer

[![GitHub](https://img.shields.io/badge/GitHub-Ashwin52-black)](https://github.com/Ashwin52)
