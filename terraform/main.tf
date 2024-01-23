//create vpc 
resource "aws_vpc" "main" {
    cidr_block = "10.0.0.0/16"
    instance_tenancy = "default"

    tags = {
        Name = "MainVPC"
        Who = "Terraform"
    }
}

//create public subnets
resource "aws_subnet" "public_subnets" {
    count = length(var.public_subnet_cidrs)
    vpc_id = aws_vpc.main.id
    cidr_block = element(var.public_subnet_cidrs, count.index)
    availability_zone = element(var.subnet_azs, count.index)
    map_public_ip_on_launch = true

    tags = {
        Name = "Public Subnet ${count.index + 1}"
        Who = "Terraform"
    }
}

//create private subnets
resource "aws_subnet" "private_subnets" {
    count = length(var.private_subnet_cidrs)
    vpc_id = aws_vpc.main.id
    cidr_block = element(var.private_subnet_cidrs, count.index)
    availability_zone = element(var.subnet_azs, count.index)

    tags = {
        Name = "Private Subnet ${count.index + 1}"
        Who = "Terraform"
    }
}

//create igw
resource "aws_internet_gateway" "gw" {
    vpc_id = aws_vpc.main.id

    tags = {
        Name = "MainVPC-IGW"
        Who = "Terraform"
    }
}
//create routetable for public subnets
resource "aws_route_table" "second_rtb" {
    vpc_id = aws_vpc.main.id

    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.gw.id
    }

    tags = {
        Name = "second rtb"
        Who = "Terraform"
    }
}
//connect public subnets to route table
resource "aws_route_table_association" "public_subnet_association" {
    count = length(var.public_subnet_cidrs)
    subnet_id = element(aws_subnet.public_subnets[*].id, count.index)
    route_table_id = aws_route_table.second_rtb.id

    
}

//start ec2
resource "aws_instance" "ec2_deploy" {
    ami = "ami-09024b009ae9e7adf"
    instance_type = "t2.micro"
    key_name = aws_key_pair.ssh_key_pair.key_name
    subnet_id = element(aws_subnet.public_subnets[*].id, 0)
    security_groups = [aws_security_group.public_subnet_sg.id]

    tags = {
        Name = "EC2 Instance"
        Who = "Terraform"
    }

}