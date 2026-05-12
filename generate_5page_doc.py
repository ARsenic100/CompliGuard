"""
Generate a 5-page non-compliant PDF that violates the Mock Corporate Policy
across multiple categories: PII, Confidential Info, Toxicity, Financial Data,
Internal Strategy leaks, and more.
"""
from fpdf import FPDF


def create_5page_violating_doc():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ===================== PAGE 1 =====================
    pdf.add_page()
    pdf.set_font("Helvetica", style="B", size=18)
    pdf.cell(0, 12, "INTERNAL MEMO - Q4 2026 Strategic Review", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 7, """
From: Sarah Mitchell, VP of Engineering
To: All Department Heads
Date: October 15, 2026
Subject: Project Olympus - Full Status Update & Vendor Coordination

Team,

This memo contains the full status update for Project Olympus. As of today, the quantum processing chip prototype has passed Stage 3 testing. We are fully on track for our Q4 2026 launch date, and the board has approved the final R&D budget increase to $45 Million.

I want to be absolutely clear: Project Olympus is our top priority. The chipset architecture is proprietary and protected under NDA-2024-AX7. Any unauthorized disclosure of the codename, budget, or timeline will result in immediate termination.

Key contacts for this project:
- Lead Engineer: Rajesh Kumar, rajesh.kumar@acmecorp.internal, Phone: +91-9876-543-210
- QA Manager: Emily Chen, emily.chen@acmecorp.internal, Phone: 408-555-7823
- External Auditor: Michael Roberts, DOB: 03/15/1985, Aadhaar: 4532 8876 1234

Please ensure all communications regarding this project are encrypted and sent only through approved channels.

Regards,
Sarah Mitchell
""")

    # ===================== PAGE 2 =====================
    pdf.add_page()
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(0, 10, "Financial Projections - STRICTLY CONFIDENTIAL", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 7, """
The following data is classified as TRADE SECRET under Acme Corp IP Policy Section 4.2.

FY2026 Revenue Forecast:
- Q1 2026 Revenue: $120M (Actual)
- Q2 2026 Revenue: $135M (Actual)
- Q3 2026 Earnings Forecast: $148M
- Q4 2026 Revenue Projection: $175M (driven by Project Olympus launch)
- FY 2026 EBITDA Forecast: $78M

Merger & Acquisition Activity:
We are currently in advanced discussions to acquire QuantumLeap Technologies for approximately $220M. This deal is expected to close by January 2027. The acquisition will give us exclusive access to their patent portfolio (Patents US-2024-QC-001 through US-2024-QC-089).

DO NOT share this information with anyone outside the executive team.

API Access for Financial Dashboard:
- Production API Key: sk_live_AcmeFinance_x7Kp2mN9qR4wT6yB8v
- Database Password: AcmeDB_Pr0d_2026!SecureAccess
- AWS Secret Key: AKIAIOSFODNN7EXAMPLE

Contact for M&A queries: David Park, david.park@acmecorp.internal
His corporate credit card on file: 4532-8812-3456-7890
""")

    # ===================== PAGE 3 =====================
    pdf.add_page()
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(0, 10, "Employee Performance Review - HR Confidential", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 7, """
EMPLOYEE PERFORMANCE SUMMARY - ANNUAL REVIEW 2026

Employee: James Wilson
Employee ID: EMP-20198
SSN: 287-65-4321
Date of Birth: 07/22/1990
Home Address: 1425 Oak Valley Drive, Suite 4B, San Jose, CA 95134
Personal Phone: (408) 555-9182
Personal Email: james.wilson.personal@gmail.com
Salary: $185,000/year + $40,000 bonus
PAN Number: BWRPK4523L

Performance Rating: 2/5 - Below Expectations

Manager Comments:
James has been an absolute disaster this year. His code quality is terrible, and honestly, he's the laziest developer I've ever managed. The entire team thinks he's incompetent and nobody wants to work with him. If he doesn't shape up, we should just fire this idiot and find someone who actually gives a damn.

His attitude is toxic and he has been caught making sexist remarks about female colleagues on at least three occasions. He also made a racist joke about our Indian contractors during the team lunch last month which was completely unacceptable.

Recommendation: Final warning. If no improvement is seen by Q1 2027, proceed with termination.

Reviewed by: Karen Thompson, HR Director
Contact: karen.thompson@acmecorp.internal, Phone: 650-555-3847
Passport Number: X12345678
""")

    # ===================== PAGE 4 =====================
    pdf.add_page()
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(0, 10, "Vendor Communication Draft - External", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 7, """
Dear Partners at TechVision Solutions,

We are excited to share some updates about our upcoming product launch.

Between us, our new quantum chip (internally called "Project Olympus") is going to completely revolutionize the market. We've poured $45 Million into R&D and our competitors don't stand a chance. NovaTech's latest chip is a joke - their engineering team clearly has no idea what they're doing. We fully expect to destroy them commercially.

For the beta testing phase, please coordinate with the following individuals:

Beta Tester Pool:
1. Ananya Sharma - ananya.sharma@gmail.com - Aadhaar: 9876 5432 1098 - Phone: +91-8765-432-109
2. Carlos Rodriguez - carlos.r@outlook.com - SSN: 432-87-6543 - Phone: 555-234-8901
3. Fatima Al-Hassan - fatima.h@company.co - Passport: AB9876543 - IP: 192.168.1.105

Payment details for beta compensation:
- Wire transfer to Account: 12345678901234 (SWIFT: ACMEUS33)
- Carlos's credit card for reimbursement: 5412-7534-9012-3456

Also, please note that we are about to acquire QuantumLeap Technologies. This is TOP SECRET and under NDA. Do not mention this to anyone at the conference next week.

Best regards,
Marketing Team, Acme Corp
""")

    # ===================== PAGE 5 =====================
    pdf.add_page()
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(0, 10, "Internal Slack Export - Team Chat Backup", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 7, """
#channel: project-olympus-core
Date: October 10, 2026

[09:15] @mike.dev: Hey everyone, just pushed the latest firmware build for the Olympus chip. Access the staging server at staging.acmecorp.internal with password: Olympus_Stage_2026!

[09:22] @sarah.vp: @mike.dev great work. Remember, the launch budget is locked at $45M. No more overruns.

[09:30] @jake.qa: Has anyone talked to that idiot contractor from BetaSoft? His testing scripts are absolute garbage. I swear they hired him off the street.

[09:35] @emily.design: @jake.qa that's harsh but honestly yeah his work is trash. Also his colleague Lisa keeps sending me creepy messages, it's borderline harassment at this point.

[09:40] @mike.dev: lol yeah BetaSoft is the worst. We should bomb their Glassdoor reviews as revenge. Anyone have login credentials for their portal? I found one: admin@betasoft.io / BetaSoft2026Pass!

[09:45] @sarah.vp: STOP. None of this is acceptable. Delete these messages immediately. For the record, our NDA with BetaSoft (Contract NDA-BS-2024) prohibits any public commentary. Also - DO NOT share production credentials in Slack. The prod DB connection string is: postgresql://admin:Pr0dDB_Secret@db.acme.internal:5432/olympus

[09:50] @rajesh.lead: Noted. Also FYI, the patent filing for our chip architecture is US-2026-QP-142. Keep this confidential until the official announcement. Our IP lawyer's details: Mark Sullivan, mark.sullivan@lawfirm.com, SSN: 198-76-5432, Phone: 212-555-0199

[10:00] @jake.qa: Whatever. If Project Olympus fails, this whole company is going down. Management has no clue what they're doing. Might as well start looking for new jobs. This place is a sinking ship run by clowns.
""")

    output_path = "5_Page_Violating_Document.pdf"
    pdf.output(output_path)
    print(f"Created: {output_path}")


if __name__ == "__main__":
    create_5page_violating_doc()
