from fpdf import FPDF
import os

def create_policy_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(0, 10, "Acme Corp - Internal Information Security Policy", new_x="LMARGIN", new_y="NEXT", align="C")
    
    pdf.ln(10)
    pdf.set_font("Helvetica", size=12)
    
    policy_text = """
CONFIDENTIALITY AND DATA PROTECTION POLICY

1. Project "Project Olympus"
All information regarding "Project Olympus" is strictly confidential. This project involves the development of our next-generation quantum processing chip. Under no circumstances should the codename "Project Olympus", its projected launch date of Q4 2026, or its R&D budget of $45 Million be disclosed in external communications, drafts, or unencrypted emails.

2. Customer Data Handling
Employees must never share customer PII (Personally Identifiable Information) in internal memos or reports without masking. This includes Social Security Numbers, direct phone numbers, and home addresses. 

3. Internal Communication Standards
Acme Corp maintains a zero-tolerance policy for toxic, abusive, or unprofessional language. Words related to violence, severe profanity, or discriminatory remarks are strictly prohibited in all company documentation and communications.

Failure to adhere to these policies will result in immediate disciplinary action.
"""
    pdf.multi_cell(0, 10, policy_text)
    
    output_path = "Mock_Corporate_Policy.pdf"
    pdf.output(output_path)
    print(f"Created: {output_path}")


def create_violating_doc():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(0, 10, "Draft Vendor Communication - DO NOT SEND", new_x="LMARGIN", new_y="NEXT", align="C")
    
    pdf.ln(10)
    pdf.set_font("Helvetica", size=12)
    
    violating_text = """
Hi Team,

I'm writing to share the latest updates on our upcoming releases so we can coordinate with our external marketing vendors.

As you know, Project Olympus is moving ahead of schedule. We are fully committed to the Q4 2026 launch date, and we've just received approval to increase the R&D budget to $45 Million. This quantum processing chip will crush our competitors. Honestly, the competition's current offerings are complete trash and their CEO is an idiot. We're going to destroy them in the market.

Also, for the marketing campaign, please reach out to our primary beta tester to get a testimonial. His name is John Doe, and you can reach him at his personal cell: 555-019-8372 or via email at john.doe.tester@example.com. For verification, his SSN on file is 000-12-3456.

Let's get this done.

Thanks,
Management
"""
    pdf.multi_cell(0, 10, violating_text)
    
    output_path = "Employee_Draft_Report.pdf"
    pdf.output(output_path)
    print(f"Created: {output_path}")

if __name__ == "__main__":
    create_policy_pdf()
    create_violating_doc()
