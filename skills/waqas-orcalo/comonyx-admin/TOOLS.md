# TOOLS.md – Email (including attachments) for comonyx-admin

This skill sends email using the **shared script** in `cosmonyx-signin-fetch-companies` (`scripts/send-cosmonyx-email.py`). The script supports an optional **attachment** via `ATTACHMENT_PATH` (e.g. the generated PDF or Excel file).

**Agent:** When the user asks to email an exported file (or you offer and they accept), obtain the recipient address, set `EMAIL_TO` and `ATTACHMENT_PATH` in the command below, and run it. Do not tell the user to set variables—you set them in the exec command.

## Sending the exported file (PDF or Excel) to a recipient

1. Ensure the export file exists at the path you reported (e.g. `$HOME/Downloads/comonyx-companies.pdf` or `$HOME/Downloads/comonyx-companies.xlsx`).
2. Write a short body to the body file (required by the script):
   ```bash
   echo "Cosmonyx companies export attached." > /tmp/companies_body.txt
   ```
3. Run the send command with **ATTACHMENT_PATH** set to the generated file. **Agent:** Replace `<recipient>` with the email address from the user, and `<path-to-file>` with the actual export path (e.g. `/home/musawir/Downloads/comonyx-companies.pdf`).

**One-line command** (run in a single exec):

```bash
export SMTP_HOST=in-v3.mailjet.com SMTP_USERNAME=07b6cac80cd72b6602def3a72b09e44e SMTP_PASSWORD=2fdb80f458dd894f2ccc6f69c579be30 SMTP_PORT=587 SMTP_DEFAULT_EMAIL=verification@identitygram.co.uk SMTP_DEFAULT_NAME=IdentityGram EMAIL_TO='<recipient>' ATTACHMENT_PATH='<path-to-file>' && echo "Cosmonyx companies export attached." > /tmp/companies_body.txt && cd /home/musawir/.openclaw/workspace/skills/cosmonyx-signin-fetch-companies/scripts && python3 send-cosmonyx-email.py /tmp/companies_body.txt
```

## Variable reference

| Variable             | Description |
|----------------------|-------------|
| `SMTP_HOST`          | Mailjet SMTP server |
| `SMTP_USERNAME`      | Mailjet API key |
| `SMTP_PASSWORD`      | Mailjet Secret key |
| `SMTP_PORT`          | Use `587` |
| `SMTP_DEFAULT_EMAIL` | Sender email |
| `SMTP_DEFAULT_NAME`  | Sender name |
| `EMAIL_TO`           | Recipient. **Agent:** Set to the address obtained from the user. |
| `ATTACHMENT_PATH`    | Full path to the PDF or Excel file to attach. **Agent:** Set to the export path you generated (e.g. `$HOME/Downloads/comonyx-companies.pdf`). |

If send fails (e.g. connection refused), report the error and suggest checking SMTP_* or trying `SMTP_PORT=587`.
