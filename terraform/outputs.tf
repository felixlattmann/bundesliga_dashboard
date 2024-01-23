output "ssh_key_public" {
    value = var.ssh_pub_key
}

output "public_ip_ec2" {
    value = aws_instance.ec2_deploy.public_ip
}

output "key_name" {
    value = aws_key_pair.ssh_key_pair.key_name
}

resource "local_file" "ip_adress" {
    content = aws_instance.ec2_deploy.public_ip
    filename = "ip_address.txt"
}