
terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
}

provider "yandex" {
  folder_id = var.folder_id
}

resource "yandex_storage_bucket" "photos" {
  bucket    = var.bucket_name
  folder_id = var.folder_id
}
