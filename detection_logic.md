## Baseline Behavior

- Normal login hours: 9 AM – 6 PM
- Typical region: ap-south-1
- Request frequency: low (1–5 per minute)

---

## Detection Rules (v1)

- Off-hours login → +2
- New IP/region → +3
- High frequency (>10/min) → +3
- Sensitive action → +4
- Failed attempt → +2

---

## Sensitive Actions

- DeleteBucket
- PutBucketPolicy
- CreateUser
- AttachRolePolicy

---

## Data Format

{
  user,
  ip,
  region,
  hour,
  action,
  is_failed
}