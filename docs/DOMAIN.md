# Connecting sarthakmane.in (GoDaddy) to Azure

Keep the domain registered and its DNS hosted at GoDaddy; only a few records change.

## 1. Start in Azure

Azure Portal → your App Service → **Custom domains** → **Add custom domain**:

- Domain provider: **All other domain services**
- TLS/SSL certificate: **App Service Managed Certificate** (free)
- Domain: `sarthakmane.in`

Azure shows two values. Keep the page open:
- an **A record** IP address
- a **TXT** record named `asuid` with a long verification ID

## 2. Add records in GoDaddy

GoDaddy → My Products → `sarthakmane.in` → **DNS** → **DNS Records**:

| Type | Name | Value | Notes |
|---|---|---|---|
| A | `@` | *IP from Azure* | **Edit** the existing `@` A record (often "Parked"). Don't add a second one. |
| TXT | `asuid` | *verification ID from Azure* | Proves you own the domain |
| CNAME | `www` | `<your-app>.azurewebsites.net` | Edit the existing `www` CNAME if there is one |
| TXT | `asuid.www` | *same verification ID* | For the www domain |

Remove any GoDaddy **forwarding** set up for the domain, since it overrides these records.

## 3. Finish in Azure

Back on the Add custom domain page, click **Validate**, then **Add**. DNS changes usually show up within minutes but can take up to 48 hours. Azure then issues and binds the free certificate automatically.

Repeat *Add custom domain* for `www.sarthakmane.in`. The app redirects `www` to `sarthakmane.in` through the `CANONICAL_HOST` setting.

## 4. Check

- https://sarthakmane.in loads with a padlock
- https://www.sarthakmane.in redirects to it
- The `DJANGO_ALLOWED_HOSTS` app setting contains both names. The provisioning script sets this.
