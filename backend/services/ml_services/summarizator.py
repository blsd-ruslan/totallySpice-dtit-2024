import os
from io import BytesIO

import fitz
from openai import OpenAI
import json

from services.minio_service import get_file_from_minio
from utils.environment_variables import OPEN_API_KEY


class Field:
    def __init__(self, field_name, field_value, page_number, position):
        self.field_name = field_name.strip() if field_name else "Unnamed Field"
        self.field_value = field_value.strip() if field_value else ""
        self.page_number = page_number
        self.position = position  # Rectangle area of the form field
        self.reason = None  # To store the reason if the field is invalid


class PDFProcessor:
    def __init__(self, pdf_path, output_pdf_path):
        self.pdf_path = pdf_path
        self.output_pdf_path = output_pdf_path
        self.fields = []
        self.anomalous_fields = []
        self.knowledge_base = []
        self.client = OpenAI(api_key=OPEN_API_KEY)

    def open_file(self):
        file_data = get_file_from_minio(self.pdf_path)
        pdf_data = BytesIO(file_data)
        pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
        return pdf_document

    def extract_fields(self):
        self.fields = []
        # file_data = get_file_from_minio(self.pdf_path)
        # pdf_data = BytesIO(file_data)
        pdf_document = self.open_file()

        for page_number in range(len(pdf_document)):
            page = pdf_document[page_number]
            widgets = page.widgets()

            if not widgets:
                continue

            for widget in widgets:
                field_name = widget.field_name
                field_value = widget.field_value
                rect = widget.rect

                field = Field(
                    field_name=field_name,
                    field_value=field_value,
                    page_number=page_number,
                    position=rect
                )
                self.fields.append(field)

        pdf_document.close()

    def validate_fields(self):
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
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=50,
                    temperature=0,
                )
                validation = response.choices[0].message.content.strip()

                if validation.lower().startswith('valid'):
                    continue
                elif validation.lower().startswith('invalid'):
                    reason = validation.partition(':')[2].strip()
                    field.reason = reason
                    self.anomalous_fields.append(field)
                    self.knowledge_base.append({
                        "field_name": field_name,
                        "field_value": field_value,
                        "reason": reason,
                        # "coordinates": {
                        #     "x0": field.position.x0,
                        #     "y0": field.position.y0,
                        #     "x1": field.position.x1,
                        #     "y1": field.position.y1,
                        # },
                        "page_number": field.page_number + 1  # Convert to 1-based index
                    })
                else:
                    field.reason = 'Validation response not understood.'
                    self.anomalous_fields.append(field)
            except Exception as e:
                print(f"Error validating field '{field_name}': {e}")
                field.reason = f"Exception occurred: {e}"
                self.anomalous_fields.append(field)

    def annotate_pdf(self):
        pdf_document = self.open_file()

        for field in self.anomalous_fields:
            page_number = field.page_number
            rect = field.position
            reason = field.reason or 'No reason provided.'

            page = pdf_document[page_number]
            page.draw_rect(rect, color=(1, 0, 0), width=1)
            annot = page.add_text_annot(rect, reason)
            annot.set_colors(stroke=(1, 0, 0))
            annot.update()

        pdf_document.save(self.output_pdf_path)
        pdf_document.close()

    def save_knowledge_base(self, path="services/ml_services/docs/knowledge_base.json"):
        with open(path, "w") as f:
            json.dump(self.knowledge_base, f, indent=4)

    def process_pdf(self):
        self.extract_fields()
        if not self.fields:
            print("No fields found in the PDF.")
            return

        print(f"Found {len(self.fields)} fields. Validating with OpenAI API...")

        self.validate_fields()
        print(f"Detected {len(self.anomalous_fields)} anomalous fields.")

        self.annotate_pdf()
        print(f"Anomalies have been highlighted in '{self.output_pdf_path}'.")

        self.save_knowledge_base()
        print(f"Knowledge base saved to 'services/ml_services/docs/knowledge_base.json'.")


class ChatProcessor:
    def __init__(self, knowledge_base_path):
        self.knowledge_base_path = knowledge_base_path
        self.client = OpenAI(api_key=OPEN_API_KEY)
        self.load_knowledge_base()
        self.sessions = {}  # To store conversation history for each session

    def load_knowledge_base(self):
        try:
            with open(self.knowledge_base_path, "r") as f:
                self.knowledge_base = json.load(f)
        except FileNotFoundError:
            self.knowledge_base = []
        print(self.knowledge_base)

    def get_response(self, user_query, session_id):
        if session_id not in self.sessions:
            self.sessions[session_id] = []

        # Add user query to session history
        self.sessions[session_id].append({"role": "user", "content": user_query})

        # Build context from the knowledge base
        anomalies_summary = "\n".join([
            f"- Field '{item['field_name']}' on page {item['page_number']}: {item['reason']}"
            for item in self.knowledge_base
        ])

        context = f"""
    The following anomalies were detected in the document:
    {anomalies_summary}

    User Query: {user_query}

    Respond to the query using the context above.
    """
        # Add the context as a system message at the start of the session
        if len(self.sessions[session_id]) == 1:  # First interaction
            self.sessions[session_id].insert(0, {"role": "system", "content": context})

        try:
            # Generate response
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=self.sessions[session_id],
                max_tokens=2000,
                temperature=0.7,
            )
            assistant_response = response.choices[0].message.content.strip()

            # Add assistant response to session history
            self.sessions[session_id].append({"role": "assistant", "content": assistant_response})

            return assistant_response
        except Exception as e:
            return f"Error during chat: {e}"


if __name__ == "__main__":
    # Path to the PDF
    pdf_path = "new.pdf"
    output_pdf_path = "new_with_anomalies.pdf"
    openai_api_key = os.getenv("OPENAI_API")
    knowledge_base_path = "docs/knowledge_base.json"
    # Instantiate the PDFProcessor
    processor = PDFProcessor(pdf_path, output_pdf_path, openai_api_key)
    # Process the PDF
    processor.process_pdf()

    chat_processor = ChatProcessor(knowledge_base_path, openai_api_key)
    session_id = "user_1234"  # Unique session identifier
    print("\nStarting chat session...")

    # Step 3: Simulate user queries and assistant responses
    messages = [
        "What anomalies were found in the document?",
        "Can you explain the issue with the field 'Place of birth'?",
    ]

    for i, message in enumerate(messages):
        print(f"\nUser ({i + 1}): {message}")
        response = chat_processor.get_response(message, session_id)
        print(f"Assistant ({i + 1}): {response}")

    print("\nChat session ended.")
