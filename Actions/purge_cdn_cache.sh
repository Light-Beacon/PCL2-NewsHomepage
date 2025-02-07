token=""

service="cdn"
host="cdn.tencentcloudapi.com"
region=""
action="PurgeUrlsCache"
version="2018-06-06"
algorithm="TC3-HMAC-SHA256"
timestamp=$(date +%s)
date=$(date -u -d @$timestamp +"%Y-%m-%d")
payload="{\"Urls\":$purge_urls}"

# ************* 步骤 1：拼接规范请求串 *************
http_request_method="POST"
canonical_uri="/"
canonical_querystring=""
canonical_headers="content-type:application/json; charset=utf-8\nhost:$host\nx-tc-action:$(echo $action | awk '{print tolower($0)}')\n"
signed_headers="content-type;host;x-tc-action"
hashed_request_payload=$(echo -n "$payload" | openssl sha256 -hex | awk '{print $2}')
canonical_request="$http_request_method\n$canonical_uri\n$canonical_querystring\n$canonical_headers\n$signed_headers\n$hashed_request_payload"
echo "$canonical_request"

# ************* 步骤 2：拼接待签名字符串 *************
credential_scope="$date/$service/tc3_request"
hashed_canonical_request=$(printf "$canonical_request" | openssl sha256 -hex | awk '{print $2}')
string_to_sign="$algorithm\n$timestamp\n$credential_scope\n$hashed_canonical_request"
echo "$string_to_sign"

# ************* 步骤 3：计算签名 *************
secret_date=$(printf "$date" | openssl sha256 -hmac "TC3$secret_key" | awk '{print $2}')
echo $secret_date
secret_service=$(printf $service | openssl dgst -sha256 -mac hmac -macopt hexkey:"$secret_date" | awk '{print $2}')
echo $secret_service
secret_signing=$(printf "tc3_request" | openssl dgst -sha256 -mac hmac -macopt hexkey:"$secret_service" | awk '{print $2}')
echo $secret_signing
signature=$(printf "$string_to_sign" | openssl dgst -sha256 -mac hmac -macopt hexkey:"$secret_signing" | awk '{print $2}')
echo "$signature"

# ************* 步骤 4：拼接 Authorization *************
authorization="$algorithm Credential=$secret_id/$credential_scope, SignedHeaders=$signed_headers, Signature=$signature"
echo $authorization

# ************* 步骤 5：构造并发起请求 *************
curl -XPOST "https://$host" -d "$payload" -H "Authorization: $authorization" -H "Content-Type: application/json; charset=utf-8" -H "Host: $host" -H "X-TC-Action: $action" -H "X-TC-Timestamp: $timestamp" -H "X-TC-Version: $version" -H "X-TC-Region: $region" -H "X-TC-Token: $token"