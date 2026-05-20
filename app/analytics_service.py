from collections import Counter
from .expiry_service import expiry_status


# Builds dashboard stat cards.
def build_dashboard_stats(items):
    stats = {
        "total_entries": len(items),
        "total_quantity": sum(item.quantity for item in items),
        "expired": 0,
        "expiring_soon": 0,
        "unknown": 0
    }

    for item in items:
        status = expiry_status(item.expiration_date)

        if status == "expired":
            stats["expired"] += 1

        elif status in ["urgent", "soon"]:
            stats["expiring_soon"] += 1

        elif status == "unknown":
            stats["unknown"] += 1

    return stats


# Builds analytics page data.
def build_analytics(items, scan_logs):
    category_counter = Counter()
    expiry_counter = Counter()

    for item in items:
        status = expiry_status(item.expiration_date)
        expiry_counter[status] += item.quantity

        category = item.product.category or "Other"
        category_counter[category] += item.quantity

    total_quantity = sum(item.quantity for item in items)
    total_entries = len(items)

    expired = expiry_counter["expired"]
    urgent = expiry_counter["urgent"]
    soon = expiry_counter["soon"]
    safe = expiry_counter["safe"]
    unknown = expiry_counter["unknown"]

    expiry_risk = expired + urgent + soon

    if total_quantity == 0:
        health_score = 100
    else:
        penalty = (
            (expired * 35)
            + (urgent * 20)
            + (soon * 10)
            + (unknown * 4)
        )

        health_score = max(
            0,
            min(100, 100 - int((penalty / total_quantity)))
        )

    total_scans = len(scan_logs)
    successful_scans = len([log for log in scan_logs if log.success])
    failed_scans = total_scans - successful_scans

    if total_scans == 0:
        scan_success_rate = 0
    else:
        scan_success_rate = int(
            (successful_scans / total_scans) * 100
        )

    most_common_category = "No data"

    if category_counter:
        most_common_category = (
            category_counter.most_common(1)[0][0]
        )

    category_data = []

    if category_counter:
        highest_count = max(category_counter.values())

        for category, count in category_counter.most_common(8):
            category_data.append({
                "name": category,
                "count": count,
                "percent": int((count / highest_count) * 100)
            })

    return {
        "total_items": total_entries,
        "total_quantity": total_quantity,
        "expired": expired,
        "urgent": urgent,
        "soon": soon,
        "safe": safe,
        "unknown": unknown,
        "expiry_risk": expiry_risk,
        "health_score": health_score,
        "total_scans": total_scans,
        "successful_scans": successful_scans,
        "failed_scans": failed_scans,
        "scan_success_rate": scan_success_rate,
        "most_common_category": most_common_category,
        "category_data": category_data
    }