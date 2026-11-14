
variable "folder_id" {
  description = "Yandex Cloud folder ID"
  type        = string
}

variable "bucket_name" {
  description = "Object Storage bucket name"
  type        = string
}

variable "domain" {
  type = string
}

variable "cert_id" {
  type = string
}

variable "dns_zone_id" {
  description = "Full domain name of the website, e.g. photos.vvot02.itiscl.ru"
  type        = string
}
