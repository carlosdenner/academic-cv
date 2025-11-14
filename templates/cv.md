# Carlos Denner dos Santos — Curriculum Vitae

## Publications
{% for name,works in sections.items() if works -%}
### {{ name }}
{% for w in works -%}
- {{ w.title }}{% if w.venue %}. *{{ w.venue }}*{% endif %}{% if w.year %} ({{ w.year }}){% endif %}{% if w.doi %}. DOI: {{ w.doi }}{% endif %}{% if w.url %} [link]({{ w.url }}){% endif %}
{% endfor %}
{% endfor %}
