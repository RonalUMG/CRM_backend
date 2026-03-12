from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError

from admissions.models import HighSchool
from commercial.models import AcademicOffer
from .models import Campus, Lead, Product, Site


def landing(request):
    context = {
        "total_campus": Campus.objects.count(),
        "total_programs": Product.objects.filter(active=True).count(),
        "total_offers": AcademicOffer.objects.count(),
        "programs": Product.objects.filter(active=True).order_by("name")[:12],
        "campuses": Campus.objects.order_by("name"),
        "sites": Site.objects.select_related("campus").order_by("name"),
        "high_schools": HighSchool.objects.filter(active=True).order_by("name"),
    }
    return render(request, "public/landing.html", context)


def apply(request):
    if request.method != "POST":
        return redirect("public_landing")

    data = request.POST
    lead = Lead(
        name=(data.get("name") or "").strip(),
        email=(data.get("email") or "").strip(),
        phone=(data.get("phone") or "").strip(),
        message=(data.get("message") or "").strip(),
    )

    campus_id = data.get("preferred_campus") or None
    site_id = data.get("preferred_site") or None
    high_school_id = data.get("high_school") or None

    if campus_id:
        lead.preferred_campus_id = campus_id
    if site_id:
        lead.preferred_site_id = site_id
    if high_school_id:
        lead.high_school_id = high_school_id

    try:
        lead.save()
    except ValidationError as exc:
        context = {
            "errors": exc.message_dict if hasattr(exc, "message_dict") else {"form": [str(exc)]},
            "form": data,
            "total_campus": Campus.objects.count(),
            "total_programs": Product.objects.filter(active=True).count(),
            "total_offers": AcademicOffer.objects.count(),
            "programs": Product.objects.filter(active=True).order_by("name")[:12],
            "campuses": Campus.objects.order_by("name"),
            "sites": Site.objects.select_related("campus").order_by("name"),
            "high_schools": HighSchool.objects.filter(active=True).order_by("name"),
        }
        return render(request, "public/landing.html", context, status=400)

    return redirect("public_thanks")


def thanks(request):
    return render(request, "public/thanks.html")
