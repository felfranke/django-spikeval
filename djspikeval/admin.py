# -*- coding: utf-8 -*-

from django.apps import apps
from django.contrib import admin

__author__ = "pmeier82"

Algorithm = apps.get_registered_model("djspikeval", "algorithm")
Batch = apps.get_registered_model("djspikeval", "batch")
Benchmark = apps.get_registered_model("djspikeval", "benchmark")
Evaluation = apps.get_registered_model("djspikeval", "evaluation")
Trial = apps.get_registered_model("djspikeval", "trial")


class AlgorithmAdmin(admin.ModelAdmin):
    pass


class BatchAdmin(admin.ModelAdmin):
    pass


class BenchmarkAdmin(admin.ModelAdmin):
    pass


class EvaluationAdmin(admin.ModelAdmin):
    pass


class TrialAdmin(admin.ModelAdmin):
    pass


admin.site.register(Algorithm, AlgorithmAdmin)
admin.site.register(Batch, BatchAdmin)
admin.site.register(Benchmark, BenchmarkAdmin)
admin.site.register(Evaluation, EvaluationAdmin)
admin.site.register(Trial, TrialAdmin)

if __name__ == "__main__":
    pass
