import json
import base64
from django.views.generic import TemplateView
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
import os
from dotenv import load_dotenv
from google import genai
from google.genai.types import Part   # For inline image data

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class HomePageView(TemplateView):
    template_name = 'index.html'


def generate_response(question, image_data=None, mime_type=None):
    try:
        contents = []

        # Add image if uploaded
        if image_data and mime_type:
            contents.append(
                Part.from_bytes(data=image_data, mime_type=mime_type)
            )

        # Add the text prompt
        if question:
            contents.append(question)
        else:
            contents.append("Describe this image in detail.")

        # Generate streaming response
        response = client.models.generate_content_stream(
            model="gemini-2.5-flash",      # Good vision model on free tier
            contents=contents
        )

        for chunk in response:
            if chunk.text:
                yield chunk.text

    except Exception as e:
        error_msg = str(e).lower()
        if "quota" in error_msg or "429" in error_msg:
            yield "❌ Gemini quota exceeded. Please wait a minute."
        else:
            yield f"Error: {str(e)}"


@csrf_exempt
def answer(request):
    question = ""
    image_data = None
    mime_type = None

    if request.method == "POST":
        try:
            # Handle JSON with image (base64)
            data = json.loads(request.body)

            question = data.get("message", "")

            # Get image if sent
            if data.get("image"):
                image_b64 = data["image"].split(",")[1] if "," in data["image"] else data["image"]
                image_data = base64.b64decode(image_b64)
                mime_type = data.get("mime_type", "image/jpeg")

        except:
            pass

    if not question and not image_data:
        question = "Hello! How can I help you today?"

    return StreamingHttpResponse(
        generate_response(question, image_data, mime_type),
        content_type="text/plain"
    )