import json
import boto3
import os
import uuid
from datetime import datetime, timezone

sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')

behavior_table = dynamodb.Table('UserBehaviorTable')
alert_table = dynamodb.Table('AlertHistoryTable')


def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    detail = event.get("detail", {})
    identity = detail.get("userIdentity", {})

    print("IDENTITY:", identity)

    # Ignore AWS internal events
    if identity.get("type") == "AWSService":
        print("Ignoring AWS internal event")
        return {"status": "ignored"}

    # Extract user
    user = identity.get("userName") or identity.get("arn", "unknown")

    ip = detail.get("sourceIPAddress", "unknown")
    event_time = detail.get("eventTime", "")
    action = detail.get("eventName", "")

    hour = extract_hour(event_time)

    print(f"User: {user}, IP: {ip}, Hour: {hour}, Action: {action}")

    # Fetch existing behavior
    response = behavior_table.get_item(Key={'user_id': user})
    existing = response.get('Item')

    score = 0
    reasons = []

    if existing:
        print("Existing user found:", existing)

        # IP anomaly
        if existing.get('last_ip') != ip:
            score += 3
            reasons.append("New IP detected")

        # Time anomaly
        if hour is not None and abs(existing.get('last_hour', hour) - hour) > 5:
            score += 2
            reasons.append("Unusual access time")

        # Frequency anomaly
        prev_time = existing.get('last_seen_time')
        prev_count = int(existing.get('request_count', 1))

        if prev_time:
            diff = time_diff_seconds(prev_time, event_time)
            print("Time difference:", diff)

            if diff is not None and diff < 60:
                prev_count += 1
            else:
                prev_count = 1
        else:
            prev_count = 1

        print("Request count:", prev_count)

        if prev_count >= 5:
            score += 3
            reasons.append("High frequency activity")

    else:
        print("New user detected, creating baseline")
        prev_count = 1

    # Update behavior table
    behavior_table.put_item(
        Item={
            'user_id': user,
            'last_ip': ip,
            'last_hour': hour,
            'last_seen_time': event_time,
            'request_count': prev_count
        }
    )

    print("Updated UserBehaviorTable")

    # Severity logic
    severity = "LOW"
    if score >= 3:
        severity = "MEDIUM"
    if score >= 6:
        severity = "HIGH"

    if len(reasons) >= 2:
        score += 2
        reasons.append("Multiple anomaly signals")

    print(f"Score: {score}, Severity: {severity}, Reasons: {reasons}")

    # 🚨 IF ALERT → store + send
    if score >= 2:
        store_alert(user, action, ip, score, severity, reasons, event_time)
        send_alert(user, action, ip, score, severity, reasons)

    return {"status": "processed"}


# ------------------------
# STORE ALERT (NEW 🔥)
# ------------------------
def store_alert(user, action, ip, score, severity, reasons, event_time):
    alert_id = str(uuid.uuid4())

    alert_table.put_item(
        Item={
            'alert_id': alert_id,
            'user': user,
            'action': action,
            'ip': ip,
            'score': score,
            'severity': severity,
            'reasons': reasons,
            'timestamp': event_time
        }
    )

    print("Alert stored in DynamoDB:", alert_id)


# ------------------------
# HELPERS
# ------------------------
def extract_hour(event_time):
    try:
        dt = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%SZ")
        return dt.hour
    except:
        return None


def time_diff_seconds(t1, t2):
    try:
        dt1 = datetime.strptime(t1, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        dt2 = datetime.strptime(t2, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return abs((dt2 - dt1).total_seconds())
    except:
        return None


def send_alert(user, action, ip, score, severity, reasons):
    topic_arn = os.environ['SNS_TOPIC_ARN']

    message = f"""
🚨 Sentinel Zero Alert

User: {user}
Action: {action}
IP: {ip}

Risk Score: {score}
Severity: {severity}

Reasons: {', '.join(reasons)}
"""

    sns.publish(
        TopicArn=topic_arn,
        Subject=f"[{severity}] Suspicious Activity",
        Message=message
    )