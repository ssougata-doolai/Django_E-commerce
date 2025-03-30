from django import forms

Quantity = (
    ('1','1'),
    ('2','2'),
    ('3','3'),
    ('4','4'),
)

class ChooseQuantity(forms.Form):
    qty = forms.ChoiceField(choices = Quantity, initial='1')
