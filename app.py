import streamlit as st
import json
from google import genai
import textwrap
from pathlib import Path

from knowledge_base import retrieve_policies

# PAGE CONFIGURATION

st.set_page_config(
    page_title="ResolveAI",
    page_icon="✦",
    layout="wide"
)

# LOAD CUSTOM CSS

css_path = Path(__file__).parent / "style.css"

with open(css_path, "r", encoding="utf-8") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

# GEMINI CLIENT

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


MODEL = "gemini-3.8-flash"


# MOCK BUSINESS DATABASE


ORDERS = {

    "ORD1001": {
        "customer": "Ananya",
        "product": "Wireless Headphones",
        "price": 2999,
        "order_date": "2026-09-01",
        "delivery_date": "2026-09-05",
        "status": "Delivered",
        "days_since_delivery": 13
    },

    "ORD1002": {
        "customer": "Rahul",
        "product": "Laptop",
        "price": 65000,
        "order_date": "2026-09-10",
        "delivery_date": "2026-09-15",
        "status": "Delayed",
        "days_since_delivery": 3
    },

    "ORD1003": {
        "customer": "Priya",
        "product": "Smartphone",
        "price": 28000,
        "order_date": "2026-08-20",
        "delivery_date": "2026-08-25",
        "status": "Delivered",
        "days_since_delivery": 24
    }
}

# AGENT TOOL 1 — ORDER LOOKUP


def check_order(order_id):

    order_id = order_id.strip().upper()

    if order_id in ORDERS:

        return {
            "found": True,
            "order_id": order_id,
            **ORDERS[order_id]
        }

    return {
        "found": False,
        "order_id": order_id,
        "message": "Order not found in the business database."
    }


# AGENT TOOL 2 — REFUND ELIGIBILITY


def check_refund_eligibility(order):

    if not order.get("found"):

        return {
            "eligible": False,
            "reason": "Order information unavailable."
        }

    days = order["days_since_delivery"]

    if days <= 15:

        return {
            "eligible": True,
            "reason": "Order is within the standard 15-day refund window."
        }

    return {
        "eligible": False,
        "reason": "Order is outside the standard 15-day refund window."
    }

# AGENT TOOL 3 — ESCALATION

def determine_escalation(priority, category):

    priority = priority.lower()
    category = category.lower()

    if priority == "high":

        return {
            "escalate": True,
            "department": "Customer Support Manager",
            "reason": "High-priority complaint."
        }

    if category in [
        "delivery",
        "payment",
        "technical",
        "fraud"
    ]:

        return {
            "escalate": True,
            "department": "Relevant Department",
            "reason": f"{category.title()} issue requires department review."
        }

    return {
        "escalate": False,
        "department": "Customer Support",
        "reason": "Standard support workflow."
    }

# LLM CALL FUNCTION

def ask_gemini(prompt):

    try:

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )

        return json.loads(response.text)

    except Exception as e:

        st.error(f"Gemini API error: {e}")

        return None

# AGENT STEP 1 — TRIAGE


def triage_complaint(complaint):

    text = complaint.lower()

    if any(word in text for word in ["delivery", "delayed", "delay", "arrive", "shipping", "shipment"]):
        category = "delivery"
        intent = "complaint about delayed delivery"
    elif any(word in text for word in ["refund", "return", "money", "cancel"]):
        category = "refund"
        intent = "request for refund or return"
    elif any(word in text for word in ["broken", "defective", "damage", "not working", "warranty"]):
        category = "technical"
        intent = "complaint about defective product"
    else:
        category = "general"
        intent = "general customer complaint"

    if any(word in text for word in ["urgent", "urgently", "immediately", "asap"]):
        priority = "High"
    elif any(word in text for word in ["delay", "delayed", "problem", "issue"]):
        priority = "Medium"
    else:
        priority = "Low"

    if any(word in text for word in ["angry", "frustrated", "terrible", "unacceptable"]):
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return {
        "category": category,
        "intent": intent,
        "sentiment": sentiment,
        "priority": priority,
        "issue_summary": complaint[:150]
    }

# AGENT STEP 2 — DECISION


