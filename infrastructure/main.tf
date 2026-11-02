
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

# Service account for the cloudphoto application
resource "yandex_iam_service_account" "cloudphoto" {
  name        = "cloudphoto-sa"
  description = "Service account for cloudphoto CLI"
  folder_id   = var.folder_id
}

# Grant access to the photo archive bucket
resource "yandex_storage_bucket_iam_binding" "cloudphoto_admin" {
  bucket = yandex_storage_bucket.photos.bucket
  role   = "storage.admin"

  members = [
    "serviceAccount:${yandex_iam_service_account.cloudphoto.id}"
  ]
}

# Static access key for boto3
resource "yandex_iam_service_account_static_access_key" "cloudphoto" {
  service_account_id = yandex_iam_service_account.cloudphoto.id
  description        = "Static access key for cloudphoto CLI"

  depends_on = [
    yandex_storage_bucket_iam_binding.cloudphoto_admin
  ]
}

