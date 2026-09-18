POLICIES = [
    {
        "title": "Refund Policy",
        "keywords": [
            "refund",
            "return",
            "money",
            "returning",
            "cancel"
        ],
        "content": """
Customers can request a refund within 15 days of delivery.

Products must be unused unless the product is defective.

Defective products can be refunded or replaced within the warranty period.

Refunds are normally processed within 5-7 business days.
"""
    },

    {
        "title": "Shipping Policy",
        "keywords": [
            "delivery",
            "shipping",
            "late",
            "delay",
            "delayed",
            "arrive",
            "shipment",
            "order"
        ],
        "content": """
Standard delivery takes 3-5 business days.

If an order is delayed by more than 3 business days,
the customer support team should escalate the issue to logistics.

Premium customers with delayed orders should receive priority handling.
"""
    },

    {
        "title": "Warranty Policy",
        "keywords": [
            "broken",
            "defective",
            "damage",
            "warranty",
            "not working",
            "repair",
            "replacement"
        ],
        "content": """
Electronic products have a 1-year warranty.

Manufacturing defects are covered under warranty.

Physical damage caused by the customer is not covered.

Eligible customers can receive a repair or replacement.
"""
    },

    {
        "title": "Customer Support Policy",
        "keywords": [
            "support",
            "complaint",
            "urgent",
            "priority",
            "escalate",
            "customer",
            "issue"
        ],
        "content": """
High-priority complaints should be escalated immediately.

Premium customers receive priority support.

Customers should receive a clear explanation of the resolution.

If an issue cannot be resolved by customer support,
it should be escalated to the appropriate department.
"""
    }
]


def retrieve_policies(query, top_k=2):
    """
    Lightweight RAG retrieval system.

    It finds the company policies that are most relevant
    to the customer's complaint.
    """

    query = query.lower()

    results = []

    for policy in POLICIES:

        score = 0

        for keyword in policy["keywords"]:

            if keyword in query:
                score += 1

        results.append(
            (score, policy)
        )

    results.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return [
        policy
        for score, policy in results[:top_k]
        if score > 0
    ]