def make_business_decision(
    complaint,
    customer_type,
    triage,
    policies,
    order,
    refund,
    escalation
):

    policy_text = "\n\n".join(
        [
            f"{p['title']}:\n{p['content']}"
            for p in policies
        ]
    )

    prompt = f"""
You are the DECISION AGENT of ResolveAI.

Your responsibility is to decide the correct business
action for a customer complaint.

CUSTOMER TYPE:
{customer_type}

CUSTOMER COMPLAINT:
{complaint}

TRIAGE RESULT:
{json.dumps(triage, indent=2)}

ORDER DATA:
{json.dumps(order, indent=2)}

REFUND CHECK:
{json.dumps(refund, indent=2)}

ESCALATION CHECK:
{json.dumps(escalation, indent=2)}

RELEVANT COMPANY POLICIES:
{policy_text}

Use ONLY the supplied company policies and business data.

Do not invent policies.

Decide:

1. recommended_action
2. reasoning
3. customer_response
4. internal_note

The customer response must be professional,
empathetic and concise.

The internal note should explain what the support
employee should do next.

Return ONLY valid JSON:

{{
    "recommended_action": "...",
    "reasoning": "...",
    "customer_response": "...",
    "internal_note": "..."
}}
"""

    result = ask_gemini(prompt)

    if result is not None:
        return result

    # Fallback decision if Gemini is temporarily unavailable
    if escalation["escalate"]:
        action = f"Escalate to {escalation['department']}"
    elif order.get("status") == "Delayed":
        action = "Escalate delayed order to logistics"
    elif refund["eligible"]:
        action = "Approve refund"
    else:
        action = "Provide standard customer support"

    return {
        "recommended_action": action,
        "reasoning": (
            f"Fallback decision based on business tools and company policies. "
            f"{escalation['reason']}"
        ),
        "customer_response": (
            f"We're sorry for the inconvenience. Your complaint has been reviewed "
            f"and your case will be handled through the appropriate support process. "
            f"As a {customer_type.lower()} customer, your case has been given priority."
        ),
        "internal_note": (
            f"Follow the recommended action: {action}. "
            f"Review the retrieved company policies and business-tool results."
        )
    }

# COMPLETE AGENT WORKFLOW


def run_agent(complaint, customer_type, order_id):

    activity_log = []

    # Step 1: Complaint triage
    activity_log.append("✓ Complaint received")
    triage = triage_complaint(complaint)

    activity_log.append(
        f"✓ Complaint categorized as {triage['category'].title()}"
    )

    activity_log.append(
        f"✓ Priority determined: {triage['priority']}"
    )

    # Step 2: RAG policy retrieval
    policies = retrieve_policies(complaint)

    for policy in policies:
        activity_log.append(
            f"✓ Retrieved policy: {policy['title']}"
        )

    # Step 3: Order lookup tool
    order = check_order(order_id)

    if order["found"]:
        activity_log.append(
            f"✓ Order {order_id.upper()} found in business database"
        )
    else:
        activity_log.append(
            f"✗ Order {order_id.upper()} not found"
        )

    # Step 4: Refund eligibility tool
        # Step 4: Refund eligibility tool

    if triage["category"] == "refund":

        refund = check_refund_eligibility(order)

        if refund["eligible"]:
            activity_log.append("✓ Refund eligibility checked: Eligible")
        else:
            activity_log.append("✓ Refund eligibility checked: Not eligible")

    else:

        refund = {
            "eligible": False,
            "reason": "Refund check not required for this complaint."
        }

        activity_log.append("✓ Refund check skipped — not a refund complaint")

    # Step 5: Escalation tool
    escalation = determine_escalation(
        triage["priority"],
        triage["category"]
    )

    if escalation["escalate"]:
        activity_log.append(
            f"✓ Escalation required: {escalation['department']}"
        )
    else:
        activity_log.append("✓ No escalation required")

    # Step 6: Final business decision
    decision = make_business_decision(
        complaint,
        customer_type,
        triage,
        policies,
        order,
        refund,
        escalation
    )

    activity_log.append("✓ Business decision generated")
    activity_log.append("✓ Customer response generated")
    activity_log.append("✓ Internal support note generated")

    return {
        "triage": triage,
        "policies": policies,
        "order": order,
        "refund": refund,
        "escalation": escalation,
        "decision": decision,
        "activity_log": activity_log
    }


# SIDEBAR

