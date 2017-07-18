#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Proxy models for augmenting our source data tables with methods useful for processing.
"""
from django.db import models
from opencivicdata.core.models import Organization
from calaccess_raw.models import FilerToFilerTypeCd


class OCDPartyManager(models.Manager):
    """
    Limited the OCD Organization model to politics parties.
    """
    def get_queryset(self):
        """
        Override the default manager to limit the results to political parties.
        """
        return super(OCDPartyManager, self).get_queryset().filter(classification='party')

    def get_by_name(self, name):
        """
        Helper for getting the OCD party object giving a raw name from CAL-ACCESS.

        If not found, return the "UNKNOWN" Organization object.
        """
        # First try a full name
        try:
            return self.get_queryset().get(name=name)
        except self.model.DoesNotExist:
            pass

        # If that doesn't work, try an alternate name
        try:
            return self.get_queryset().get(other_names__name=name)
        except self.model.DoesNotExist:
            pass

        # And if that doesn't work, just return the unknown party object
        return self.get_queryset().get(name='UNKNOWN')

    def get_by_filer_id(self, filer_id, election_date):
        """
        Lookup the party for the given filer_id, effective before election_date.

        If not found, return the "UNKNOWN" Organization object.
        """
        # Try to see if the record exists in the raw data with a party code
        try:
            party_code = FilerToFilerTypeCd.objects.filter(
                filer_id=filer_id,
                effect_dt__lte=election_date,
            ).latest('effect_dt').party_cd
        except FilerToFilerTypeCd.DoesNotExist:
            # If it doesn't hit just quit now
            return self.get_queryset().get(name='UNKNOWN')

        # IF we have a code, transform "INDEPENDENT" and "NON-PARTISAN" codes to "NO PARTY PREFERENCE"
        if party_code in [16007, 16009]:
            party_code = 16012

        # Try pulling out the party using the lookup code
        try:
            return self.get_queryset().get(identifiers__identifier=party_code)
        except self.model.DoesNotExist:
            pass

        # If that fails, just quit and return the unknown party object
        return self.get_queryset().get(name='UNKNOWN')


class OCDPartyProxy(Organization):
    """
    A proxy on the OCD Organization model with helper methods for interacting with party entities.
    """
    objects = OCDPartyManager()

    class Meta:
        """
        Make this a proxy model.
        """
        proxy = True

    def is_unknown(self):
        """
        Returns whether or not the provided party is unknown.
        """
        return self.name == 'UNKNOWN'