#!/usr/bin/env bash
# Creates the minimum Azure resources for sarthakmane.in.
# Review the estimated cost in docs/AZURE.md before running.
#
# Prerequisites: Azure CLI (`az login` done), and a subscription selected.
# Usage: bash infra/provision.sh                 # SQLite (default, ~$14/month)
#        DB_MODE=postgres bash infra/provision.sh  # + PostgreSQL (~$30/month)
set -euo pipefail

DB_MODE="${DB_MODE:-sqlite}"

LOCATION="${LOCATION:-centralindia}"
RG="${RG:-rg-sarthakmane}"
SUFFIX="${SUFFIX:-$RANDOM}"                      # keeps global names unique
APP="${APP:-sarthakmane-web-$SUFFIX}"             # -> https://$APP.azurewebsites.net
PLAN="${PLAN:-plan-sarthakmane}"
PG="${PG:-pg-sarthakmane-$SUFFIX}"
PG_ADMIN="${PG_ADMIN:-sarthakadmin}"
PG_PASSWORD="${PG_PASSWORD:-$(openssl rand -base64 24 | tr -dc 'A-Za-z0-9' | head -c 24)Aa1}"
DB_NAME="sarthakmane"
STORAGE="${STORAGE:-stsarthak$SUFFIX}"            # 3-24 lowercase letters/digits
STUDIO_PATH="${STUDIO_PATH:-studio-$(openssl rand -hex 4)}"
ADMIN_PATH="${ADMIN_PATH:-dj-$(openssl rand -hex 4)}"

echo "==> Resource group"
az group create -n "$RG" -l "$LOCATION" -o none

echo "==> App Service plan (Linux, B1)"
az appservice plan create -g "$RG" -n "$PLAN" --is-linux --sku B1 -o none

echo "==> Web app (Python 3.12)"
az webapp create -g "$RG" -p "$PLAN" -n "$APP" --runtime "PYTHON:3.12" -o none
az webapp config set -g "$RG" -n "$APP" --startup-file "bash startup.sh" \
  --always-on true --http20-enabled true --min-tls-version 1.2 --ftps-state Disabled -o none
az webapp update -g "$RG" -n "$APP" --https-only true -o none
az webapp config set -g "$RG" -n "$APP" --generic-configurations '{"healthCheckPath": "/healthz"}' -o none
# Publish-profile deployments from GitHub Actions need SCM basic auth.
az resource update -g "$RG" --namespace Microsoft.Web --resource-type basicPublishingCredentialsPolicies \
  --name scm --parent "sites/$APP" --set properties.allow=true -o none

if [ "$DB_MODE" = "postgres" ]; then
  echo "==> PostgreSQL Flexible Server (Burstable B1ms, 32 GB)"
  az postgres flexible-server create -g "$RG" -n "$PG" -l "$LOCATION" \
    --tier Burstable --sku-name Standard_B1ms --storage-size 32 --version 16 \
    --admin-user "$PG_ADMIN" --admin-password "$PG_PASSWORD" \
    --public-access 0.0.0.0 --backup-retention 7 --high-availability Disabled --yes -o none
  az postgres flexible-server db create -g "$RG" -s "$PG" -d "$DB_NAME" -o none
  DATABASE_URL="postgres://$PG_ADMIN:$PG_PASSWORD@$PG.postgres.database.azure.com:5432/$DB_NAME?sslmode=require"
else
  echo "==> Database: SQLite on the app's persistent /home storage"
  DATABASE_URL="sqlite:////home/data/db.sqlite3"
fi

echo "==> Storage account for photos & videos"
az storage account create -g "$RG" -n "$STORAGE" -l "$LOCATION" --sku Standard_LRS --kind StorageV2 \
  --access-tier Hot --min-tls-version TLS1_2 --allow-blob-public-access true -o none
STORAGE_KEY=$(az storage account keys list -g "$RG" -n "$STORAGE" --query "[0].value" -o tsv)
az storage container create --account-name "$STORAGE" --account-key "$STORAGE_KEY" -n media --public-access blob -o none
# Private container for database backups; copies older than 30 days are deleted automatically.
az storage container create --account-name "$STORAGE" --account-key "$STORAGE_KEY" -n backups --public-access off -o none
az storage account management-policy create -g "$RG" --account-name "$STORAGE" -o none --policy '{
  "rules": [{"enabled": true, "name": "expire-db-backups", "type": "Lifecycle",
    "definition": {"filters": {"blobTypes": ["blockBlob"], "prefixMatch": ["backups/db/"]},
      "actions": {"baseBlob": {"delete": {"daysAfterModificationGreaterThan": 30}}}}}]}'

echo "==> App settings"
az webapp config appsettings set -g "$RG" -n "$APP" -o none --settings \
  SCM_DO_BUILD_DURING_DEPLOYMENT=true \
  DJANGO_DEBUG=0 \
  DJANGO_SECRET_KEY="$(openssl rand -base64 48 | tr -d '\n')" \
  DJANGO_ALLOWED_HOSTS="sarthakmane.in,www.sarthakmane.in" \
  SITE_URL="https://sarthakmane.in" \
  CANONICAL_HOST="sarthakmane.in" \
  STUDIO_PATH="$STUDIO_PATH" \
  DJANGO_ADMIN_PATH="$ADMIN_PATH" \
  DATABASE_URL="$DATABASE_URL" \
  AZURE_STORAGE_ACCOUNT_NAME="$STORAGE" \
  AZURE_STORAGE_ACCOUNT_KEY="$STORAGE_KEY" \
  AZURE_STORAGE_CONTAINER=media \
  AZURE_BACKUP_CONTAINER=backups

cat <<SUMMARY

Done. Keep these somewhere safe (a password manager):
  Web app:        https://$APP.azurewebsites.net
  Studio (admin): https://sarthakmane.in/$STUDIO_PATH/
  Django admin:   https://sarthakmane.in/$ADMIN_PATH/
  Database:       $DATABASE_URL

Next:
  1. GitHub repo -> Settings -> Secrets and variables -> Actions:
       variable AZURE_WEBAPP_NAME = $APP
       secret   AZURE_WEBAPP_PUBLISH_PROFILE = output of:
         az webapp deployment list-publishing-profiles -g $RG -n $APP --xml
  2. Push to main. GitHub Actions tests and deploys.
  3. Create your login (one time):
       az webapp config appsettings set -g $RG -n $APP --settings \
         DJANGO_SUPERUSER_USERNAME=sarthak DJANGO_SUPERUSER_EMAIL=you@example.com DJANGO_SUPERUSER_PASSWORD='<strong password>'
     wait for the restart, sign in at /$STUDIO_PATH/, then remove the password setting:
       az webapp config appsettings delete -g $RG -n $APP --setting-names DJANGO_SUPERUSER_PASSWORD
  4. Connect the domain: docs/DOMAIN.md
SUMMARY