with st.sidebar:

    st.markdown(
        textwrap.dedent(
            """
            <div style="
                font-size:25px;
                font-weight:800;
                margin-bottom:5px;
            ">
                ✦ ResolveAI
            </div>

            <div style="
                color:#94a3b8;
                font-size:13px;
                margin-bottom:25px;
            ">
                AI Support Operations
            </div>
            """
        ),
        unsafe_allow_html=True
    )

    st.markdown("###  Customer Information")

    customer_type = st.selectbox(
        "Customer Type",
        [
            "Standard",
            "Premium"
        ]
    )

    order_id = st.text_input(
        "Order ID",
        value="ORD1002"
    )

    st.divider()

    st.markdown("###  Agent Capabilities")

    capabilities = [
        "LLM reasoning",
        "RAG policy retrieval",
        "Order lookup tool",
        "Refund eligibility",
        "Escalation detection",
        "Automated decision",
        "Response generation"
    ]

    for capability in capabilities:

        st.markdown(
            textwrap.dedent(
                f"""
                <div class="capability">
                    ✓ {capability}
                </div>
                """
            ),
            unsafe_allow_html=True
        )

    st.divider()

    st.markdown(
        textwrap.dedent(
            """
            <div style="
                color:#94a3b8;
                font-size:12px;
                line-height:1.6;
            ">
                ResolveAI combines AI reasoning,
                company knowledge and business tools
                to automate customer complaint resolution.
            </div>
            """
        ),
        unsafe_allow_html=True
    )


# HERO HEADER

st.markdown(
    textwrap.dedent(
        """
        <div class="hero">

        <div class="hero-title">
            ✦ ResolveAI
        </div>

        <div class="hero-subtitle">
            Intelligent Customer Complaint Resolution
        </div>

        <span class="hero-badge">
            LLM + RAG + Business Tools + Automated Decisioning
        </span>

        </div>
        """
    ),
    unsafe_allow_html=True
)

# AGENT WORKFLOW

st.markdown(
    textwrap.dedent(
        """
        <div class="section-title">
             Agent Workflow
        </div>

        <div class="section-caption">
            ResolveAI analyzes the complaint, retrieves relevant
            knowledge, checks business data and generates a resolution.
        </div>
        """
    ),
    unsafe_allow_html=True
)

workflow = st.columns(5)

workflow_data = [
    ("01", "TRIAGE", "Understand complaint"),
    ("02", "RAG", "Retrieve policies"),
    ("03", "TOOLS", "Access business data"),
    ("04", "DECISION", "Choose action"),
    ("05", "RESOLUTION", "Generate response")
]

for col, data in zip(workflow, workflow_data):

    with col:

        st.markdown(
            textwrap.dedent(
                f"""
                <div class="workflow-card">

                <div class="workflow-number">
                    STEP {data[0]}
                </div>

                <div class="workflow-title">
                    {data[1]}
                </div>

                <div class="workflow-text">
                    {data[2]}
                </div>

                </div>
                """
            ),
            unsafe_allow_html=True
        )

# COMPLAINT INPUT

st.markdown(
    textwrap.dedent(
        """
        <div class="section-title">
             Resolve a Customer Complaint
        </div>

        <div class="section-caption">
            Select a demo scenario or enter a custom complaint.
        </div>
        """
    ),
    unsafe_allow_html=True
)

examples = {

    "Delayed Delivery":
        "My laptop was supposed to arrive three days ago but it still hasn't arrived. I need it urgently.",

    "Defective Product":
        "My headphones stopped working after only a few weeks. Can I get a refund?",

    "Refund Request":
        "I bought this product more than two weeks ago and now I want to return it.",

    "Premium Customer":
        "I am a premium customer and my order is delayed. I have already contacted support twice."
}


selected_example = st.selectbox(
    "Choose a demo complaint",
    list(examples.keys())
)


complaint = st.text_area(
    "Customer Complaint",
    value=examples[selected_example],
    height=130
)

# ANALYZE BUTTON


if st.button(
    "✦  Resolve Complaint",
    type="primary",
    use_container_width=True
):

    if not complaint.strip():

        st.warning(
            "Please enter a customer complaint."
        )

    else:

        with st.spinner(
            "ResolveAI is analyzing the complaint..."
        ):

            try:

                result = run_agent(
                    complaint,
                    customer_type,
                    order_id
                )

                st.session_state["result"] = result

            except Exception as e:

                st.error(
                    f"Agent Error: {str(e)}"
                )

# DISPLAY RESULTS

