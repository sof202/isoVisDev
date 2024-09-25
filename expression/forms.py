from django import forms

class GeneForm(forms.Form):
    """Form for gene name input."""
    gene_name = forms.CharField(label="Gene Name", max_length=100)

class TheForm(forms.Form):
    """Form for transferring user selection"""

    Transcripts = forms.MultipleChoiceField(
        choices=[],  # Choices will be populated dynamically
        widget=forms.SelectMultiple,  # Or SelectMultiple for a dropdown
    )

    def __init__(self, *args, **kwargs):
        """Initialize the form and set dynamic choices"""
        super().__init__(*args, **kwargs)
        if 'choices' in kwargs.get('initial', {}):
            self.fields['Transcripts'].choices = kwargs['initial']['choices']
