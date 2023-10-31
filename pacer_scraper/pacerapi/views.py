import os
import shutil
import threading
from django.conf import settings
from .models import Address, Status
from rest_framework import viewsets
from .scraper.pdf_data import PdfData
from .scraper.pacer import PacerScraper
from .serializers import AddressSerializer
from rest_framework.response import Response

scraper = PacerScraper()
pdfdata = PdfData()


class CaseNumberView(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def create(self, request, **kwargs):
        case_number = request.data.get('case_number')
        check_status = Status.objects.filter(case_number=case_number).values_list("status", flat=True)
        status = None

        if "DONE" in check_status or "PROCESSING" in check_status:
            return Response({
                "message": f"{check_status[0]} {case_number}"
            })
        else:
            try:
                status = Status(case_number=case_number, status="PROCESSING")
                status.save()

                processing_thread = threading.Thread(target=self.process_request, args=(case_number,))
                processing_thread.start()

                return Response({"message": f"Processing {case_number}"})

            except Exception as e:
                if status:
                    status.delete()
                return Response({'error': f"An error occurred: {str(e)}"}, status=500)

    def process_request(self, case_number):
        try:
            case_number_urls = scraper.start_driver(case_number=case_number)
            pdfdata.scrape_pdf_data(case_number, case_number_urls)
            self.delete_folder()
            status = Status.objects.get(case_number=case_number)
            status.status = "DONE"
            status.save()

            try:
                address = Address.objects.get(case_number=case_number).address
                return Response({
                    'received_case_number': case_number,
                    'address': address,
                })
            except Address.DoesNotExist:
                return Response({'received_case_number': case_number, 'address': 'Address not found'})
        except Exception as e:
            if status:
                status.delete()
            return Response({'error': f"An error occurred: {str(e)}"}, status=500)

    def delete_folder(self):
        folder_path = os.path.join(settings.BASE_DIR, "casepdf")
        shutil.rmtree(folder_path)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        case_number = instance.case_number

        try:
            status = Status.objects.get(case_number=case_number)
        except Status.DoesNotExist:
            return Response({'message': 'Status not found'}, status=status.HTTP_404_NOT_FOUND)

        status.delete()
        instance.delete()

        return Response({'message': 'Address and status deleted'})
