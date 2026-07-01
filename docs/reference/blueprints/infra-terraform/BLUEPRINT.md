# Blueprint: Infrastructure — Terraform

**Status:** DEFERRED — Implemented in PI-10  
**Target PI:** PI-10-General-Availability

## Purpose

Terraform modules for deploying the Agentic Engineering Platform to AWS (EKS) and Azure (AKS).

## Module Structure

```
infra/terraform/
├── modules/
│   ├── eks/                    # AWS EKS cluster
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── aks/                    # Azure AKS cluster
│   ├── aurora-postgres/        # AWS Aurora PostgreSQL Multi-AZ
│   ├── azure-flexible-server/  # Azure PostgreSQL Flexible Server
│   ├── elasticache-redis/      # AWS Redis Cluster
│   ├── azure-redis/            # Azure Redis Cache
│   ├── msk-kafka/              # AWS Managed Kafka
│   ├── azure-event-hubs/       # Azure Event Hubs (Kafka protocol)
│   ├── clickhouse/             # ClickHouse Cloud via provider
│   ├── vault-hcp/              # HashiCorp Cloud Platform Vault
│   └── pgvector/               # RDS + pgvector extension
├── envs/
│   ├── dev/
│   │   ├── main.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   └── prod/
└── README.md
```

## Naming Conventions

All Terraform resources prefixed `aep_`:
- `aep_eks_cluster`
- `aep_aurora_cluster`
- `aep_msk_cluster`

## Tagging Strategy

Every resource tagged:
- `Project: aep`
- `Environment: dev|staging|prod`
- `ManagedBy: terraform`
- `CostCenter: platform-engineering`

## State Backend

Remote state in S3 (AWS) or Azure Blob Storage with state locking via DynamoDB or Azure Blob lease.

## Deployment Flow

```
terraform init
terraform plan -out=tfplan
# Human reviews plan (non-bypassable — Constitution H2)
terraform apply tfplan
```

No `terraform apply -auto-approve` in any environment.
