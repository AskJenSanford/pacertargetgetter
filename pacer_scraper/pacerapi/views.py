from rest_framework.views import APIView
from rest_framework.response import Response
from .scraper.pacer import PacerScraper
from .scraper.pdf_data import PdfData

scraper = PacerScraper()
pdfdata = PdfData()


class CaseNumberView(APIView):
    def post(self, request):
        case_number = request.data.get('case_number')
        print(case_number)
        case_number_urls = scraper.start_driver(case_number=case_number)
        print(case_number_urls)
        pdfdata.scrape_pdf_data(case_number, case_number_urls)
        return Response({'received_case_number': case_number})
