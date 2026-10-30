# Azure: resources, cost, deployment

## What we use (and why it's the minimum)

| Resource | SKU | Why | Est. cost / month* |
|---|---|---|---|
| App Service plan (Linux) | **B1** (1 vCPU, 1.75 GB) | Cheapest tier that allows a **custom domain + free SSL**. F1 (Free) doesn't support custom domains. | ~$13 |
| Azure Database for PostgreSQL – Flexible Server | **Burstable B1ms**, 32 GB, 7-day backups | Durable database with automatic backups | ~$12.5 compute + ~$3.7 storage ≈ **$16** (**free for 12 months** on a new Azure free account: 750 h B1ms + 32 GB) |
| Storage account (Blob) | Standard LRS, Hot | Photos & videos. Survives redeploys, cheap per GB | < $1 for a few GB |
| App Service Managed Certificate | – | HTTPS for sarthakmane.in and www | Free |
| DNS | stays at GoDaddy | No Azure DNS zone needed | Free |

**Total ≈ $30/month, or ≈ $14/month while the PostgreSQL free offer lasts.**

\*Pay-as-you-go list prices, Central India / East US region, rounded. Prices vary by region and change over time, so confirm in the [Azure pricing calculator](https://azure.microsoft.com/pricing/calculator/) before creating anything. Outbound bandwidth: first 100 GB/month free.

### Cheaper still (not recommended)

Skip PostgreSQL and keep SQLite on App Service's persistent `/home` disk (**≈ $13/month total**). It works for one writer, but `/home` is a network share. SQLite on it can hit locking errors, and backups are up to you. To do it, set `DATABASE_URL=sqlite:////home/data/db.sqlite3` instead of a Postgres URL. You can move to Postgres later with `dumpdata`/`loaddata`.

### Keeping cost in check

- Set a **budget alert** (Cost Management → Budgets) at, say, $35 so you're emailed before any surprise.
- Prefer **YouTube links** for long videos. Uploaded videos are served from Blob Storage and count toward bandwidth.
- Everything sits in one resource group (`rg-sarthakmane`). Deleting that group removes all of it.

## First deployment

1. Install the [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli), run `az login`.
2. Review `infra/provision.sh` (region defaults to `centralindia`), then run it:
   ```bash
   bash infra/provision.sh
   ```
   Save the summary it prints: your private Studio URL and the DB password.
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
