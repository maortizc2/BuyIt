from django import template
import markdown

register = template.Library()

@register.filter(name='markdownify')
def markdownify(text):
    return markdown.markdown(text, extensions=['fenced_code', 'codehilite'])
