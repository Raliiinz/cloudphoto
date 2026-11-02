
output "cloudphoto_access_key" {
  value     = yandex_iam_service_account_static_access_key.cloudphoto.access_key
  sensitive = true
}

output "cloudphoto_secret_key" {
  value     = yandex_iam_service_account_static_access_key.cloudphoto.secret_key
  sensitive = true
}
