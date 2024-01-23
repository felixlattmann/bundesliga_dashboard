variable "ssh_pub_key" {
    type = string
    description = "The ssh_key to use for the EC2 instance"
}

variable "aws_region" {
    type = string
    description = "Defines in what region to deploy (default: eu-central-1)"
    default = "eu-central-1"
}

variable "public_subnet_cidrs" {
    type = list(string)
    description = "CIDR values for 2 public subnets"
    default = ["10.0.1.0/24", "10.0.2.0/24"]
} 

variable "private_subnet_cidrs" {
    type = list(string)
    description = "CIDR values for 2 private subnets"
    default = ["10.0.3.0/24", "10.0.4.0/24"]
} 

variable "subnet_azs" {
    type = list(string)
    description = "Availability zones in which to deploy the subnets"
    default = ["eu-central-1a", "eu-central-1b"]
}