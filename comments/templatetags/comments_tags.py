from django import template

register = template.Library()

#comment
    # template filter za filtriranje queryseta: u context-u imam Queryset Comment objekata naziva 'replies' i
    # integer 'comment_id'. Sada želim filtrirati 'replies' u template-u, da dobijem novi Queryset koji će sadržavati
    # Comment objekte čiji je parent_id field jednak comment_id-u iz konteksta. Primjer korištenja:
    #       {% for reply in replies|for_comment:comment_id %} 
    # Dakle, 'for_comment' je naziv filter funkcije, 'replies' je prvi argument, 'comment_id' drugi - možemo čitati
    # "replies comment objekta čiji je id jednak comment_id-u". Važno je 'replies|for_comment:comment_id' napisati
    # bez razmaka jer django to onda interpretira kao jednu cijelinu, što je potrebno. Na kraju ovaj template filter
    # nisam koristio.
@register.filter
def for_comment(replies, comment_id):
    return replies.filter(parent_id=comment_id)