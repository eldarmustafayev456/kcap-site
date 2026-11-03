# Direct enquiry delivery

The static website stays on GitHub Pages. Deploy `enquiry.php` to the dedicated `forms.koreacentralasia.com` document root on the existing hosting service.

The handler requires a private `kcap-form-private/config.php` directory beside the document root, outside all public roots; directory permissions 0700, config permissions 0600. Configuration keys: enabled, consent_version, state_dir, rate_key (generated on the server), published_project_ids. Never commit real configuration or runtime state.

HTTPS is mandatory. Keep `content/release.json` form_delivery_connected false until the certificate is valid, the applicable privacy and transfer notices are complete, and both recipient inboxes have been tested. Only then enable the flag and rebuild.

Recipient routing: general to info@koreacentralasia.com; project enquiries to project@koreacentralasia.com. The server chooses the recipient. A 202 response means mail transport acceptance, not confirmed inbox delivery.

## SMTP

The handler uses PHPMailer with authenticated SMTPS, host `mail.koreacentralasia.com`, port 465, username `info@koreacentralasia.com`, and certificate verification enabled. The existing host disables PHP mail().

Install dependencies in the private `kcap-form-private` directory using `composer.json`. Add `smtp` to the private config with host, port and username. The password is read separately from the private `smtp-password.txt` file, permissions 0600, in a 0700 directory outside all web document roots. The account holder enters it directly on the server. Never publish, log, screenshot or return its contents.

Only verify whether the credential file is present/non-empty; do not read it back in tools. SMTP errors are returned as generic delivery failures. Test both recipient inboxes before public activation.
