# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import simplejson
import zipfile
from StringIO import StringIO

from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.defaultfilters import slugify
from django.utils import importlib
from django.views.generic import (
    View, DetailView, UpdateView, DeleteView, CreateView, ListView, RedirectView)
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from numpy import nan, nansum, nanmax

from ..forms import DatasetForm
# from ..util import render_to, PLOT_COLORS

__all__ = [
    "ModuleBaseView", "ModuleList", "ModuleCreate", "ModuleDetail",
    "ModuleUpdate", "ModuleDelete", "ModuleDownload", "ModuleSummary",
    "ModuleToggle"]
__author__ = "pmeier82"

Dataset = apps.get_registered_model("djspikeval", "dataset")
Module = apps.get_registered_model("djspikeval", "module")


class ModuleBaseView(object):
    model = Module


class ModuleList(ModuleBaseView, ListView):
    template_name = "djspikeval/module/list.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        cntx = super(ModuleList, self).get_context_data(**kwargs)
        cntx.update(scope=self.request.GET.get("scope"))
        return cntx

    def get_queryset(self):
        # TODO: adjust filter for query set
        rval = Module.objects.all()
        if not self.request.user.is_superuser:
            rval = rval.filter(
                Q(status=Dataset.STATUS.public) |
                Q(user__pk=self.request.user.pk)
            )
        if self.request.GET.get("scope"):
            rval = (
                rval.filter(name__icontains=self.request.GET.get("scope")) |
                rval.filter(kind__name__icontains=self.request.GET.get("scope")))
        return rval.distinct()


class ModuleCreate(ModuleBaseView, CreateView):
    template_name = "djspikeval/module/create.html"
    form_class = ModuleForm

    def get_form_kwargs(self):
        kwargs = super(ModuleCreate, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class ModuleDetail(ModuleBaseView, DetailView):
    template_name = "djspikeval/dataset/detail.html"


class ModuleUpdate(ModuleBaseView, UpdateView):
    template_name = "djspikeval/dataset/update.html"
    form_class = DatasetForm

    def get_form_kwargs(self):
        kwargs = super(ModuleUpdate, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class ModuleDelete(ModuleBaseView, DeleteView):
    template_name = "djspikeval/dataset/delete.html"
    success_url = reverse_lazy("dataset:list")


class ModuleDownload(ModuleBaseView, View):
    """serve dataset as archive"""

    def get(self, request, *args, **kwargs):
        try:
            obj = get_object_or_404(Dataset, pk=self.kwargs["pk"])
            assert obj.is_accessible(request.user), "insufficient permissions"
        except Exception, ex:
            messages.error(request, "You are not allowed to view or modify this Dataset: %s" % ex)
            return redirect("dataset:list")
        df_list = [df for df in obj.datafile_set.order_by("parameter") if df.is_valid]
        arc, buf = None, None

        # build archive
        try:
            # build buffer and archive
            buf = StringIO()
            arc = zipfile.ZipFile(buf, mode="w")
            for df in df_list:
                arc.writestr(df.rd_file.name, df.rd_file.data.read())
                if df.gt_file and df.gt_public:
                    arc.writestr(df.gt_file.name, df.gt_file.data.read())
            arc.close()
            buf.seek(0)

            response = HttpResponse(buf.read())
            response["Content-Disposition"] = "attachment; filename=%s.zip" % slugify(obj.name)
            response["Content-Type"] = "application/x-zip"
            return response
        except Exception, ex:
            messages.error(request, "Error creating archive: %s" % ex)
            return redirect(obj)
        finally:
            try:
                del arc
            except:
                pass
            try:
                del buf
            except:
                pass


class ModuleSummary(ModuleBaseView, View):
    """summary for this dataset"""

    def get(self, request, *args, **kwargs):
        return HttpResponse("TEST")


class ModuleToggle(ModuleBaseView, View):
    """toggle dataset visibility"""

    def get(self, request, *args, **kwargs):
        try:
            obj = get_object_or_404(Dataset, pk=self.kwargs["pk"])
            assert obj.is_accessible(self.request.user), "insufficient permissions"
            obj.toggle()
            messages.info(self.request, "Dataset \"%s\" toggled to %s" % (obj, obj.status))
        except Exception, ex:
            messages.error(self.request, "Dataset not toggled: %s" % ex)
        finally:
            return redirect(obj)


if __name__ == "__main__":
    pass