if "result" in st.session_state:

    result = st.session_state["result"]

    st.divider()

    # AGENT ACTIVITY


    st.markdown(
        textwrap.dedent(
            """
            <div class="section-title">
                 Agent Activity
            </div>
            """
        ),
        unsafe_allow_html=True
    )

    activity_html = ""

    for activity in result["activity_log"]:

        activity_html += (
            f'<div class="activity-item">{activity}</div>'
        )

    st.markdown(
        f'<div class="activity-box">'
        f'<div style="font-size:17px; font-weight:700; margin-bottom:10px; color:white;">'
        f'Live Resolution Pipeline'
        f'</div>'
        f'{activity_html}'
        f'</div>',
        unsafe_allow_html=True
    )


    # RESULTS


    st.markdown(
        textwrap.dedent(
            """
            <div class="section-title">
                 Resolution Results
            </div>
            """
        ),
        unsafe_allow_html=True
    )

    # TRIAGE


    triage = result["triage"]

    st.markdown(
        textwrap.dedent(
            """
            <div class="section-caption">
                Complaint analysis and priority assessment
            </div>
            """
        ),
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "CATEGORY",
        triage["category"].upper()
    )

    intent = triage["intent"]

    if "delivery" in intent.lower():
        intent = "Delayed Delivery"
    elif "refund" in intent.lower():
        intent = "Refund Request"
    elif "defective" in intent.lower():
        intent = "Defective Product"
    elif "return" in intent.lower():
        intent = "Product Return"

    col2.metric(
        "INTENT",
        intent
    )

    col3.metric(
        "SENTIMENT",
        triage["sentiment"]
    )

    col4.metric(
        "PRIORITY",
        triage["priority"].upper()
    )

    st.info(
        f" {triage['issue_summary']}"
    )

    # ORDER DATA

    st.markdown(
        textwrap.dedent(
            """
            <div class="section-title">
                 Business Data
            </div>
            """
        ),
        unsafe_allow_html=True
    )

    order = result["order"]

    if order["found"]:

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "PRODUCT",
            order["product"]
        )

        col2.metric(
            "ORDER VALUE",
            f"₹{order['price']}"
        )

        col3.metric(
            "STATUS",
            order["status"]
        )

        col4.metric(
            "ORDER ID",
            order["order_id"]
        )

    else:

        st.warning(
            order["message"]
        )

    # RAG

    st.markdown(
        textwrap.dedent(
            """
            <div class="section-title">
                 Retrieved Knowledge
            </div>

            <div class="section-caption">
                Company policies retrieved by the RAG layer
            </div>
            """
        ),
        unsafe_allow_html=True
    )

    policies = result["policies"]

    if policies:

        for policy in policies:

            with st.expander(
                f" {policy['title']}"
            ):

                st.write(
                    policy["content"]
                )

    else:

        st.warning(
            "No relevant company policy was retrieved."
        )

    # BUSINESS CHECKS

    st.markdown(
        textwrap.dedent(
            """
            <div class="section-title">
                 Business Checks
            </div>
            """
        ),
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        if result["refund"]["eligible"]:

            st.success(
                " Refund Eligible"
            )

        else:

            st.warning(
                " Refund Not Eligible"
            )

        st.caption(
            result["refund"]["reason"]
        )

    with col2:

        if result["escalation"]["escalate"]:

            st.error(
                " Escalation Required"
            )

        else:

            st.success(
                " Standard Support Workflow"
            )

        st.caption(
            result["escalation"]["reason"]
        )

    # FINAL DECISION

    st.markdown(
        textwrap.dedent(
            """
            <div class="section-title">
                 AI Business Decision
            </div>
            """
        ),
        unsafe_allow_html=True
    )

    decision = result["decision"]

    st.markdown(
        textwrap.dedent(
            f"""
            <div class="decision-card">

            <div class="decision-label">
                Recommended Action
            </div>

            <div class="decision-value">
                {decision['recommended_action']}
            </div>

            </div>
            """
        ),
        unsafe_allow_html=True
    )

    with st.expander(
        " View Decision Reasoning"
    ):

        st.write(
            decision["reasoning"]
        )

    # CUSTOMER RESPONSE


    st.markdown(
        textwrap.dedent(
            """
            <div class="section-title">
                 Customer Response
            </div>

            <div class="section-caption">
                AI-generated response ready for the customer
            </div>
            """
        ),
        unsafe_allow_html=True
    )

    st.text_area(
        "Generated Response",
        value=decision["customer_response"],
        height=160
    )

    # INTERNAL NOTE

    st.markdown(
        textwrap.dedent(
            """
            <div class="section-title">
                 Internal Support Note
            </div>

            <div class="section-caption">
                Guidance for the support team
            </div>
            """
        ),
        unsafe_allow_html=True
    )

    st.text_area(
        "Internal Note",
        value=decision["internal_note"],
        height=130
    )


    # COMPLETE

    st.markdown(
        textwrap.dedent(
            """
            <div style="
                margin-top:25px;
            padding:18px;
            border-radius:16px;
            background:#ecfdf5;
            border:1px solid #a7f3d0;
            color:#065f46;
            font-weight:650;
            text-align:center;
            ">
            ✓ ResolveAI completed the complaint resolution workflow
            </div>
            """
        ),
        unsafe_allow_html=True
    )