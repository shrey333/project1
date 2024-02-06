import os
import csv
from io import BytesIO
import pandas as pd

from django.conf import settings
from django.http import HttpResponse
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView


class ImageView(APIView):
    parser_classes = (MultiPartParser,)
    csv_data = None  # Class variable to store CSV data

    @classmethod
    def load_csv_data(cls):
        if cls.csv_data is None:
            # Load images.csv into a DataFrame and store it in the class variable
            csv_path = os.path.join(settings.BASE_DIR, "server/static/dataset.csv")
            cls.csv_data = pd.read_csv(csv_path)

    def post(self, request, *args, **kwargs):
        file_obj = request.data["inputFile"]

        # Get filename from the uploaded file
        filename, _ = os.path.splitext(file_obj.name)

        # Load CSV data if not already loaded
        self.load_csv_data()

        # Search for the filename in the DataFrame and retrieve the associated value
        try:
            value = self.csv_data.loc[
                self.csv_data["Image"] == filename, "Results"
            ].values[0]
        except IndexError:
            return Response({"error": "Filename not found in images.csv"}, status=400)

        # Construct the plain text response
        response_text = f"{filename}:{value}"
        return HttpResponse(response_text, content_type="text/plain")
