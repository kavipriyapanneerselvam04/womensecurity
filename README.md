# SafeHer

Full-stack software prototype with live GPS tracking, panic/fall alerts, geo-fencing, and SMS simulation/real delivery.

## Implemented
- Live location from browser GPS (with permission), shown on Leaflet map.
- Show current location button to fetch and display real coordinates on click.
- User-defined geo-fence center and radius from Geo-Fence page.
- Automatic boundary alert when user exits their own geo-fence.
- Fall detection simulation button.
- Emergency panic button.
- User registration + login pages.
- SMS sent only to parent/guardian/warden contacts linked to that specific user.
- Optional real SMS via Twilio API.
- Auto MySQL DB/table creation at backend startup.
- Light/Dark mode toggle with icon.

## Run in VS Code Terminal
```powershell
cd C:\Users\Admin\OneDrive\Desktop\miniproject\women_safety_system
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd backend
python app.py
```

Open:
- `http://127.0.0.1:5000/`
- `http://127.0.0.1:5000/register-page` (new user register)

Login:
- Name: `Admin User`
- Phone: `+910000000000`

Register:
- Create a new user from register page.
- Then login using same name + phone.

## Send SMS to Warden/Guardian
1. Register a normal user (role `user`) and login as that user.
2. Open `User Management` page.
3. Add contacts with role `Warden`, `Guardian`, or `Parent` and link them to that user.
3. Keep `Enable SMS notifications` checked.
4. Trigger `Simulate Fall` or `Emergency Panic Button`.
5. SMS goes only to that user's linked contacts.
6. Backend console prints:
   - `SMS SENT: Emergency alert with location -> ...`

## Real SMS (Optional Twilio)
Set these env vars before running backend:
```powershell
$env:SMS_PROVIDER="twilio"
$env:TWILIO_ACCOUNT_SID="ACxxxxxxxx"
$env:TWILIO_AUTH_TOKEN="xxxxxxxx"
$env:TWILIO_FROM_NUMBER="+1xxxxxxxxxx"
```

Then alerts will attempt real SMS to saved contact numbers.

## MySQL
Configured in `backend/config.py`:
- host: `localhost`
- user: `root`
- password: `ROOT`
- database: `women_safety_db`

If your MySQL password differs, update `MYSQL_PASSWORD` in `backend/config.py`.
