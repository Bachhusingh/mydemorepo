variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "ap-south-1"
}

variable "cluster_name" {
  description = "EKS Cluster"
  type        = string
  default     = "cicd-lab-eks"
}

variable "db_password" {
  description = "PostgreSQL master password"
  type        = string
  sensitive   = true
}