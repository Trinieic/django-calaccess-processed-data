#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Models for storing data from Campaign Disclosure Statements (Form 460).
"""
from __future__ import unicode_literals
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from calaccess_processed.managers import ProcessedDataManager
from calaccess_processed.models.campaign.filings import CampaignExpenditureSubItemBase


class Form460ScheduleGItemBase(CampaignExpenditureSubItemBase):
    """
    Abstract base model for items reported on Schedule G of Form 460 filings.

    On Schedule G, campaign filers are required to itemize payments made on
    their behalf by agents or contractors during the period covered by the
    filing.
    """
    agent_title = models.CharField(
        verbose_name='agent title',
        max_length=10,
        blank=True,
        help_text='Name title of the agent (from EXPN_CD.AGENT_NAMT)',
    )
    agent_lastname = models.CharField(
        verbose_name='agent lastname',
        max_length=200,
        blank=True,
        help_text='Last name of the agent or business name (from '
                  'EXPN_CD.AGENT_NAML)',
    )
    agent_firstname = models.CharField(
        verbose_name='agent firstname',
        max_length=45,
        help_text='First name of the agent (from EXPN_CD.AGENT_NAMF)',
    )
    agent_name_suffix = models.CharField(
        verbose_name='agent name suffix',
        max_length=10,
        blank=True,
        help_text='Name suffix of the agent (from EXPN_CD.AGENT_NAMS)',
    )
    PARENT_SCHEDULE_CHOICES = (
        ('E', 'Schedule E: Payments Made'),
        ('F', 'Schedule F: Accrued Expenses (Unpaid Bills)')
    )
    parent_schedule = models.CharField(
        max_length=1,
        blank=True,
        help_text="Indicates which schedule (E or F) includes the parent item "
                  "(from EXPN_CD.G_FROM_E_F)",
    )

    class Meta:
        """
        Model options.
        """
        abstract = True


@python_2_unicode_compatible
class Form460ScheduleGItem(Form460ScheduleGItemBase):
    """
    Payments made by on behalf of campaign filers.

    These transactions are itemized on Schedule G of the most recent version
    of each Form 460 filing. For payments itemized on any version of any Form
    460 filing, see Form460schedulegitemversion.

    Derived from EXPN_CD records where FORM_TYPE is 'G'.
    """
    filing = models.ForeignKey(
        'Form460Filing',
        related_name='schedule_g_items',
        null=True,
        on_delete=models.SET_NULL,
        help_text='Foreign key referring to the Form 460 on which the '
                  'payment was reported (from RCPT_CD.FILING_ID)',
    )

    objects = ProcessedDataManager()

    class Meta:
        """
        Model options.
        """
        unique_together = ((
            'filing',
            'line_item',
        ),)

    def __str__(self):
        return '%s-%s' % (self.filing, self.line_item)


@python_2_unicode_compatible
class Form460ScheduleGItemVersion(Form460ScheduleGItemBase):
    """
    Every version of each payment made on behalf of a campaign filer.

    For payments itemized on Schedule G of the most recent version of each Form
    460 filing, see Form460ScheduleGitem.

    Derived from EXPN_CD records where FORM_TYPE is 'G'.
    """
    filing_version = models.ForeignKey(
        'Form460FilingVersion',
        related_name='schedule_g_items',
        null=True,
        on_delete=models.SET_NULL,
        help_text='Foreign key referring to the version of the Form 460 that '
                  'includes the payment made'
    )

    objects = ProcessedDataManager()

    class Meta:
        """
        Model options.
        """
        unique_together = ((
            'filing_version',
            'line_item',
        ),)
        index_together = ((
            'filing_version',
            'line_item',
        ),)

    def __str__(self):
        return '%s-%s-%s' % (
            self.filing_version.filing_id,
            self.filing_version.amend_id,
            self.line_item
        )
