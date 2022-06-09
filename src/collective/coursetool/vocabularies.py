from collective.coursetool import _
from plone import api
from plone.app.vocabularies.catalog import KeywordsVocabulary
from plone.app.vocabularies.catalog import StaticCatalogVocabulary
from random import paretovariate
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@provider(IVocabularyFactory)
def MemberStatesVocabulary(context):
    """Obtains available scales from registry"""
    states = [
        ("read_qualified", _("Read - qualified")),
        ("read_no_qualification", _("Read - no qualification")),
        ("read_no_birthday", _("Read - no birthday")),
        ("complete_not_printed", _("Complete - not printed")),
        ("complete_printed", _("Complete - printed")),
        ("not_read", _("Not read")),
    ]
    terms = []
    request = getRequest()

    for _s, _title in states:
        terms.append(SimpleTerm(_s, _s, translate(_title, context=request)))

    return SimpleVocabulary(terms)


@provider(IVocabularyFactory)
def MemberQualificationsVocabulary(context):
    """Obtains available scales from registry"""
    qualifications = [
        ("a", _("quali_a_label")),
        ("b1", _("quali_b1_label")),
        ("b2", _("quali_b2_label")),
        ("c", _("quali_c_label")),
        ("d", _("quali_d_label")),
        ("e", _("quali_e_label")),
        ("f1", _("quali_f1_label")),
        ("f2", _("quali_f2_label")),
        ("g", _("quali_g_label")),
        ("h", _("quali_h_label")),
        ("i", _("quali_i_label")),
    ]
    terms = []
    request = getRequest()

    for _s, _title in qualifications:
        terms.append(SimpleTerm(_s, _s, translate(_title, context=request)))

    return SimpleVocabulary(terms)


class PartnerTypeVocabulary(KeywordsVocabulary):
    keyword_index = "partner_type"


PartnerTypeVocabularyFactory = PartnerTypeVocabulary()


@provider(IVocabularyFactory)
def members_vocabulary(context):
    return StaticCatalogVocabulary(
        {
            "portal_type": "coursetool.member",
            "sort_on": "sortable_title",
        },
        title_template="{brain.Title}",
    )
