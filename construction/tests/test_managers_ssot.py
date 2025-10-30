from django.test import TestCase
from django.db.models import Sum
from construction import models


class SSOTManagersTests(TestCase):
    def test_expense_manager_matches_aggregates(self):
        project = models.Project.get_active_project() or models.Project.objects.first()

        mgr_total = models.Expense.objects.project_totals(project)
        qs = models.Expense.objects.all()
        if project:
            qs = qs.filter(project=project)
        agg_total = float(qs.aggregate(total=Sum('amount'))['total'] or 0)
        self.assertEqual(mgr_total, agg_total)

        totals = models.Expense.objects.totals(project, {})
        self.assertEqual(totals['total_expenses'], agg_total)

    def test_sale_manager_matches_aggregates(self):
        project = models.Project.get_active_project() or models.Project.objects.first()

        mgr_total = models.Sale.objects.project_totals(project)
        qs = models.Sale.objects.all()
        if project:
            qs = qs.filter(project=project)
        agg_total = float(qs.aggregate(total=Sum('amount'))['total'] or 0)
        self.assertEqual(mgr_total, agg_total)

        totals = models.Sale.objects.totals(project, {})
        self.assertEqual(totals['total_sales'], agg_total)

    def test_unit_manager_matches_aggregates(self):
        project = models.Project.get_active_project() or models.Project.objects.first()
        stats = models.Unit.objects.project_stats(project)
        qs = models.Unit.objects.all()
        if project:
            qs = qs.filter(project=project)
        agg = qs.aggregate(total_area=Sum('area'), total_price=Sum('total_price'))
        self.assertEqual(stats['total_area'], float(agg['total_area'] or 0))
        self.assertEqual(stats['total_price'], float(agg['total_price'] or 0))

    def test_expense_period_and_cumulative_match(self):
        project = models.Project.get_active_project() or models.Project.objects.first()
        period = models.Period.objects.filter(project=project).order_by('year', 'month_number').first()
        if not period:
            self.skipTest('No period found for project')

        # period_totals
        mgr_period = models.Expense.objects.period_totals(project, period)
        qs_period = models.Expense.objects.filter(project=project, period=period)
        agg_period = float(qs_period.aggregate(total=Sum('amount'))['total'] or 0)
        self.assertEqual(mgr_period, agg_period)

        # cumulative_until
        mgr_cum = models.Expense.objects.cumulative_until(project, period)
        qs_cum = models.Expense.objects.filter(project=project).filter(
            models.Q(period__year__lt=period.year) |
            models.Q(period__year=period.year, period__month_number__lte=period.month_number)
        )
        agg_cum = float(qs_cum.aggregate(total=Sum('amount'))['total'] or 0)
        self.assertEqual(mgr_cum, agg_cum)

    def test_sale_period_and_cumulative_match(self):
        project = models.Project.get_active_project() or models.Project.objects.first()
        period = models.Period.objects.filter(project=project).order_by('year', 'month_number').first()
        if not period:
            self.skipTest('No period found for project')

        # period_totals
        mgr_period = models.Sale.objects.period_totals(project, period)
        qs_period = models.Sale.objects.filter(project=project, period=period)
        agg_period = float(qs_period.aggregate(total=Sum('amount'))['total'] or 0)
        self.assertEqual(mgr_period, agg_period)

        # cumulative_until
        mgr_cum = models.Sale.objects.cumulative_until(project, period)
        qs_cum = models.Sale.objects.filter(project=project).filter(
            models.Q(period__year__lt=period.year) |
            models.Q(period__year=period.year, period__month_number__lte=period.month_number)
        )
        agg_cum = float(qs_cum.aggregate(total=Sum('amount'))['total'] or 0)
        self.assertEqual(mgr_cum, agg_cum)


