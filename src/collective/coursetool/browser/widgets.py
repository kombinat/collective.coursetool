from collective.z3cform.datagridfield.datagridfield import DataGridFieldObjectWidget
from collective.z3cform.datagridfield.datagridfield import DataGridFieldWidget
from z3c.form import interfaces
from z3c.form.interfaces import IFormLayer
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer
from zope.schema.interfaces import IField


class CourseOccurrencesWidget(DataGridFieldWidget):
    """override template for course.occurrences"""

    def createObjectWidget(self, idx):
        valueType = self.field.value_type
        widget = CourseOccurrencesObjectWidgetFactory(valueType, self.request)
        widget.setErrors = idx not in ["TT", "AA"]
        return widget


@adapter(IField, IFormLayer)
@implementer(interfaces.IFieldWidget)
def CourseOccurrencesFieldWidget(field, request):
    return FieldWidget(field, CourseOccurrencesWidget(request))


class CourseOccurrencesObjectWidget(DataGridFieldObjectWidget):
    """override template for row in course.occurrence"""


@adapter(IField, interfaces.IFormLayer)
@implementer(interfaces.IFieldWidget)
def CourseOccurrencesObjectWidgetFactory(field, request):
    return FieldWidget(field, CourseOccurrencesObjectWidget(request))
