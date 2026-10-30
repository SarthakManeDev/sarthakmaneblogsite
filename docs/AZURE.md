# Azure: resources, cost, deployment

## What we use (the minimum)

| Resource | SKU | Why | Est. cost / month* |
|---|---|---|---|
| App Service plan (Linux) | **B1** (1 vCPU, 1.75 GB RAM, 10 GB disk) | Cheapest tier that allows a **custom domain + free SSL**. F1 (Free) doesn't support custom domains. | ~$13 |
| Database | **SQLite** on App Service's persistent `/home` storage | No separate database server to pay for | $0 |
| Storage account (Blob) | Standard LRS, Hot | Photos & videos, plus daily-ish database backups | < $1 for a few GB |
| App Service Managed Certificate | – | HTTPS for sarthakmane.in and www | Free |
| DNS | stays at GoDaddy | No Azure DNS zone needed | Free |

**Total ≈ $13–14/month.**

\*Pay-as-you-go list prices, rounded; they vary by region and over time. Confirm in the [Azure pricing calculator](https://azure.microsoft.com/pricing/calculator/) before creating anything. Outbound bandwidth: first 100 GB/month free.

### How SQLite is made safe enough

- **Locking**: `/home` is a network share. SQLite is configured to wait up to 20 s for a lock and to take the write lock up front, so the rare overlapping write queues instead of erroring. Only you write to the site, so contention is minimal.
- **Backups**: after any change you make in the Studio (at most every 5 minutes), and on every app start, a consistent snapshot is uploaded to the private `backups` container. Copies older than 30 days are deleted automatically. Run one manually with `python manage.py backup_db`.
- **Restore**: in the Azure portal, open the storage account → `backups` container → download the snapshot you want. Then App Service → *Advanced Tools (Kudu)* → *Debug console* → upload it to `/home/data/` as `db.sqlite3` and restart the app.

### When to move to PostgreSQL (~$30/month)

Upgrade if you ever see "database is locked" errors, have several people writing, or want point-in-time restore. `DB_MODE=postgres bash infra/provision.sh` creates a Burstable B1ms server (free for 12 months on a new Azure free account). Move existing content with `python manage.py dumpdata` / `loaddata`.

### Keeping cost in check

- Set a **budget alert** (Cost Management → Budgets) at, say, $18 so you're emailed before any surprise.
- Prefer **YouTube links** for long videos. Uploaded videos are served from Blob Storage and count toward bandwidth.
- Everything sits in one resource group (`rg-sarthakmane`). Deleting that group removes all of it.

## First deployment

1. Install the [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli), run `az login`.
2. Review `infra/provision.sh` (region defaults to `centralindia`), then run it:
   ```bash
   bash infra/provision.sh
   ```
   Save the summary it prints: your private Studio URL and admin paths.
3. In the GitHub repo → *Settings → Secrets and variables → Actions*:
   - Variable `AZURE_WEBAPP_NAME` = the app name printed
   - Secret `AZURE_WEBAPP_PUBLISH_PROFILE` = output of `az webapp deployment list-publishing-profiles -g rg-sarthakmane -n <app> --xml`
4. Push to `main`. The workflow runs the tests, then deploys. Startup runs migrations and `collectstatic`.
5. Create your login once (see the provisioning summary), then sign in at `/<STUDIO_PATH>/`.
6. Connect the domain: [DOMAIN.md](DOMAIN.md).

## Day-to-day

- Every push to `main` → tested → deployed automatically.
- Logs: `az webapp log tail -g rg-sarthakmane -n <app>`.
- Settings (secrets, paths) live in *App Service → Environment variables*, never in the code.
