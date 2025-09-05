# templates_config.py

TEMPLATE_IDS = ["template_a_ministry", "template_b_step1"]

TEMPLATES = {
    "template_a_ministry": {
        "display_name": "Business Plan Template (A)",
        "sections": [
            "Executive Summary",
            "Vision/Mission Statement and Goals",
            "Company Summary",
            "Products and/or Services",
            "Market Assessment",
            "Strategic Implementation",
            "Financial Plan",
        ],
        "subsections": {
            "Vision/Mission Statement and Goals": [
                "A. Vision Statement",
                "B. Goals and Objectives",
                "C. Keys to Success",
            ],
            "Company Summary": [
                "A. Company Background",
                "B. Resources, Facilities and Equipment",
                "C. Marketing Methods",
                "D. Management and Organization",
                "E. Ownership Structure",
                "F. Social Responsibility",
                "G. Internal Analysis",
            ],
            "Market Assessment": [
                "A. Examining the General Market",
                "B. Customer Analysis",
                "C. Industry Analysis",
                "D. Strategic Alternatives",
            ],
            "Strategic Implementation": [
                "A. Production",
                "B. Resource Needs",
                "C. Sourcing/Procurement Strategy",
                "D. Marketing Strategy",
                "E. Performance Standards",
            ],
            "Financial Plan": ["A. Financial Projections", "B. Contingency Plan"],
        },
    },
    "template_b_step1": {
        "display_name": "Business Plan Template (B)",
        "sections": [
            "Cover Page",
            "Contents Page",
            "1. Introduction & Background",
            "2. Executive Summary",
            "3. Marketing Plan",
            "4. Competitor Analysis",
            "5. SWOT",
            "6. Human Resource Analysis (HR Plan)",
            "7. Key Management Controls",
            "8. Technical Review",
            "9. Production Plan",
            "10. Suppliers Analysis",
            "11. Risk Analysis",
            "12. Financial Plan",
            "13. Exit Strategy",
            "14. Conclusion and Recommendations",
            "15. Annexures",
        ],
    },
}
