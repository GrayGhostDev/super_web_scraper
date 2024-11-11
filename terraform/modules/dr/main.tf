```hcl
# Secondary region infrastructure for disaster recovery
provider "aws" {
  alias  = "secondary"
  region = var.secondary_region
}

# VPC in secondary region
module "vpc_secondary" {
  source = "../vpc"
  providers = {
    aws = aws.secondary
  }

  vpc_cidr     = var.vpc_cidr
  environment  = var.environment
  project_name = var.project_name
}

# EKS cluster in secondary region
module "eks_secondary" {
  source = "../eks"
  providers = {
    aws = aws.secondary
  }

  cluster_name = "${var.project_name}-${var.environment}-secondary"
  vpc_id       = module.vpc_secondary.vpc_id
  subnet_ids   = module.vpc_secondary.private_subnet_ids
  environment  = var.environment
  project_name = var.project_name
}

# RDS read replica in secondary region
resource "aws_db_instance" "secondary" {
  provider                = aws.secondary
  identifier             = "${var.project_name}-${var.environment}-secondary"
  instance_class         = "db.r5.large"
  replicate_source_db    = var.primary_db_arn
  auto_minor_version_upgrade = true
  multi_az              = true
  vpc_security_group_ids = [aws_security_group.rds_secondary.id]
  subnet_group_name      = aws_db_subnet_group.secondary.name

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# ElastiCache replication group in secondary region
resource "aws_elasticache_replication_group" "secondary" {
  provider                  = aws.secondary
  replication_group_id      = "${var.project_name}-${var.environment}-secondary"
  description              = "Secondary region cache cluster"
  node_type                = "cache.r5.large"
  num_cache_clusters       = 2
  automatic_failover_enabled = true
  multi_az_enabled         = true
  subnet_group_name        = aws_elasticache_subnet_group.secondary.name
  security_group_ids       = [aws_security_group.redis_secondary.id]

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# S3 bucket for DR backups
resource "aws_s3_bucket" "dr_backup" {
  provider = aws.secondary
  bucket   = "grayghost-dr-backup-${var.environment}"
  
  versioning {
    enabled = true
  }

  lifecycle_rule {
    enabled = true
    
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    
    expiration {
      days = 90
    }
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}
```