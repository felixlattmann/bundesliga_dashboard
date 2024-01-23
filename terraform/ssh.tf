resource "random_pet" "ssh_key_name" {
    prefix = "ssh"
    separator = "-"
}
resource "aws_key_pair" "ssh_key_pair" {
    key_name = random_pet.ssh_key_name.id
    public_key = var.ssh_pub_key
}