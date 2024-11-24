import os

import fitz
from openai import OpenAI

class Field:
    def __init__(self, field_name, field_value, page_number, position):
        self.field_name = field_name.strip() if field_name else "Unnamed Field"
        self.field_value = field_value.strip() if field_value else ""
        self.page_number = page_number
        self.position = position  # Rectangle area of the form field
        self.reason = None  # To store the reason if the field is invalid

class PDFProcessor:
    def __init__(self, pdf_path, output_pdf_path, openai_api_key):
        self.pdf_path = pdf_path
        self.output_pdf_path = output_pdf_path
        self.fields = []
        self.anomalous_fields = []
        # Instantiate the OpenAI client with your API key
        print(openai_api_key)
        self.client = OpenAI(api_key=openai_api_key)

    def extract_fields(self):
        """
        Extracts all fillable form fields from a PDF and retrieves their positions.
        """
        pdf_document = fitz.open(self.pdf_path)

        for page_number in range(len(pdf_document)):
            page = pdf_document[page_number]
            widgets = page.widgets()  # Retrieves form fields (widgets) on the page

            if not widgets:
                continue  # Skip pages without form fields

            for widget in widgets:
                field_name = widget.field_name  # Name of the form field
                field_value = widget.field_value  # Value of the form field
                rect = widget.rect  # Rectangle area of the form field

                field = Field(
                    field_name=field_name,
                    field_value=field_value,
                    page_number=page_number,
                    position=rect
                )
                self.fields.append(field)

        pdf_document.close()

    def validate_fields(self):
        """
        Validates each field's value based on its name using the OpenAI API.
        Updates the anomalous_fields list with fields that are invalid.
        """
        for field in self.fields:
            field_name = field.field_name
            field_value = field.field_value

            prompt = f"""
You are an expert data validator. Given the field name and its value, determine if the value is appropriate for the field.

Respond in the following format:
- If the value is appropriate, respond with 'Valid'.
- If the value is not appropriate, respond with 'Invalid: [Reason]', where [Reason] is a brief explanation.

Field Name: {field_name}
Field Value: {field_value}

Is the field value appropriate for the field name?
"""
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=50,
                    temperature=0,
                )
                validation = response.choices[0].message.content.strip()

                if validation.lower().startswith('valid'):
                    # Field is valid, do nothing
                    continue
                elif validation.lower().startswith('invalid'):
                    # Extract the reason
                    reason = validation.partition(':')[2].strip()
                    field.reason = reason
                    self.anomalous_fields.append(field)
                else:
                    # Unexpected response, treat as anomaly
                    field.reason = 'Validation response not understood.'
                    self.anomalous_fields.append(field)
            except Exception as e:
                print(f"Error validating field '{field_name}': {e}")
                # Optionally, treat as anomaly if validation fails
                field.reason = f"Exception occurred: {e}"
                self.anomalous_fields.append(field)

    def annotate_pdf(self):
        """
        Draws red bounding boxes around anomalous fields and saves the modified PDF.
        """
        pdf_document = fitz.open(self.pdf_path)

        for field in self.anomalous_fields:
            page_number = field.page_number
            rect = field.position
            reason = field.reason or 'No reason provided.'

            page = pdf_document[page_number]
            # Draw a red rectangle around the anomalous field
            page.draw_rect(rect, color=(1, 0, 0), width=1)
            # Optionally, add a text annotation with the reason
            annot = page.add_text_annot(rect, reason)
            annot.set_colors(stroke=(1, 0, 0))
            annot.update()

        # Save the modified PDF with red bounding boxes
        pdf_document.save(self.output_pdf_path)
        pdf_document.close()

    def process_pdf(self):
        """
        Orchestrates the PDF processing: extraction, validation, and annotation.
        """
        # Step 1: Extract all fields from the PDF
        self.extract_fields()
        if not self.fields:
            print("No fields found in the PDF.")
            return

        print(f"Found {len(self.fields)} fields. Validating with OpenAI API...")

        # Step 2: Validate fields with OpenAI
        self.validate_fields()
        print(f"Detected {len(self.anomalous_fields)} anomalous fields.")

        # Step 3: Draw red bounding boxes around anomalous fields
        self.annotate_pdf()
        print(f"Anomalies have been highlighted in '{self.output_pdf_path}'.")

        # Optionally, print the anomalies with reasons
        for field in self.anomalous_fields:
            print(f"Page {field.page_number + 1}, Field '{field.field_name}': {field.reason}")

if __name__ == "__main__":
    # Path to the PDF
    pdf_path = "new.pdf"
    output_pdf_path = "new_with_anomalies.pdf"
    openai_api_key = os.environ.get("OPENAI_API")

    # Instantiate the PDFProcessor
    processor = PDFProcessor(pdf_path, output_pdf_path, openai_api_key)
    # Process the PDF
    processor.process_pdf()
