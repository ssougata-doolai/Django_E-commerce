import string
import random
from . models import Order
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse

def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    the_id =  "".join(random.choice(chars) for x in range(size))
    try:
        order = Order.objects.get(order_id = the_id)
        id_generator()
    except Order.DoesNotExist:
        return the_id


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
