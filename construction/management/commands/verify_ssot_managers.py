from django.core.management.base import BaseCommand
from django.db.models import Sum, Q, Count
from construction import models


class Command(BaseCommand):
    help = "Verify SSOT managers for Expense and Sale against legacy aggregates on REAL database"

    def handle(self, *args, **options):
        project = models.Project.get_active_project() or models.Project.objects.first()
        if not project:
            self.stdout.write(self.style.WARNING("No project found."))
            return

        self.stdout.write(self.style.SUCCESS(f"Active/First project: {project.name} (id={project.id})"))

        errors = 0

        # Project totals (Expense/Sale)
        exp_mgr = models.Expense.objects.project_totals(project)
        exp_agg = float(models.Expense.objects.filter(project=project).aggregate(total=Sum('amount'))['total'] or 0)
        if round(exp_mgr, 6) != round(exp_agg, 6):
            errors += 1
            self.stdout.write(self.style.ERROR(f"Expense project_totals mismatch: manager={exp_mgr} agg={exp_agg}"))

        sale_mgr = models.Sale.objects.project_totals(project)
        sale_agg = float(models.Sale.objects.filter(project=project).aggregate(total=Sum('amount'))['total'] or 0)
        if round(sale_mgr, 6) != round(sale_agg, 6):
            errors += 1
            self.stdout.write(self.style.ERROR(f"Sale project_totals mismatch: manager={sale_mgr} agg={sale_agg}"))

        # Project totals (Transactions)
        tx_mgr = models.Transaction.objects.project_totals(project)
        tx_qs = models.Transaction.objects.filter(project=project)
        tx_deposits = float(tx_qs.aggregate(total=Sum('amount', filter=Q(transaction_type__in=['principal_deposit','loan_deposit'])))['total'] or 0)
        tx_withdrawals = float(tx_qs.aggregate(total=Sum('amount', filter=Q(transaction_type='principal_withdrawal')))['total'] or 0)
        tx_profits = float(tx_qs.aggregate(total=Sum('amount', filter=Q(transaction_type='profit_accrual')))['total'] or 0)
        if not (
            round(tx_mgr['deposits'],6) == round(tx_deposits,6) and
            round(tx_mgr['withdrawals'],6) == round(tx_withdrawals,6) and
            round(tx_mgr['profits'],6) == round(tx_profits,6) and
            round(tx_mgr['net_capital'],6) == round(tx_deposits + tx_withdrawals,6)
        ):
            errors += 1
            self.stdout.write(self.style.ERROR(
                f"Transaction project_totals mismatch: mgr={tx_mgr} agg={{'deposits':{tx_deposits},'withdrawals':{tx_withdrawals},'profits':{tx_profits}}}"
            ))

        # Per-period checks (first 12 periods to keep it fast)
        periods = models.Period.objects.filter(project=project).order_by('year', 'month_number')[:12]
        for period in periods:
            # Expense period
            e_mgr = models.Expense.objects.period_totals(project, period)
            e_agg = float(models.Expense.objects.filter(project=project, period=period).aggregate(total=Sum('amount'))['total'] or 0)
            if round(e_mgr, 6) != round(e_agg, 6):
                errors += 1
                self.stdout.write(self.style.ERROR(f"Expense period_totals mismatch @ {period.label}: manager={e_mgr} agg={e_agg}"))

            # Sale period
            s_mgr = models.Sale.objects.period_totals(project, period)
            s_agg = float(models.Sale.objects.filter(project=project, period=period).aggregate(total=Sum('amount'))['total'] or 0)
            if round(s_mgr, 6) != round(s_agg, 6):
                errors += 1
                self.stdout.write(self.style.ERROR(f"Sale period_totals mismatch @ {period.label}: manager={s_mgr} agg={s_agg}"))

            # Expense cumulative
            e_cum_mgr = models.Expense.objects.cumulative_until(project, period)
            e_cum_qs = models.Expense.objects.filter(project=project).filter(
                Q(period__year__lt=period.year) | Q(period__year=period.year, period__month_number__lte=period.month_number)
            )
            e_cum_agg = float(e_cum_qs.aggregate(total=Sum('amount'))['total'] or 0)
            if round(e_cum_mgr, 6) != round(e_cum_agg, 6):
                errors += 1
                self.stdout.write(self.style.ERROR(f"Expense cumulative_until mismatch @ {period.label}: manager={e_cum_mgr} agg={e_cum_agg}"))

            # Sale cumulative
            s_cum_mgr = models.Sale.objects.cumulative_until(project, period)
            s_cum_qs = models.Sale.objects.filter(project=project).filter(
                Q(period__year__lt=period.year) | Q(period__year=period.year, period__month_number__lte=period.month_number)
            )
            s_cum_agg = float(s_cum_qs.aggregate(total=Sum('amount'))['total'] or 0)
            if round(s_cum_mgr, 6) != round(s_cum_agg, 6):
                errors += 1
                self.stdout.write(self.style.ERROR(f"Sale cumulative_until mismatch @ {period.label}: manager={s_cum_mgr} agg={s_cum_agg}"))

            # Transactions period
            tx_mgr_period = models.Transaction.objects.period_totals(project, period)
            tx_qs_p = models.Transaction.objects.filter(project=project, period=period)
            tx_dep_p = float(tx_qs_p.aggregate(total=Sum('amount', filter=Q(transaction_type__in=['principal_deposit','loan_deposit'])))['total'] or 0)
            tx_wd_p = float(tx_qs_p.aggregate(total=Sum('amount', filter=Q(transaction_type='principal_withdrawal')))['total'] or 0)
            tx_pf_p = float(tx_qs_p.aggregate(total=Sum('amount', filter=Q(transaction_type='profit_accrual')))['total'] or 0)
            if not (
                round(tx_mgr_period['deposits'],6) == round(tx_dep_p,6) and
                round(tx_mgr_period['withdrawals'],6) == round(tx_wd_p,6) and
                round(tx_mgr_period['profits'],6) == round(tx_pf_p,6) and
                round(tx_mgr_period['net_capital'],6) == round(tx_dep_p + tx_wd_p,6)
            ):
                errors += 1
                self.stdout.write(self.style.ERROR(
                    f"Transaction period_totals mismatch @ {period.label}: mgr={tx_mgr_period} agg={{'deposits':{tx_dep_p},'withdrawals':{tx_wd_p},'profits':{tx_pf_p}}}"
                ))

        if errors == 0:
            self.stdout.write(self.style.SUCCESS("SSOT verification passed. Managers match legacy aggregates."))
        else:
            self.stdout.write(self.style.ERROR(f"SSOT verification found {errors} mismatches."))

        # Units stats check
        unit_mgr = models.Unit.objects.project_stats(project)
        u_qs = models.Unit.objects.filter(project=project).aggregate(
            total_units=Count('id'),
            total_area=Sum('area'),
            total_price=Sum('total_price')
        )
        u_ok = (
            unit_mgr['total_units'] == (u_qs['total_units'] or 0) and
            round(unit_mgr['total_area'], 6) == round(float(u_qs['total_area'] or 0), 6) and
            round(unit_mgr['total_price'], 6) == round(float(u_qs['total_price'] or 0), 6)
        )
        if u_ok:
            self.stdout.write(self.style.SUCCESS("Unit manager stats match aggregates."))
        else:
            self.stdout.write(self.style.ERROR(f"Unit manager stats mismatch: mgr={unit_mgr} agg={u_qs}"))

        # Investor checks (first 5)
        investors = models.Investor.objects.filter(project=project)[:5]
        for inv in investors:
            t = models.Transaction.objects.totals(project, {'investor_id': inv.id})
            qs = models.Transaction.objects.filter(project=project, investor=inv)
            dep = float(qs.aggregate(total=Sum('amount', filter=Q(transaction_type__in=['principal_deposit','loan_deposit'])))['total'] or 0)
            wd = float(qs.aggregate(total=Sum('amount', filter=Q(transaction_type='principal_withdrawal')))['total'] or 0)
            pf = float(qs.aggregate(total=Sum('amount', filter=Q(transaction_type='profit_accrual')))['total'] or 0)
            ok = (
                round(t.get('deposits', 0),6) == round(dep,6) and
                round(t.get('withdrawals', 0),6) == round(wd,6) and
                round(t.get('profits', 0),6) == round(pf,6) and
                round(t.get('net_capital', 0),6) == round(dep + wd,6)
            )
            if ok:
                self.stdout.write(self.style.SUCCESS(f"Investor #{inv.id} totals match."))
            else:
                self.stdout.write(self.style.ERROR(f"Investor #{inv.id} mismatch: mgr={t} dep={dep} wd={wd} pf={pf}"))

