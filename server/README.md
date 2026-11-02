# Direct enquiry delivery

The static website stays on GitHub Pages. Deploy `enquiry.php` to the dedicated `forms.koreacentralasia.com` document root on the existing hosting service.

The handler requires a private `kcap-form-private/config.php` directory beside the document root, outside all public roots; directory permissions 0700, config permissions 0600. Configuration keys: enabled, consent_version, state_dir, rate_key (generated on the server), published_project_ids. Never commit real configuration or runtime state.

HTTPS is mandatory. Keep `content/release.json` form_delivery_connected false until the certificate is valid, the applicable privacy and transfer notices are complete, and both recipient inboxes have been tested. Only then enable the flag and rebuild.

Recipient routing: general to info@koreacentralasia.com; project enquiries to project@koreacentralasia.com. The server chooses the recipient. A 202 response means mail transport acceptance, not confirmed inbox delivery.
