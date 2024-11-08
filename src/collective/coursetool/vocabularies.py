from collective.coursetool import _
from plone.app.vocabularies.catalog import KeywordsVocabulary
from plone.app.vocabularies.catalog import StaticCatalogVocabulary
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class StaticValuesVocabulary:
    values = []

    def __call__(self, context=None):
        terms = []
        request = getRequest()

        for _s, _title in self.values:
            terms.append(SimpleTerm(_s, _s, translate(_title, context=request)))

        return SimpleVocabulary(terms)


class MemberStatesVocabulary(StaticValuesVocabulary):
    values = [
        ("read_qualified", _("Read - qualified")),
        ("read_no_qualification", _("Read - no qualification")),
        ("read_no_birthday", _("Read - no birthday")),
        ("complete_not_printed", _("Complete - not printed")),
        ("complete_printed", _("Complete - printed")),
        ("not_read", _("Not read")),
    ]


MemberStatesVocabularyFactory = MemberStatesVocabulary()


class MemberQualificationsVocabulary(StaticValuesVocabulary):
    values = [
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


MemberQualificationsVocabularyFactory = MemberQualificationsVocabulary()


class ExamTypesVocabulary(StaticValuesVocabulary):
    values = [
        ("abs_1_lit_a", _("Abs. 1 lit. a: Vorarlberger Fischerprüfung")),
        (
            "abs_1_lit_b",
            _(
                "Abs. 1 lit. b: Erfolgreich abgelegte Prüfung in anderen Bundesländern oder Staaten"
            ),
        ),
        (
            "abs_1_lit_c",
            _(
                "Abs. 1 lit. c: Erfolgreicher Abschluss der Fischereifacharbeiterprüfung"
            ),
        ),
        (
            "abs_1_lit_d",
            _("Abs. 1 lit. d: Gleichwertig zur Fischerprüfung anerkannte Ausbildung"),
        ),
        ("abs_1_lit_e", _("Abs. 1 lit. e: Erfolgreich abgelegte Eignungsprüfung")),
        ("abs_2", _("Abs. 2: Teilnahme an einer Unterweisung")),
    ]


ExamTypesVocabularyFactory = ExamTypesVocabulary()


class CourseTypesVocabulary(StaticValuesVocabulary):
    values = [
        ("offline", _("course_type_offline")),
        ("online", _("course_type_online")),
    ]


CourseTypesVocabularyFactory = CourseTypesVocabulary()


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
